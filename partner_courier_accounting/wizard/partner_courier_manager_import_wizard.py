import base64
import re
from io import BytesIO
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PartnerCourierManagerImportWizard(models.TransientModel):
    _name = 'partner.courier.manager.import.wizard'
    _description = 'Kurye Yönetici İçe Aktarma Sihirbazı'

    file = fields.Binary(string='Excel Dosyası', required=True)
    filename = fields.Char(string='Dosya Adı')
    state = fields.Selection(
        [('upload', 'Dosya Yükle'), ('review', 'Doğrulama'), ('done', 'Tamamlandı')],
        default='upload',
        required=True,
    )
    line_ids = fields.One2many(
        'partner.courier.manager.import.wizard.line',
        'wizard_id',
        string='Doğrulama Satırları',
    )
    ready_line_count = fields.Integer(compute='_compute_line_counts')
    issue_line_count = fields.Integer(compute='_compute_line_counts')

    @api.depends('line_ids.state')
    def _compute_line_counts(self):
        for wizard in self:
            wizard.ready_line_count = len(wizard.line_ids.filtered(lambda line: line.state == 'ready'))
            wizard.issue_line_count = len(wizard.line_ids.filtered(lambda line: line.state == 'error'))

    def action_validate_file(self):
        self.ensure_one()
        rows = self._read_xlsx_rows()
        if not rows:
            raise UserError(_('Excel dosyasında okunabilir satır bulunamadı.'))

        header_map = self._get_header_map(rows[0])
        self.line_ids.unlink()

        partner_model = self.env['res.partner']
        seen_courier_ids = set()
        line_values = []
        for row_number, row in enumerate(rows[1:], start=2):
            courier_id = self._to_text(self._cell(row, header_map['courier_id']))
            manager_name = self._to_text(self._cell(row, header_map['manager_name']))
            manager_phone = self._to_text(self._cell(row, header_map['manager_phone']))
            if not any((courier_id, manager_name, manager_phone)):
                continue

            values = {
                'row_number': row_number,
                'courier_id': courier_id,
                'manager_name': manager_name,
                'manager_phone': manager_phone,
                'state': 'error',
            }
            if not courier_id:
                values['error_message'] = _('Kurye ID boş bırakılamaz.')
            elif courier_id in seen_courier_ids:
                values['error_message'] = _('Bu Kurye ID Excel dosyasında birden fazla kez yer alıyor.')
            else:
                seen_courier_ids.add(courier_id)
                partners = partner_model.search([('courier_id', '=', courier_id)])
                if not partners:
                    values['error_message'] = _('Bu Kurye ID ile eşleşen kurye bulunamadı.')
                elif len(partners) > 1:
                    values['error_message'] = _('Bu Kurye ID birden fazla kişiyle eşleşiyor.')
                else:
                    partner = partners[0]
                    values.update({
                        'partner_id': partner.id,
                        'current_manager_name': partner.manager_name,
                        'current_manager_phone': partner.manager_phone,
                    })
                    if (
                        (partner.manager_name or '') == manager_name
                        and (partner.manager_phone or '') == manager_phone
                    ):
                        values.update({
                            'state': 'unchanged',
                            'error_message': _('Mevcut bilgilerle aynı, güncelleme gerekmiyor.'),
                        })
                    else:
                        values['state'] = 'ready'
            line_values.append((0, 0, values))

        if not line_values:
            raise UserError(_('Excel dosyasında işlenecek veri satırı bulunamadı.'))

        self.write({'line_ids': line_values, 'state': 'review'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_import(self):
        self.ensure_one()
        lines_to_update = self.line_ids.filtered(lambda line: line.state == 'ready')
        if not lines_to_update:
            raise UserError(_('İçe aktarılacak doğrulanmış satır bulunamadı.'))

        for line in lines_to_update:
            line.partner_id.write({
                'manager_name': line.manager_name,
                'manager_phone': line.manager_phone,
            })
            line.state = 'imported'

        self.state = 'done'
        skipped_count = len(self.line_ids) - len(lines_to_update)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Kurye Yönetici İçe Aktarma'),
                'message': _('%s kurye güncellendi. %s satır işleme alınmadı.') % (
                    len(lines_to_update),
                    skipped_count,
                ),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def action_back_to_upload(self):
        self.ensure_one()
        self.write({'state': 'upload', 'line_ids': [(5, 0, 0)]})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _get_header_map(self, header_row):
        field_by_header = {
            'kurye id': 'courier_id',
            'yönetici': 'manager_name',
            'yönetici telefonu': 'manager_phone',
        }
        header_map = {}
        for index, value in enumerate(header_row):
            field_name = field_by_header.get(self._normalize_header(value))
            if field_name:
                if field_name in header_map:
                    raise UserError(_('Excelde aynı başlık birden fazla kez yer alıyor: %s') % value)
                header_map[field_name] = index

        missing = [
            label for field_name, label in (
                ('courier_id', 'Kurye ID'),
                ('manager_name', 'Yönetici'),
                ('manager_phone', 'Yönetici Telefonu'),
            ) if field_name not in header_map
        ]
        if missing:
            raise UserError(_('Excelde eksik kolon var: %s') % ', '.join(missing))
        return header_map

    def _read_xlsx_rows(self):
        try:
            data = base64.b64decode(self.file)
            archive = ZipFile(BytesIO(data))
        except Exception as exc:
            raise UserError(_('Geçerli bir xlsx dosyası yükleyin.')) from exc

        namespaces = {
            'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
            'rel': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
        }
        archive_names = set(archive.namelist())
        if 'xl/workbook.xml' not in archive_names:
            raise UserError(_('Excel çalışma kitabı okunamadı.'))

        shared_strings = self._read_shared_strings(archive, archive_names, namespaces)
        sheet_path = self._get_first_sheet_path(archive, namespaces)
        root = ET.fromstring(archive.read(sheet_path))
        rows = []
        for row_node in root.findall('main:sheetData/main:row', namespaces):
            row = []
            for cell in row_node.findall('main:c', namespaces):
                index = self._column_index(cell.attrib.get('r', ''))
                while len(row) < index:
                    row.append('')
                row.append(self._cell_value(cell, shared_strings, namespaces))
            rows.append(row)
        return rows

    def _read_shared_strings(self, archive, archive_names, namespaces):
        if 'xl/sharedStrings.xml' not in archive_names:
            return []
        root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
        return [
            ''.join(text_node.text or '' for text_node in item.findall('.//main:t', namespaces))
            for item in root.findall('main:si', namespaces)
        ]

    def _get_first_sheet_path(self, archive, namespaces):
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        first_sheet = workbook.find('main:sheets/main:sheet', namespaces)
        if first_sheet is None:
            raise UserError(_('Excel sayfası bulunamadı.'))
        relationship_id = first_sheet.attrib.get('{%s}id' % namespaces['rel'])
        relationships = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        for relationship in relationships:
            if relationship.attrib.get('Id') == relationship_id:
                return 'xl/' + relationship.attrib.get('Target', '').lstrip('/')
        raise UserError(_('Excel sayfası okunamadı.'))

    def _cell_value(self, cell, shared_strings, namespaces):
        cell_type = cell.attrib.get('t')
        if cell_type == 'inlineStr':
            return ''.join(text_node.text or '' for text_node in cell.findall('.//main:t', namespaces))
        value_node = cell.find('main:v', namespaces)
        if value_node is None:
            return ''
        value = value_node.text or ''
        if cell_type == 's':
            return shared_strings[int(value)] if value.isdigit() and int(value) < len(shared_strings) else ''
        return value

    def _column_index(self, cell_reference):
        letters = re.sub(r'[^A-Z]', '', cell_reference.upper())
        index = 0
        for letter in letters:
            index = index * 26 + ord(letter) - 64
        return max(index - 1, 0)

    @staticmethod
    def _cell(row, index):
        return row[index] if index < len(row) else ''

    @staticmethod
    def _to_text(value):
        if value in (None, False):
            return ''
        text = str(value).strip()
        return text[:-2] if text.endswith('.0') else text

    def _normalize_header(self, value):
        return ' '.join(self._to_text(value).casefold().split())


class PartnerCourierManagerImportWizardLine(models.TransientModel):
    _name = 'partner.courier.manager.import.wizard.line'
    _description = 'Kurye Yönetici İçe Aktarma Doğrulama Satırı'
    _order = 'row_number'

    wizard_id = fields.Many2one(
        'partner.courier.manager.import.wizard',
        required=True,
        ondelete='cascade',
    )
    row_number = fields.Integer(string='Satır')
    courier_id = fields.Char(string='Kurye ID')
    partner_id = fields.Many2one('res.partner', string='Eşleşen Kurye')
    current_manager_name = fields.Char(string='Mevcut Yönetici')
    current_manager_phone = fields.Char(string='Mevcut Yönetici Telefonu')
    manager_name = fields.Char(string='Yeni Yönetici')
    manager_phone = fields.Char(string='Yeni Yönetici Telefonu')
    state = fields.Selection(
        [
            ('ready', 'Güncellenecek'),
            ('unchanged', 'Değişiklik Yok'),
            ('error', 'Hatalı'),
            ('imported', 'İçe Aktarıldı'),
        ],
        string='Durum',
        required=True,
    )
    error_message = fields.Char(string='Açıklama')

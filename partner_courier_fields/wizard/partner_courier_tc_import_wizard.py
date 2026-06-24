import base64
import re
from io import BytesIO
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from odoo import _, fields, models
from odoo.exceptions import UserError


class PartnerCourierTcImportWizard(models.TransientModel):
    _name = 'partner.courier.tc.import.wizard'
    _description = 'Kurye TC İçe Aktarma Sihirbazı'

    file = fields.Binary(string='Excel Dosyası', required=True)
    filename = fields.Char(string='Dosya Adı')

    def action_import(self):
        self.ensure_one()
        rows = self._read_xlsx_rows()
        if not rows:
            raise UserError(_('Excel dosyasında okunabilir satır bulunamadı.'))

        # Check for header row
        first_row = rows[0]
        val0 = self._to_text(self._cell(first_row, 0)).lower()
        val1 = self._to_text(self._cell(first_row, 1)).lower()
        is_header = any(keyword in val0 for keyword in ['kurye', 'id', 'tc', 't.c.']) or \
                    any(keyword in val1 for keyword in ['kurye', 'id', 'tc', 't.c.'])

        start_index = 1 if is_header else 0
        data_rows = rows[start_index:]

        partner_model = self.env['res.partner']
        updated_count = 0
        skipped_count = 0

        for row in data_rows:
            courier_id = self._to_text(self._cell(row, 0))
            courier_tc = self._to_text(self._cell(row, 1))

            if not courier_id:
                skipped_count += 1
                continue

            partners = partner_model.search([('courier_id', '=', courier_id)])
            if not partners:
                skipped_count += 1
                continue

            partners[0].write({'courier_tc': courier_tc})
            updated_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Kurye TC Import'),
                'message': _('%s kuryenin TC numarası güncellendi. %s satır atlandı.') % (updated_count, skipped_count),
                'type': 'success',
                'sticky': False,
            },
        }

    def _read_xlsx_rows(self):
        try:
            data = base64.b64decode(self.file)
            archive = ZipFile(BytesIO(data))
        except Exception as exc:
            raise UserError(_('Geçerli bir xlsx dosyası yükleyin.')) from exc

        ns = {
            'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
            'rel': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
        }
        names = set(archive.namelist())
        if 'xl/workbook.xml' not in names:
            raise UserError(_('Excel çalışma kitabı okunamadı.'))

        shared_strings = self._read_shared_strings(archive, names, ns)
        sheet_path = self._get_first_sheet_path(archive, ns)
        root = ET.fromstring(archive.read(sheet_path))
        rows = []
        for row_node in root.findall('main:sheetData/main:row', ns):
            row = []
            for cell in row_node.findall('main:c', ns):
                index = self._column_index(cell.attrib.get('r', ''))
                while len(row) < index:
                    row.append('')
                row.append(self._cell_value(cell, shared_strings, ns))
            rows.append(row)
        return rows

    def _read_shared_strings(self, archive, names, ns):
        if 'xl/sharedStrings.xml' not in names:
            return []
        root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
        return [''.join(t.text or '' for t in item.findall('.//main:t', ns)) for item in root.findall('main:si', ns)]

    def _get_first_sheet_path(self, archive, ns):
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        first_sheet = workbook.find('main:sheets/main:sheet', ns)
        if first_sheet is None:
            raise UserError(_('Excel sayfası bulunamadı.'))
        rel_id = first_sheet.attrib.get('{%s}id' % ns['rel'])
        rels = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
        for rel in rels:
            if rel.attrib.get('Id') == rel_id:
                target = rel.attrib.get('Target', '')
                return 'xl/' + target.lstrip('/')
        raise UserError(_('Excel sayfası okunamadı.'))

    def _cell_value(self, cell, shared_strings, ns):
        cell_type = cell.attrib.get('t')
        if cell_type == 'inlineStr':
            return ''.join(t.text or '' for t in cell.findall('.//main:t', ns))
        value_node = cell.find('main:v', ns)
        if value_node is None:
            return ''
        value = value_node.text or ''
        if cell_type == 's':
            return shared_strings[int(value)] if value.isdigit() and int(value) < len(shared_strings) else ''
        return value

    def _column_index(self, cell_ref):
        letters = re.sub(r'[^A-Z]', '', cell_ref.upper())
        index = 0
        for letter in letters:
            index = index * 26 + ord(letter) - 64
        return max(index - 1, 0)

    def _cell(self, row, index):
        return row[index] if index < len(row) else ''

    def _to_text(self, value):
        if value in (None, False):
            return ''
        text = str(value).strip()
        return text[:-2] if text.endswith('.0') else text

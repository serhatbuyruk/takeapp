import base64
import re
from io import BytesIO
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from odoo import _, fields, models
from odoo.exceptions import UserError


class PartnerCourierAccountingImportWizard(models.TransientModel):
    _name = 'partner.courier.accounting.import.wizard'
    _description = 'Partner Courier Accounting Import Wizard'

    file = fields.Binary(string='Excel Dosyası', required=True)
    filename = fields.Char(string='Dosya Adı')
    date_start = fields.Date(string='Hafta Başlangıç', required=True)
    date_end = fields.Date(string='Hafta Bitiş', required=True)

    _HEADER_FIELD_MAP = {
        'Bölge': ('area', 'char'),
        'Şehir': ('city', 'char'),
        'Pick up': ('pickup_count', 'int'),
        'Drop off': ('dropoff_count', 'int'),
        'Google Distance Pick Up': ('google_distance_pickup_amount', 'float'),
        'Google Distance Drop Off': ('google_distance_dropoff_amount', 'float'),
        'Pick up Tutar': ('pickup_amount', 'float'),
        'Drop off Tutar': ('dropoff_amount', 'float'),
        'Kilometre Başı Mesafe Tutarı': ('distance_amount', 'float'),
        'Garanti Bölge Tutarı': ('guarantee_region_amount', 'float'),
        'Gece Mesaisi Tutarı': ('night_shift_amount', 'float'),
        'Bölge Kampanya Tutarı': ('region_campaign_amount', 'float'),
        'Haftalık Ek Paket Tutarı': ('weekly_extra_package_amount', 'float'),
        'Günlük Bonus': ('daily_bonus_amount', 'float'),
        'Bahşiş Tutar (KDV Dahil)': ('tip_amount_tax_included', 'float'),
        'Bahşiş Tutar (KDV Hariç)': ('tip_amount_tax_excluded', 'float'),
        'Hak Ediş Tutarı (KDV Hariç)': ('earning_amount_tax_excluded', 'float'),
        'Toplam Ödeme (KDV Hariç)': ('total_payment_tax_excluded', 'float'),
        "Kuryetec Bonus'u (KDV Hariç)": ('kuryetec_bonus_tax_excluded', 'float'),
        'Bonus Dahil Toplam Ödeme (KDV Hariç)': ('bonus_included_total_payment_tax_excluded', 'float'),
        'Bonus Dahil Hak Ediş (KDV Dahil)': ('bonus_included_earning_tax_included', 'float'),
        'Cash Kesinti Tutarı (KDV Dahil)': ('cash_deduction_tax_included', 'float'),
        'SoftPos Kesinti Tutarı (KDV Dahil)': ('softpos_deduction_tax_included', 'float'),
        'Sigorta Kesintisi': ('insurance_deduction_amount', 'float'),
        'Saha Kesintisi (Sipariş)': ('field_deduction_order_amount', 'float'),
        'İXOPAY (Nakit Yatırılan Tutar)': ('ixopay_cash_deposit_amount', 'float'),
        'Son Kesinti (Yemek Sepeti)': ('final_deduction_yemeksepeti_amount', 'float'),
        'Ekipman Alımı': ('equipment_purchase_amount', 'float'),
        'Toplam Kesinti': ('total_deduction_amount', 'float'),
        'Tevkifat Vergisi Tutarı': ('withholding_tax_amount', 'float'),
        'Avans': ('advance_amount', 'float'),
        'Yatırılan Ödeme': ('deposited_payment_amount', 'float'),
        'İSG Ödeme': ('isg_payment_amount', 'float'),
        'Sigorta': ('sgk_amount', 'float'),
        'Toplam Ödenecek Net Tutar (Kesintiler Düşürülmüştür)': ('net_payable_amount', 'float'),
        'Fatura Tipi': ('invoice_type', 'char'),
        'NOT': ('note', 'char'),
        'Yönetici': ('manager_name', 'char'),
    }
    _POSITION_FIELD_MAP = {
        'Son Kesinti (Yemek Sepeti)': [
            ('one_week_previous_negative_balance_amount', 'float'),
        ],
        'Toplam Kesinti': [
            ('two_week_previous_payment_deduction_amount', 'float'),
            ('one_week_previous_payment_deduction_amount', 'float'),
        ],
    }
    _REQUIRED_HEADERS = tuple(_HEADER_FIELD_MAP)

    def action_import(self):
        self.ensure_one()
        if self.date_start > self.date_end:
            raise UserError(_('Başlangıç tarihi bitiş tarihinden büyük olamaz.'))

        rows = self._read_xlsx_rows()
        if not rows:
            raise UserError(_('Excel dosyasında okunabilir satır bulunamadı.'))

        headers = [self._clean_header(value) for value in rows[0]]
        courier_id_index = self._find_header_index(headers, 'KURYE ID')
        if courier_id_index is None:
            raise UserError(_('KURYE ID kolonu bulunamadı.'))
        self._validate_required_headers(headers)

        column_map = {
            index: self._HEADER_FIELD_MAP[header]
            for index, header in enumerate(headers)
            if header in self._HEADER_FIELD_MAP
        }
        self._add_relative_balance_columns(headers, column_map)
        if not column_map:
            raise UserError(_('İçe aktarılacak muhasebe kolonu bulunamadı.'))
        self._validate_unique_courier_ids(rows, courier_id_index)

        created = updated = skipped = 0
        partner_model = self.env['res.partner']
        line_model = self.env['partner.courier.accounting.line']
        currency = self.env.company.currency_id

        for row in rows[1:]:
            courier_id = self._to_text(self._cell(row, courier_id_index))
            if not courier_id or courier_id.lower().startswith('kurye '):
                skipped += 1
                continue

            partner = partner_model.search([('courier_id', '=', courier_id)], limit=1)
            partner_count = partner_model.search_count([('courier_id', '=', courier_id)])
            if not partner_count:
                skipped += 1
                continue
            if partner_count > 1:
                raise UserError(_('Birden fazla contact aynı Kurye ID değerine sahip: %s') % courier_id)

            existing_line = line_model.search([
                ('partner_id', '=', partner.id),
                ('date_start', '=', self.date_start),
                ('date_end', '=', self.date_end),
            ], limit=1)
            overlapping_line = line_model.search([
                ('partner_id', '=', partner.id),
                ('date_start', '<=', self.date_end),
                ('date_end', '>=', self.date_start),
                '!',
                '&',
                ('date_start', '=', self.date_start),
                ('date_end', '=', self.date_end),
            ], limit=1)
            if overlapping_line:
                raise UserError(_('Hakedişte çakışan tarihler var. Bu tarih aralığı ile import edemezsin.'))

            vals = {
                'partner_id': partner.id,
                'currency_id': currency.id,
                'date_start': self.date_start,
                'date_end': self.date_end,
            }
            for index, (field_name, value_type) in column_map.items():
                vals[field_name] = self._convert_value(self._cell(row, index), value_type, field_name, courier_id)
            if existing_line:
                existing_line.write(vals)
                updated += 1
            else:
                line_model.create(vals)
                created += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Muhasebe Import'),
                'message': _('%s satır eklendi. %s satır güncellendi. %s satır atlandı.') % (created, updated, skipped),
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

    def _find_header_index(self, headers, header):
        try:
            return headers.index(header)
        except ValueError:
            return None

    def _add_relative_balance_columns(self, headers, column_map):
        for anchor, fields_to_map in self._POSITION_FIELD_MAP.items():
            anchor_index = self._find_header_index(headers, anchor)
            if anchor_index is None:
                continue
            for offset, field_info in enumerate(fields_to_map, start=1):
                column_map[anchor_index + offset] = field_info

    def _validate_required_headers(self, headers):
        missing_headers = [header for header in self._REQUIRED_HEADERS if header not in headers]
        if missing_headers:
            raise UserError(_('Excelde eksik kolon var: %s') % ', '.join(missing_headers))

    def _validate_unique_courier_ids(self, rows, courier_id_index):
        seen = set()
        duplicates = set()
        for row in rows[1:]:
            courier_id = self._to_text(self._cell(row, courier_id_index))
            if not courier_id or courier_id.lower().startswith('kurye '):
                continue
            if courier_id in seen:
                duplicates.add(courier_id)
            seen.add(courier_id)
        if duplicates:
            raise UserError(_('Excelde aynı Kurye ID birden fazla satırda var: %s') % ', '.join(sorted(duplicates)))

    def _clean_header(self, value):
        return ' '.join(self._to_text(value).split())

    def _cell(self, row, index):
        return row[index] if index < len(row) else ''

    def _to_text(self, value):
        if value in (None, False):
            return ''
        text = str(value).strip()
        return text[:-2] if text.endswith('.0') else text

    def _convert_value(self, value, value_type, field_name=None, courier_id=None):
        if value_type == 'char':
            return self._to_text(value)
        number = self._to_float(value, field_name=field_name, courier_id=courier_id)
        return int(round(number)) if value_type == 'int' else number

    def _to_float(self, value, field_name=None, courier_id=None):
        text = self._to_text(value)
        if not text:
            return 0.0
        text = text.replace('%', '').replace(' ', '')
        if ',' in text and '.' in text:
            text = text.replace('.', '').replace(',', '.')
        else:
            text = text.replace(',', '.')
        try:
            return float(text)
        except ValueError:
            raise UserError(_('Sayısal değer okunamadı. Kurye ID: %s, Alan: %s, Değer: %s') % (courier_id or '-', field_name or '-', text))

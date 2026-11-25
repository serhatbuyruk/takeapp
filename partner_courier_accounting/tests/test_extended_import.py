import base64
import uuid
from io import BytesIO
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from odoo.modules.module import get_module_resource
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestExtendedEarningsImport(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Format test', 'courier_id': 'QA-' + uuid.uuid4().hex,
        })
        self.wizard = self.env['partner.courier.accounting.import.wizard'].create({
            'file': base64.b64encode(b'placeholder'), 'date_start': '2026-11-16',
            'date_end': '2026-11-22', 'payment_date': '2026-12-01',
        })

    def headers(self, extended=True):
        filename = 'KURYETEC HAKEDİŞ FORMATI.xlsx' if extended else '11-17 MAYIS HAK EDİŞ (1).xlsx'
        with open(get_module_resource('partner_courier_accounting', filename), 'rb') as stream:
            self.wizard.file = base64.b64encode(stream.read())
        return [self.wizard._clean_header(value) for value in self.wizard._read_xlsx_rows()[0]]

    def upload(self, headers, rows):
        ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
        root = ET.Element('worksheet', xmlns=ns)
        data = ET.SubElement(root, 'sheetData')
        for i, values in enumerate([headers] + rows, 1):
            row = ET.SubElement(data, 'row', r=str(i))
            for j, value in enumerate(values):
                n, letters = j + 1, ''
                while n:
                    n, rem = divmod(n - 1, 26)
                    letters = chr(65 + rem) + letters
                cell = ET.SubElement(row, 'c', r=letters + str(i), t='inlineStr')
                ET.SubElement(ET.SubElement(cell, 'is'), 't').text = str(value)
        buf = BytesIO()
        with ZipFile(buf, 'w') as archive:
            archive.writestr('xl/workbook.xml', '<workbook xmlns="%s" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Test" sheetId="1" r:id="rId1"/></sheets></workbook>' % ns)
            archive.writestr('xl/_rels/workbook.xml.rels', '<Relationships><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
            archive.writestr('xl/worksheets/sheet1.xml', ET.tostring(root))
        self.wizard.file = base64.b64encode(buf.getvalue())

    def row(self, headers, extended=True):
        values = ['' for h in headers]
        values[0] = self.partner.courier_id
        for h in self.wizard._HEADER_FIELD_MAP:
            field, kind = self.wizard._HEADER_FIELD_MAP[h]
            values[headers.index(h)] = 'test' if kind == 'char' else '125,50'
        values[headers.index('Pick up')] = '12'
        values[headers.index('Drop off')] = '15'
        for anchor, entries in self.wizard._POSITION_FIELD_MAP.items():
            for offset, _entry in enumerate(entries, 1):
                values[headers.index(anchor) + offset] = str(offset * 17)
        if extended:
            values[headers.index('Yazlık Ek Paket Tutarı')] = '1.234,56'
            values[headers.index('P2 Kesintisi')] = '250,75'
            values[headers.index('Haciz Yazısı')] = 'İcra açıklaması\n' + 'uzunmetin' * 100
        return values

    def imported_line(self):
        return self.env['partner.courier.accounting.line'].search([('partner_id', '=', self.partner.id)])

    def test_legacy_and_extended_common_columns_match(self):
        old = self.headers(False)
        self.upload(old, [self.row(old, False)])
        self.wizard.action_import()
        line = self.imported_line()
        fields = [f for f, kind in self.wizard._HEADER_FIELD_MAP.values()]
        before = {field: line[field] for field in fields}
        self.assertFalse(line.has_extended_earnings_format)
        new = self.headers()
        self.upload(new, [self.row(new)])
        self.wizard.action_import()
        self.assertEqual(len(self.imported_line()), 1)
        self.assertEqual(before, {field: line[field] for field in fields})
        self.assertTrue(line.has_extended_earnings_format)
        self.assertEqual(line.summer_extra_package_amount, 1234.56)
        self.assertEqual(line.p2_deduction_amount, 250.75)
        self.assertIn('\n', line.garnishment_note)
        self.assertEqual(line.one_week_previous_negative_balance_amount, 17)
        self.assertEqual(line.two_week_previous_payment_deduction_amount, 17)
        self.assertEqual(line.one_week_previous_payment_deduction_amount, 34)
        self.upload(old, [self.row(old, False)])
        self.wizard.action_import()
        self.assertEqual(line.summer_extra_package_amount, 1234.56)
        self.assertTrue(line.has_extended_earnings_format)

    def test_blank_new_fields_and_pdf_html(self):
        headers = self.headers()
        row = self.row(headers)
        for name in self.wizard._EXTENDED_HEADER_FIELD_MAP:
            row[headers.index(name)] = ''
        self.upload(headers, [row])
        self.wizard.action_import()
        line = self.imported_line()
        self.assertTrue(line.has_extended_earnings_format)
        self.assertEqual(line.p2_deduction_amount, 0)
        for courier_type in ('motor', 'car'):
            if courier_type == 'car':
                self.partner.courier_type = 'car'
            content, _ = self.env['ir.actions.report']._render_qweb_html('partner_courier_accounting.action_report_courier_earning', line.ids)
            self.assertIn('P2 Kesintisi'.encode(), content)
            self.assertIn('Haciz Yazısı'.encode(), content)
        line.has_extended_earnings_format = False
        content, _ = self.env['ir.actions.report']._render_qweb_html('partner_courier_accounting.action_report_courier_earning', line.ids)
        self.assertNotIn('P2 Kesintisi'.encode(), content)

    def test_missing_and_duplicate_new_headers_rejected(self):
        headers = self.headers()
        for wrong in ([h for h in headers if h != 'P2 Kesintisi'], headers + ['Haciz Yazısı']):
            self.upload(wrong, [])
            with self.assertRaises(UserError):
                self.wizard.action_import()

    def test_duplicate_courier_and_overlapping_period_rejected(self):
        headers = self.headers()
        row = self.row(headers)
        self.upload(headers, [row, row])
        with self.assertRaises(UserError):
            self.wizard.action_import()
        self.assertFalse(self.imported_line())
        self.upload(headers, [row])
        self.wizard.action_import()
        self.wizard.date_start = '2026-11-17'
        with self.assertRaises(UserError):
            self.wizard.action_import()

    def test_invalid_second_row_rolls_back_entire_import(self):
        headers = self.headers()
        row = self.row(headers)
        other = self.env['res.partner'].create({'name': 'Other test', 'courier_id': 'QA-' + uuid.uuid4().hex})
        wrong = list(row)
        wrong[0] = other.courier_id
        wrong[headers.index('P2 Kesintisi')] = 'not a number'
        self.upload(headers, [row, wrong])
        with self.assertRaises(UserError), self.env.cr.savepoint():
            self.wizard.action_import()
        self.assertFalse(self.imported_line())

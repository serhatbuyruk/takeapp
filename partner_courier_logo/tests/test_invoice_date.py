from datetime import date

from odoo.tests.common import TransactionCase


class TestPartnerCourierLogoInvoiceDate(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Logo Tarih Test Kuryesi',
            'courier_tc': '11111111111',
        })
        settings = {
            'buyer_code': 'KURYETEC',
            'buyer_name': 'Kuryetec Test',
            'buyer_vkn': '1111111111',
            'buyer_tax_office': 'TEST',
            'buyer_country': 'TURKIYE',
            'buyer_postal_code': '07000',
            'buyer_city': 'Antalya',
            'buyer_district': 'Kepez',
            'buyer_address': 'Test Adresi',
            'buyer_phone': '8500000000',
        }
        params = cls.env['ir.config_parameter'].sudo()
        for key, value in settings.items():
            params.set_param('partner_courier_logo.%s' % key, value)

    def _payload_for_period(self, date_start, date_end):
        line = self.env['partner.courier.accounting.line'].create({
            'partner_id': self.partner.id,
            'date_start': date_start,
            'date_end': date_end,
            'earning_amount_tax_excluded': 1000,
        })
        invoice = self.env['partner.courier.logo.invoice'].create({
            'line_id': line.id,
        })
        return invoice._payload()

    def test_invoice_date_is_next_day_within_same_month(self):
        payload = self._payload_for_period(date(2026, 10, 19), date(2026, 10, 25))
        self.assertEqual(payload['invoiceDate'], '2026-10-26 00:00:00')

    def test_invoice_date_stays_on_month_end(self):
        payload = self._payload_for_period(date(2026, 10, 26), date(2026, 10, 31))
        self.assertEqual(payload['invoiceDate'], '2026-10-31 00:00:00')

    def test_invoice_date_stays_on_february_end(self):
        payload = self._payload_for_period(date(2026, 2, 23), date(2026, 2, 28))
        self.assertEqual(payload['invoiceDate'], '2026-02-28 00:00:00')

    def test_invoice_date_stays_on_year_end(self):
        payload = self._payload_for_period(date(2026, 12, 26), date(2026, 12, 31))
        self.assertEqual(payload['invoiceDate'], '2026-12-31 00:00:00')

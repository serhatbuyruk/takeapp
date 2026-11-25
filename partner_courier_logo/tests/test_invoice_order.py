from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestLogoInvoiceOrder(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({'name': 'Invoice order test'})
        self.october = self.line('2026-10-26', '2026-10-31')
        self.first = self.line('2026-11-01', '2026-11-01')
        self.second = self.line('2026-11-02', '2026-11-08')
        self.third = self.line('2026-11-09', '2026-11-15')

    def line(self, start, end, amount=1000):
        return self.env['partner.courier.accounting.line'].create({
            'partner_id': self.partner.id, 'date_start': start, 'date_end': end,
            'earning_amount_tax_excluded': amount,
        })

    def invoice(self, line, state='ready'):
        return self.env['partner.courier.logo.invoice'].create({'line_id': line.id, 'state': state})

    def test_new_courier_starts_november_second_and_cannot_skip(self):
        self.assertEqual(self.second._next_logo_invoice_line(), self.second)
        self.second._check_logo_invoice_order()
        with self.assertRaisesRegex(UserError, '02.11.2026 - 08.11.2026'):
            self.third._check_logo_invoice_order()

    def test_pre_november_is_hidden_and_blocked_before_external_request(self):
        self.assertFalse(self.october.logo_invoice_period_enabled)
        invoice = self.invoice(self.october, 'draft')
        with patch.object(type(invoice), '_send_to_logo') as send:
            with self.assertRaisesRegex(UserError, '1 Kasım 2026'):
                invoice.action_create_draft()
            send.assert_not_called()

    def test_previous_october_invoice_requires_november_first(self):
        self.invoice(self.october)
        self.assertEqual(self.second._next_logo_invoice_line(), self.first)
        with self.assertRaisesRegex(UserError, '01.11.2026 - 01.11.2026'):
            self.second._check_logo_invoice_order()
        self.invoice(self.first)
        self.second._check_logo_invoice_order()

    def test_existing_courier_continues_after_latest_period_without_backfill(self):
        self.invoice(self.second, 'completed')
        self.third._check_logo_invoice_order()
        with self.assertRaisesRegex(UserError, '09.11.2026 - 15.11.2026'):
            self.first._check_logo_invoice_order()

    def test_failed_and_cancelled_invoices_do_not_advance_order(self):
        invoice = self.invoice(self.second, 'failed')
        self.assertEqual(self.third._next_logo_invoice_line(), self.second)
        invoice.state = 'cancelled'
        self.assertEqual(self.third._next_logo_invoice_line(), self.second)
        invoice.state = 'ready'
        self.assertEqual(self.third._next_logo_invoice_line(), self.third)

    def test_zero_amount_and_other_couriers_do_not_block(self):
        self.second.earning_amount_tax_excluded = 0
        self.assertEqual(self.third._next_logo_invoice_line(), self.third)
        other = self.env['res.partner'].create({'name': 'Other order test'})
        self.third.partner_id = other
        self.assertEqual(self.third._next_logo_invoice_line(), self.third)

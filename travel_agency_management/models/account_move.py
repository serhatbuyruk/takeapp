# travel_agency_management/models/account_move.py

from odoo import models, api, _, fields
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_view_vendor_payments(self):
        self.ensure_one()

        # Bu aksiyonun sadece Tedarikçi Faturaları için çalıştığından emin olalım
        if self.move_type != 'in_invoice':
            raise UserError(_("This action is only available for vendor bills."))

        # Faturanın 'Ödenecek Borçlar' (payable) hesap satırlarını bul
        payable_lines = self.line_ids.filtered(
            lambda line: line.account_id.account_type == 'liability_payable'
        )

        # Bu satırlar ile eşleştirilmiş (reconciled) olan yevmiye kalemlerini bul.
        # Bu kalemler bize ödeme kayıtlarını verecektir.
        reconciled_lines = payable_lines.mapped('matched_debit_ids.debit_move_id') + \
                           payable_lines.mapped('matched_credit_ids.credit_move_id')
        
        # Yevmiye kalemlerinden 'account.payment' kayıtlarının ID'lerini al
        payment_ids = reconciled_lines.mapped('payment_id').ids

        if not payment_ids:
            raise UserError(_("No payments found for this bill."))

        # Ödemeleri gösteren bir pencere aksiyonu döndür
        return {
            'name': _('Payments for Bill %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', list(set(payment_ids)))],
            'target': 'current',
        }
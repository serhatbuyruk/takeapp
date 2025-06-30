from odoo import _, fields, models, api


class AccountPAymentPaytr(models.Model):
    _inherit = 'account.payment'

    def _compute_amount_available_for_refund(self):
        for payment in self:
            tx_sudo = payment.payment_transaction_id.sudo()
            if tx_sudo.provider_id.code != 'paytr':
                return super(AccountPAymentPaytr, self)._compute_amount_available_for_refund()
            if tx_sudo.provider_id.support_refund and tx_sudo.operation != 'refund':
                # Only consider refund transactions that are confirmed by summing the amounts of
                # payments linked to such refund transactions. Indeed, should a refund transaction
                # be stuck forever in a transient state (due to webhook failure, for example), the
                # user would never be allowed to refund the source transaction again.
                refund_payments = self.search([('source_payment_id', '=', self.id)])
                refunded_amount = abs(sum(refund_payments.mapped('amount')))
                if tx_sudo.refund_amount:
                    payment.amount_available_for_refund = tx_sudo.refund_amount - refunded_amount
                else:
                    payment.amount_available_for_refund = payment.amount - refunded_amount

            else:
                payment.amount_available_for_refund = 0

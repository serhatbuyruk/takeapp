# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
import base64
import hashlib
import hmac

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = "payment.provider"
    code = fields.Selection(
        selection_add=[('paytr', "PayTr")], ondelete={'paytr': 'set default'})
    paytr_merchant_id = fields.Char(string=_("Merchant Id"), required_if_provider="paytr")
    paytr_merchant_key = fields.Char(string=_("Merchant Key"), required_if_provider="paytr")
    paytr_merchant_salt = fields.Char(string=_("Merchant Salt"), required_if_provider="paytr")
    paytr_currency_id = fields.Many2one(
        string=_("Currency"), comodel_name='res.currency', required_if_provider="paytr")
    paytr_no_installment = fields.Selection(string=_("Is it in installments?"),
                                            selection=[('0', _("Yes")), ('1', _("No"))],
                                            default='0', required_if_provider="paytr")
    paytr_max_installmentt = fields.Selection(string=_("Number of installments"),
                                              selection=[('0', _("Maximum installment allowed")),
                                                         ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'),
                                                         ('7', '7'), ('8', '8'), ('9', '9'),
                                                         ('10', '10'), ('11', '11'), ('12', '12')
                                                         ],
                                              default='0', required_if_provider="paytr")
    paytr_timeout_limit = fields.Integer(string=_("timeout"), default=300, required_if_provider="paytr",
                                         help=_(
                                             """If a value other than zero is sent, the payment 
                                             transaction must be completed within this period. 
                                             (You can use it for security purposes in case 
                                             there is a price update in your system during payment)"""))
    paytr_payment_term_id = fields.Many2one(
        string=_("Payment Condition Installment-free transaction"), comodel_name='account.payment.term', required_if_provider="paytr")
    paytr_payment_interest_term_id = fields.Many2one(
        string=_("Payment Condition Installment transaction"), comodel_name='account.payment.term', required_if_provider="paytr")
    paytr_payment_interest_product_id = fields.Many2one(
        string=_("Interest rate service for installment transactions"), comodel_name='product.product', required_if_provider="paytr")

    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'paytr').update({
            'support_fees': False,
            'support_refund': 'partial'
        })

    def _get_validation_currency(self):
        """ Override of payment to return the currency for paytr validation operations.

        :return: The validation currency
        :rtype: recordset of `res.currency`
        """
        res = super()._get_validation_currency()
        if self.code != 'paytr':
            return res

        return self.paytr_currency_id

    def _paytr_calculate_hash(self, notification_data):
        merchant_key = self.paytr_merchant_key.encode()
        merchant_salt = self.paytr_merchant_salt
        hash_str = notification_data['merchant_oid'] + merchant_salt + notification_data['status'] + notification_data[
            'total_amount']
        return base64.b64encode(hmac.new(merchant_key, hash_str.encode(), hashlib.sha256).digest())

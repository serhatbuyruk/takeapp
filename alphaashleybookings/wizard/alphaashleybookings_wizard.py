# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
import base64


class alphaashleybookingsWizard(models.TransientModel):
    _name = "alphaashleybookings.wizard"
    _description = "alphaashleybookings Wizard"

    name = fields.Char(string="Name")
    sale_payment_type = fields.Selection([('bank','Bank'),('cash','Cash')],
                                    string="Payment Type", default="cash"
                                    )

    sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=32)
    sale_price = fields.Monetary(string="Sale Price", currency_field='sale_price_currency_id')
    deposit_price_currency_id = fields.Many2one('res.currency', string='Deposit Currency',default=32)
    deposit_price = fields.Monetary(string="Deposit Price", currency_field='deposit_price_currency_id')
    sale_description = fields.Char(string="Sale Description")
    received_amount_currency_id = fields.Many2one('res.currency', string='Received Amount Currency',default=32)
    received_amount = fields.Monetary(string="Received Amount", currency_field='received_amount_currency_id')
    last_received_amount = fields.Monetary(string="Last Received Amount", currency_field='received_amount_currency_id')
    remaining_amount_currency_id = fields.Many2one('res.currency', string='Remaining Amount Currency',default=32)
    remaining_amount = fields.Monetary(string="Remaining Amount", currency_field='remaining_amount_currency_id')
    commission_rate = fields.Float(string="Commission Rate")
    commission_amount_currency_id = fields.Many2one('res.currency', string='Commission Currency %',default=32)
    commission_amount = fields.Monetary(string="Commission Amount", currency_field='commission_amount_currency_id')
    customer_payment_status = fields.Selection([('not_paid','Not Paid'),('in_payment','In Payment'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
                                    string="Customer Payment Status ", default="not_paid"
                                    )


    @api.model
    def default_get(self, fields):
        defaults = super(alphaashleybookingsWizard, self).default_get(fields)

        active_ids = self.env.context.get("active_ids", [])
        # if len(active_ids) == 1:
        # Read active_id from context
        active_id = self.env.context.get('default_active_id')
        if active_id:
            # Fetch the selected record
            realestate = self.env["alphaashleybookings.profile"].browse(active_id)
            # Set values as default
            defaults['name'] = realestate.name
            defaults['sale_price'] = realestate.sale_price
            defaults['sale_price_currency_id'] = realestate.sale_price_currency_id.id
            defaults['deposit_price'] = realestate.deposit_price
            defaults['deposit_price_currency_id'] = realestate.deposit_price_currency_id.id
            defaults['remaining_amount'] = realestate.remaining_amount
            defaults['remaining_amount_currency_id'] = realestate.remaining_amount_currency_id.id
            defaults['last_received_amount'] = realestate.received_amount
            defaults['customer_payment_status'] = realestate.customer_payment_status
        return defaults

    # wizard's save button
    def update_realestate_information(self):
        # find active modems
        active_ids = self.env.context.get("active_ids", [])
        realestate = self.env["alphaashleybookings.profile"].browse(active_ids)
        # _logger.info("X" * 50 + "\n" + str(self) + "\n" + "X" * 50)
        realestate.write(
            {
                "sale_payment_type": self.sale_payment_type,
                "remaining_amount_currency_id": self.received_amount_currency_id.id,
                "remaining_amount": self.sale_price - self.last_received_amount - self.received_amount - self.deposit_price,
                "received_amount": self.received_amount,
            }
        )
        if realestate.sale_price > 0 and realestate.remaining_amount == 0 and realestate.received_amount > 0:
            realestate["customer_payment_status"] = "paid"
        if realestate.sale_price > 0 and realestate.remaining_amount > 0 and realestate.received_amount > 0:
            realestate["customer_payment_status"] = "partial"
        if realestate.sale_price > 0 and realestate.remaining_amount > 0 and realestate.received_amount == 0:
            realestate["customer_payment_status"] = "not_paid"
        #alphaashleybookings.check_context()
        # close the wizard
        return {"type": "ir.actions.act_window_close"}
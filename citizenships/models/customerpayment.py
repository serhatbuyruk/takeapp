# -*- coding: utf-8 -*-

from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime


# Creating Model/Table to Store Doctor Details
# https://www.youtube.com/watch?v=L6MxDR71_1k&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=2
class customerPayment(models.Model):
    _name = 'customer.payment'
    _description = 'Payment Record'

    name = fields.Char("Name")
    currency_id = fields.Many2one('res.currency', string='Currency Id')
    price = fields.Monetary(string="Amount", currency_field='currency_id')
    customer_payment_status = fields.Selection([('not_paid','Not Paid'),('in_payment','In Payment'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
                                    string="Customer Payment Status ", default="not_paid", tracking=True
                                    )
    description = fields.Text("Description")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")
    
class customerPaymentLines(models.Model):
    _name = 'customer.payment.lines'
    _description = 'Payment Lines Record'
    _order = 'order_sequence'

    name = fields.Char("Name")
    currency_id = fields.Many2one('res.currency', string='Currency Id')
    price = fields.Monetary(string="Amount", currency_field='currency_id')
    description = fields.Text("Description")
    customer_payment_status = fields.Selection([('not_paid','Not Paid'),('in_payment','In Payment'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
                                    string="Customer Payment Status ", default="not_paid"
                                    )
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    order_sequence = fields.Integer(string="Sequence")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")

    def from_profile(self):
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'citizenships.profile',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]'
        }
    
    
class citizenshipsProfileInherit(models.Model):
    _inherit = 'citizenships.profile'

    customer_payment_lines = fields.One2many('customer.payment.lines', 'sequence', string='Customer Payment',tracking=True)

    @api.onchange('customer_payment_lines')
    def customer_payment_lines_changed(self):
        received_amount = 0
        for customer_payment_line in self.customer_payment_lines:
            if customer_payment_line.customer_payment_status == "paid" or customer_payment_line.customer_payment_status == "partial":
                received_amount = customer_payment_line.price + received_amount
        self["received_amount_total"] = received_amount + self.deposit_price
        self["remaining_amount"] = self.sale_price - received_amount - self.deposit_price
        
        if self.sale_price > 0 and self.remaining_amount <= 0 and received_amount > 0:
            self["customer_payment_status"] = "paid"
            self["color"] = "#008000"
        if self.sale_price > 0 and self.remaining_amount > 0 and received_amount > 0:
            self["customer_payment_status"] = "partial"
            self["color"] = "#FFD700"
        if self.sale_price > 0 and self.remaining_amount > 0 and received_amount <= 0:
            self["customer_payment_status"] = "not_paid"
            self["color"] = "#FFD700"
            
        self["remaining_amount_currency_id"] = self.sale_price_currency_id.id
        self["deposit_price_currency_id"] = self.sale_price_currency_id.id
        
        if self.customer_payment_status == "paid":
            self["next_payment_date"] = False
    
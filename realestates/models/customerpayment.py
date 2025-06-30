# -*- coding: utf-8 -*-

from odoo import models, fields
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
            'res_model': 'realestates.profile',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]'
        }
    
    
class realestatesProfileInherit(models.Model):
    _inherit = 'realestates.profile'

    customer_payment_lines = fields.One2many('customer.payment.lines', 'sequence', string='Customer Payment',tracking=True)
    
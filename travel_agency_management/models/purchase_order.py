# -*- coding: utf-8 -*-
from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    origin_sale_order_id = fields.Many2one(
        'sale.order', 
        string='Origin Sale Order', 
        index=True, 
        copy=False,
        help="The sale order that generated this purchase order."
    )
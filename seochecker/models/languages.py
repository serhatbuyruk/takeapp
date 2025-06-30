# -*- coding: utf-8 -*-

from odoo import models, fields

class agencyLanguage(models.Model):
    _name = 'agency.language'
    _description = 'language seochecker'

    name = fields.Many2one('product.product', string="Product")
    description = fields.Text("Description")
    language_lines = fields.One2many('agency.language.lines', 'id', string='Language Lines')
    
class agencylanguageLines(models.Model):
    _name = 'agency.language.lines'
    _description = 'language Lines seochecker'

    product_id = fields.Many2one('product.product', string="Product")
    price = fields.Monetary(string="Price", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Para Birimi', default=31)
    description = fields.Text("Açıklama")
    sequence = fields.Integer(string="Sıra")
    color = fields.Integer(string="Renk")
    
    
class resPartnerInherit(models.Model):
    _inherit = 'res.partner'

    language_lines = fields.One2many('agency.language.lines', 'sequence', string='Language Lines')
    

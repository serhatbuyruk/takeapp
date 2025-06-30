# -*- coding: utf-8 -*-

from odoo import models, fields


# Creating Model/Table to Store Doctor Details
# https://www.youtube.com/watch?v=L6MxDR71_1k&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=2
class agencyCity(models.Model):
    _name = 'agency.city'
    _description = 'City Record'

    name = fields.Many2one('res.country.state', string="Name", domain="[('country_id', '=', 224)]")
    country_id = fields.Many2one('res.country', string="Country")
    description = fields.Text("Description")
    image_1 = fields.Binary(string="Image 1")
    city_lines = fields.One2many('agency.city.lines', 'id', string='Cities')
    
class agencyCityLines(models.Model):
    _name = 'agency.city.lines'
    _description = 'City Lines Record'

    city_id = fields.Many2one('agency.city', string='Şehir')
    price = fields.Monetary(string="Price", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Para Birimi')
    description = fields.Text("Açıklama")
    sequence = fields.Integer(string="Sıra")
    color = fields.Integer(string="Renk")
    
    
class resPartnerInherit(models.Model):
    _inherit = 'res.partner'

    city_lines = fields.One2many('agency.city.lines', 'sequence', string='Cities')
    

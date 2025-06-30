# -*- coding: utf-8 -*-

from odoo import models, fields

class agencyNotary(models.Model):
    _name = 'agency.notary'
    _description = 'notary seochecker'

    name = fields.Many2one('res.lang', string="Dil", domain=["|",["active","=",True],["active","=",False]])
    description = fields.Text("Description")
    notary_lines = fields.One2many('agency.notary.lines', 'id', string='Notary Lines')
    
class agencynotaryLines(models.Model):
    _name = 'agency.notary.lines'
    _description = 'notary Lines seochecker'

    language = fields.Many2one('res.lang', string="Dil", domain=["|",["active","=",True],["active","=",False]])
    notary = fields.Char("Noter")
    description = fields.Char("Açıklama")
    sequence = fields.Integer(string="Sıra")
    color = fields.Integer(string="Renk")
    
    
class resPartnerInherit(models.Model):
    _inherit = 'res.partner'

    notary_lines = fields.One2many('agency.notary.lines', 'sequence', string='Notary Lines')
    

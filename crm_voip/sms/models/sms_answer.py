# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SmsAnswer(models.Model):
    _name = 'crm_voip.sms.answer'
    _rec_name = 'name'
    _description = 'Sms Answer'

    partner_id = fields.Many2one('res.partner', string='Operator', domain=[('is_company', '=', True)], required=True)
    name = fields.Char("Name")
    content = fields.Text("Content")

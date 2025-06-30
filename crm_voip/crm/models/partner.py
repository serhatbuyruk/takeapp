# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID


class ResPartnerInherits(models.Model):
    _inherit = 'res.partner'

    sms_provider = fields.Many2one('crm_voip.providers.sms_services', string='Sms Provider')


class Seller(models.Model):
    _name = 'crm_voip.seller'
    _rec_name = 'name'

    name = fields.Char("Name")
    partner_id = fields.Many2one('res.partner', string='Operator', domain=[('is_company', '=', True)], required=True)
    callcenter = fields.Char("Call Center")
    callcenter_prefix = fields.Char("Outgoing Call Prefix")

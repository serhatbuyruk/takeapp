# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID
import time
from odoo.exceptions import ValidationError


class CallLog(models.Model):
    _name = 'crm_voip.crm.customer.call_log'
    _description = 'Call Log'

    partner_id = fields.Many2one(comodel_name='res.partner', string='Operator', domain=[('is_company', '=', True)],
                                 required=True)
    call_id = fields.Many2one(comodel_name="crm_voip.crm.customer.call", string="Call", required=False)
    pbx_num = fields.Char("Pbx Number")
    unique_id = fields.Char("Unique ID")
    internal_num = fields.Char("Internal Number")
    customer_num = fields.Char("Customer Number")
    incoming_number = fields.Char("Incoming Number")
    scenario = fields.Char("Scenario")
    context = fields.Char("Context")
    context_name = fields.Char("Context Name")
    digit = fields.Char("Digit")
    type = fields.Char("Type")
    queue_name = fields.Char("Queue Name")
    talktime = fields.Integer("Talk Time")
    holdtime = fields.Integer("Hold Time")

    @api.model
    def default_get(self, fields):
        res = super(CallLog, self).default_get(fields)
        if self.env.user.partner_id.parent_id:
            res['partner_id'] = self.env.user.partner_id.parent_id.id
        return res


# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SmsLog(models.Model):
    _name = 'crm_voip.sms.log'
    _description = 'Sms Log'
    _rec_name = 'mobile_number'

    partner_id = fields.Many2one(comodel_name="res.partner", string="Operator")
    customer_id = fields.Many2one(comodel_name="crm_voip.crm.customer", string="Customer")
    phone_id = fields.Many2one(comodel_name="crm_voip.crm.customer.phone", string="Phone")
    mobile_number = fields.Char("Mobile Number")
    sms_content = fields.Text("Sms Content")
    service_id = fields.Many2one(comodel_name="crm_voip.providers.sms_services", string="Service")
    result = fields.Boolean(string="Result")
    result_text = fields.Text(string="Result Text")
    matched = fields.Boolean("Matched", default=False)

    @api.model
    def match_customer(self):
        sms_log = self.search([('matched', '=', False)])
        for r in sms_log:
            phone_id = self.env['crm_voip.crm.customer.phone'].search(
                [('phone', '=', r.mobile_number), ('partner_id', '=', r.partner_id.id)],
                order='id desc', limit=1)
            r.write({
                'phone_id': phone_id.id,
                'matched': True,
                'customer_id': phone_id.customer_id.id
            })

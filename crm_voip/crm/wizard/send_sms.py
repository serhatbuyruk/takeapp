# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
import time


class SendCustomerSmsWizard(models.Model):
    _name = 'crm_voip.crm.customer.sms_wizard'
    _description = 'Sms Wizard'

    partner_id = fields.Many2one('res.partner', string='Operator', domain=[('is_company', '=', True)])
    phone_id = fields.Many2one(comodel_name="crm_voip.crm.customer.phone", string="Phone Number", required=True)
    customer_id = fields.Many2one(comodel_name="crm_voip.crm.customer", string="Customer",
                                  related='phone_id.customer_id')
    answer_id = fields.Many2one(comodel_name="crm_voip.sms.answer", string="Sms Template")
    sms_text = fields.Text("Sms Text")

    @api.onchange("answer_id")
    def _onchange_answer_id(self):
        self.sms_text = self.answer_id.content

    def send_sms(self):
        for record in self:
            self.env['crm_voip.providers.sms_services'].send_sms_by_user(record.partner_id, record.phone_id.phone,
                                                                      record.sms_text)

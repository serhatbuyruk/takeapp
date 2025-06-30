# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import datetime


class CrmCallWizard(models.Model):
    _name = 'crm_voip.crm.call_wizard'
    _description = 'Call Wizard'

    pbx_id = fields.Many2one(comodel_name="crm_voip.providers.pbx", string="PBX")
    seller_id = fields.Many2one(comodel_name="crm_voip.seller", string="Seller")
    internal_num = fields.Char("Internal Number")
    call_id = fields.Many2one(comodel_name="crm_voip.crm.customer.call", string="Call")
    phone_id = fields.Many2one(comodel_name="crm_voip.crm.customer.phone", string="Phone", required=True)

    @api.model
    def default_get(self, fields):
        res = super(CrmCallWizard, self).default_get(fields)
        pbx_record = self.env['crm_voip.providers.pbx'].search([])
        if len(pbx_record) == 1:
            res['pbx_id'] = pbx_record.id
        res['internal_num'] = self.env.user.partner_id.phone
        return res

    def call_phone(self):
        for record in self:
            result = record.pbx_id.call_phone(record.seller_id, record.phone_id.phone, record.internal_num)
            if result.get('message') == 'Successfully':
                self.env['crm_voip.crm.customer.call'].create({
                    'customer_id': record.phone_id.customer_id.id,
                    'phone_id': record.phone_id.id,
                    'seller_id': record.seller_id.id,
                    'unique_id': result['unique_id'],
                    'internal_number': record.internal_num,
                    'type': 'outbound',
                    'start': datetime.now(),
                    'phone': record.phone_id.phone,
                })

                if record.call_id and record.call_id.unanswered:
                    record.call_id.write({
                        'unanswered': False
                    })

            else:
                raise Warning(_("Call couldn't be started. Please check your VoIP software or phone"))
            print(result)

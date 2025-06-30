# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import timedelta


class CrmCallWizard(models.Model):
    _name = 'crm_voip.crm.fetch_wizard'
    _description = 'Fetch Call Detail'

    pbx_id = fields.Many2one(comodel_name="crm_voip.providers.pbx", string="PBX")
    start_date = fields.Datetime(string="Start", required=True)
    end_date = fields.Datetime(string="End", required=True)

    @api.model
    def default_get(self, fields):
        res = super(CrmCallWizard, self).default_get(fields)
        res['pbx_id'] = self._context.get('active_id')
        return res

    def fetch(self):
        for record in self:
            record.pbx_id.fetch_call_detail(recordstart_date + timedelta(hours=3), record.end_date + timedelta(hours=3))

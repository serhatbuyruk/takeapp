# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
import base64


class cordersWizard(models.TransientModel):
    _name = "corders.wizard"
    _description = "Corders Wizard"

    name = fields.Char(string="Name")
    kurye = fields.Many2one('res.partner', string="Kurye", domain="[('user_role', '=', 'kurye')]", tracking=True, copy=False)
    corder_id = fields.Many2one('corders.profile', string="Sipariş", required=True)


    @api.model
    def default_get(self, fields_list):
        res = super(cordersWizard, self).default_get(fields_list)
        # 'corder_id' değerini context'ten alıyoruz
        corder_id = self.env.context.get('corder_id')
        if corder_id:
            corder = self.env['corders.profile'].browse(corder_id)
            res.update({
                'name': corder.name,
                'kurye': corder.kurye.id,
                'corder_id': corder.id,
            })
        return res

    def update_corder_information(self):
        # Seçilen kuryeyi siparişe atıyoruz
        self.corder_id.write({
            'kurye': self.kurye.id,
        })
        # Wizard'ı kapatıyoruz
        return {'type': 'ir.actions.act_window_close'}
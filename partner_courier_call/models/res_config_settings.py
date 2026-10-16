from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    partner_courier_call_support_start_hour = fields.Float(
        string='Destek Başlangıç Saati',
        config_parameter='partner_courier_call.support_start_hour',
        default=9.0,
    )
    partner_courier_call_support_end_hour = fields.Float(
        string='Destek Bitiş Saati',
        config_parameter='partner_courier_call.support_end_hour',
        default=18.0,
    )

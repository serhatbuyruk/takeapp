from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    partner_courier_main_website_domain = fields.Char(
        string='Main Website Domain',
        config_parameter='partner_courier_accounting.main_website_domain',
    )

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    x_google_maps_geocode_api_key = fields.Char(
        string="Google Maps Geocode API Key",
        groups="base.group_system",
    )
    x_sepettakip_api_key = fields.Char(
        string="SepetTakip API Key",
        groups="base.group_system",
    )
    x_sepettakip_courier_company = fields.Char(
        string="SepetTakip Courier Company",
        groups="base.group_system",
    )
    x_sepettakip_url = fields.Char(
        string="SepetTakip URL",
        groups="base.group_system",
    )
    x_yeppos_api_key = fields.Char(
        string="YepPos API Key",
        groups="base.group_system",
    )
    x_yeppos_url = fields.Char(
        string="YepPos URL",
        groups="base.group_system",
    )

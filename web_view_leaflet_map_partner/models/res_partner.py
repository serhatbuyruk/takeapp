# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    display_address = fields.Char(compute="_compute_display_address")
    lat = fields.Float(string="Latitude", digits=(12, 6))
    lng = fields.Float(string="Longitude", digits=(12, 6))
    konum_dogrulugu = fields.Float(string="Konum Doğruluğu")
    son_konum_zamani = fields.Datetime(string="Son Konum Zamanı")
    konum_online = fields.Boolean(string="Konum Online")

    def _compute_display_address(self):
        for partner in self:
            partner.display_address = partner._display_address(without_company=True)

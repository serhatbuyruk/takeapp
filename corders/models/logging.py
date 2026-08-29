from odoo import fields, models


class IrLogging(models.Model):
    _inherit = "ir.logging"

    x_raw_json = fields.Json(string="Raw JSON")

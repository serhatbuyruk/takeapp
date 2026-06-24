from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    partner_courier_onesignal_app_id = fields.Char(
        string='OneSignal App ID',
        config_parameter='partner_courier_notification.onesignal_app_id',
    )
    partner_courier_onesignal_api_key = fields.Char(
        string='OneSignal API Key',
        config_parameter='partner_courier_notification.onesignal_api_key',
    )

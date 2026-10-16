from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    partner_courier_main_website_domain = fields.Char(
        string='Main Website Domain',
        config_parameter='partner_courier_accounting.main_website_domain',
    )
    partner_courier_kuryetec_sso_enabled = fields.Boolean(
        string='Kuryetec SSO Geçişi Aktif',
        config_parameter='partner_courier_accounting.kuryetec_sso_enabled',
    )
    partner_courier_kuryetec_sso_login = fields.Char(
        string='Özel Giriş E-Postası',
        default='demo@demo.com',
        config_parameter='partner_courier_accounting.kuryetec_sso_login',
    )
    partner_courier_kuryetec_sso_password = fields.Char(
        string='Özel Giriş Parolası',
        config_parameter='partner_courier_accounting.kuryetec_sso_password',
    )
    partner_courier_kuryetec_sso_shared_secret = fields.Char(
        string='Kuryetec SSO Shared Secret',
        config_parameter='partner_courier_accounting.kuryetec_sso_shared_secret',
        help='Kuryetec Odoo tarafındaki Shared Secret ile birebir aynı değer olmalıdır.',
    )

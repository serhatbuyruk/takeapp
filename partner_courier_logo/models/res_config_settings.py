from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    partner_courier_logo_enabled = fields.Boolean(
        string='Logo İşbaşı Entegrasyonu Aktif',
        config_parameter='partner_courier_logo.enabled',
    )
    partner_courier_logo_test_mode = fields.Boolean(
        string='Logo Test Simülasyonu',
        config_parameter='partner_courier_logo.test_mode',
        help='Dış Logo API çağrısı yapmadan SSO ve taslak fatura akışını yerelde test eder.',
    )
    partner_courier_logo_base_url = fields.Char(
        string='Logo API Base URL',
        default='https://soho-isbasi-mwv3-stg.logo-paas.com',
        config_parameter='partner_courier_logo.base_url',
    )
    partner_courier_logo_api_key = fields.Char(
        string='Logo API Key', config_parameter='partner_courier_logo.api_key',
    )
    partner_courier_logo_integration_login = fields.Char(
        string='Entegrasyon Kullanıcı Adı', config_parameter='partner_courier_logo.integration_login',
    )
    partner_courier_logo_integration_password = fields.Char(
        string='Entegrasyon Parolası', config_parameter='partner_courier_logo.integration_password',
    )
    partner_courier_logo_sso_start_endpoint = fields.Char(
        string='SSO Başlatma Endpointi', default='/api/v1.0/user/ssorequesturl',
        config_parameter='partner_courier_logo.sso_start_endpoint',
    )
    partner_courier_logo_sso_exchange_endpoint = fields.Char(
        string='SSO Anahtar Endpointi', default='/api/v1.0/user/getuserappkey',
        config_parameter='partner_courier_logo.sso_exchange_endpoint',
    )
    partner_courier_logo_sso_login_endpoint = fields.Char(
        string='SSO Login Endpointi', default='/api/v1.0/user/Login',
        config_parameter='partner_courier_logo.sso_login_endpoint',
    )
    partner_courier_logo_invoice_endpoint = fields.Char(
        string='Taslak Fatura Endpointi', default='/api/v1.0/invoices/integrationInvoices',
        config_parameter='partner_courier_logo.invoice_endpoint',
    )
    partner_courier_logo_buyer_name = fields.Char(
        string='Alıcı Ünvanı', default='KURYETEC LOJİSTİK LİMİTED ŞİRKETİ',
        config_parameter='partner_courier_logo.buyer_name',
    )
    partner_courier_logo_buyer_vkn = fields.Char(
        string='Alıcı VKN', default='5970986246',
        config_parameter='partner_courier_logo.buyer_vkn',
    )
    partner_courier_logo_buyer_tax_office = fields.Char(
        string='Alıcı Vergi Dairesi', default='ANTALYA KURUMLAR VERGİ DAİRESİ',
        config_parameter='partner_courier_logo.buyer_tax_office',
    )

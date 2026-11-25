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
        help='Dış Logo API çağrısı yapmadan fatura gönderim akışını yerelde test eder.',
    )
    partner_courier_logo_base_url = fields.Char(
        string='Logo Giriş API Base URL',
        default='https://integration.isbasi.com',
        config_parameter='partner_courier_logo.base_url',
        help='Fatura servis adresi başarılı giriş yanıtındaki baseUrl alanından otomatik alınır.',
    )
    partner_courier_logo_api_key = fields.Char(
        string='Logo API Key', config_parameter='partner_courier_logo.api_key',
    )
    partner_courier_logo_buyer_code = fields.Char(
        string='Alıcı Cari Kodu', config_parameter='partner_courier_logo.buyer_code', default='KURYETEC',
    )
    partner_courier_logo_buyer_name = fields.Char(
        string='Alıcı Ünvanı', config_parameter='partner_courier_logo.buyer_name',
    )
    partner_courier_logo_buyer_vkn = fields.Char(
        string='Alıcı VKN', config_parameter='partner_courier_logo.buyer_vkn',
    )
    partner_courier_logo_buyer_tax_office = fields.Char(
        string='Alıcı Vergi Dairesi', config_parameter='partner_courier_logo.buyer_tax_office',
    )
    partner_courier_logo_buyer_country = fields.Char(
        string='Alıcı Ülke', config_parameter='partner_courier_logo.buyer_country', default='TÜRKİYE',
    )
    partner_courier_logo_buyer_postal_code = fields.Char(
        string='Alıcı Posta Kodu', config_parameter='partner_courier_logo.buyer_postal_code',
    )
    partner_courier_logo_buyer_city = fields.Char(
        string='Alıcı İl', config_parameter='partner_courier_logo.buyer_city',
    )
    partner_courier_logo_buyer_district = fields.Char(
        string='Alıcı İlçe', config_parameter='partner_courier_logo.buyer_district',
    )
    partner_courier_logo_buyer_address = fields.Char(
        string='Alıcı Adres', config_parameter='partner_courier_logo.buyer_address',
    )
    partner_courier_logo_buyer_phone = fields.Char(
        string='Alıcı Telefon', config_parameter='partner_courier_logo.buyer_phone',
    )
    partner_courier_logo_buyer_email = fields.Char(
        string='Alıcı E-Posta', config_parameter='partner_courier_logo.buyer_email',
    )
    partner_courier_logo_integration_login = fields.Char(
        string='İşbaşı Hesap E-Postası', config_parameter='partner_courier_logo.integration_login',
    )
    partner_courier_logo_integration_password = fields.Char(
        string='Entegrasyon Parolası', config_parameter='partner_courier_logo.integration_password',
    )
    partner_courier_logo_login_endpoint = fields.Char(
        string='Entegrasyon Giriş Endpointi', default='/api/v1.0/user/integrationLogin',
        config_parameter='partner_courier_logo.login_endpoint',
    )
    partner_courier_logo_invoice_endpoint = fields.Char(
        string='Kurye Fatura Gönderim Endpointi', default='/api/v1.0/invoices/integrationInvoices',
        config_parameter='partner_courier_logo.invoice_endpoint',
    )

    def action_test_partner_courier_logo_connection(self):
        self.ensure_one()
        self.env['partner.courier.logo.invoice'].sudo()._get_logo_authentication(force_refresh=True)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Logo İşbaşı',
                'message': 'Merkezi İşbaşı hesabı ile bağlantı başarıyla kuruldu.',
                'type': 'success',
                'sticky': False,
            },
        }

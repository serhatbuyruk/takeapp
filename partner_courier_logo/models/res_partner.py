from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    logo_connection_state = fields.Selection([
        ('disconnected', 'Bağlı Değil'), ('connected', 'Bağlı'), ('error', 'Hatalı'),
    ], string='Logo İşbaşı Bağlantısı', default='disconnected', copy=False, index=True)
    logo_tenant_id = fields.Char(string='Logo Tenant ID', copy=False, groups='base.group_system')
    logo_access_token = fields.Char(string='Logo Access Token', copy=False, groups='base.group_system')
    logo_connected_at = fields.Datetime(string='Logo Bağlantı Tarihi', copy=False, readonly=True)
    logo_connection_error = fields.Text(string='Logo Bağlantı Hatası', copy=False, readonly=True,
                                        groups='base.group_system')


class PartnerCourierAccountingLine(models.Model):
    _inherit = 'partner.courier.accounting.line'

    logo_invoice_ids = fields.One2many('partner.courier.logo.invoice', 'line_id', string='Logo Faturaları')
    logo_invoice_state = fields.Selection([
        ('draft', 'Hazırlık'), ('awaiting_connection', 'Logo Bağlantısı Bekliyor'),
        ('creating', 'Taslak Oluşturuluyor'), ('ready', 'Onay Bekliyor'),
        ('completed', 'Kesildi'), ('failed', 'Hatalı'),
    ], compute='_compute_logo_invoice_state', string='Logo Fatura Durumu')

    def _compute_logo_invoice_state(self):
        for line in self:
            invoice = line.logo_invoice_ids[:1]
            line.logo_invoice_state = invoice.state if invoice else False

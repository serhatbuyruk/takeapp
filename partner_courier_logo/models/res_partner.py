from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    logo_invoice_enabled = fields.Boolean(
        string='Kurye Fatura Kesebilir',
        help='İşaretli kuryeler hakediş ekranında Logo İşbaşı fatura oluşturma butonunu görür.',
    )
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

    logo_invoice_period_enabled = fields.Boolean(compute='_compute_logo_invoice_policy')
    logo_invoice_order_error = fields.Char(compute='_compute_logo_invoice_policy')

    def _next_logo_invoice_line(self):
        self.ensure_one()
        lines = self.sudo().search([('partner_id', '=', self.partner_id.id),
                                   ('date_start', '!=', False), ('date_end', '!=', False)],
                                  order='date_end, date_start, id')
        sent = lines.filtered(lambda line: line.logo_invoice_state in ('ready', 'completed'))
        last = sent[-1:]
        start = date(2026, 11, 1) if last else date(2026, 11, 2)
        return lines.filtered(lambda line: (
            line.date_start >= start
            and (not last or line.date_end > last.date_end)
            and line.logo_invoice_state not in ('ready', 'completed')
            and (line.bonus_included_total_payment_tax_excluded
                 or line.total_payment_tax_excluded or line.earning_amount_tax_excluded) > 0
        ))[:1]

    def _logo_order_error(self, next_line):
        self.ensure_one()
        if not self.date_start or self.date_start < date(2026, 11, 1):
            return _('1 Kasım 2026 öncesi hakedişler için fatura oluşturulamaz.')
        if self.logo_invoice_state in ('ready', 'completed'):
            return False
        if next_line and self == next_line:
            return False
        if next_line:
            return _(
                'Faturalarınızı tarih sırasına göre oluşturmalısınız. '
                'Önce %s - %s dönemine ait hakediş faturasını oluşturun; '
                'ardından sonraki döneme geçebilirsiniz.'
            ) % (next_line.date_start.strftime('%d.%m.%Y'), next_line.date_end.strftime('%d.%m.%Y'))
        return _('Son oluşturduğunuz faturadan sonraki uygun hakediş döneminden devam etmelisiniz.')

    @api.depends('date_start', 'date_end', 'partner_id', 'logo_invoice_ids.state')
    def _compute_logo_invoice_policy(self):
        for partner in self.mapped('partner_id'):
            lines = self.filtered(lambda line: line.partner_id == partner)
            next_line = lines[:1]._next_logo_invoice_line()
            for line in lines:
                line.logo_invoice_period_enabled = bool(line.date_start and line.date_start >= date(2026, 11, 1))
                line.logo_invoice_order_error = line._logo_order_error(next_line)

    def _check_logo_invoice_order(self):
        self.ensure_one()
        error = self._logo_order_error(self._next_logo_invoice_line())
        if error:
            raise UserError(error)

    logo_invoice_ids = fields.One2many('partner.courier.logo.invoice', 'line_id', string='Logo Faturaları')
    logo_invoice_state = fields.Selection([
        ('draft', 'Hazırlık'), ('awaiting_connection', 'Logo Bağlantısı Bekliyor'),
        ('creating', 'Taslak Oluşturuluyor'), ('ready', 'Onay Bekliyor'),
        ('completed', 'Kesildi'), ('cancelled', 'Geri Alındı'), ('failed', 'Hatalı'),
    ], compute='_compute_logo_invoice_state', string='Logo Fatura Durumu')

    @api.depends('logo_invoice_ids.state')
    def _compute_logo_invoice_state(self):
        for line in self:
            invoice = line.logo_invoice_ids[:1]
            line.logo_invoice_state = invoice.state if invoice else False

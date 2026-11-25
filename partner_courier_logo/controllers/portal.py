from odoo import http, _
from odoo.http import request


class CourierLogoPortal(http.Controller):

    def _partner(self):
        partner_id = request.session.get('courier_accounting_partner_id')
        return request.env['res.partner'].sudo().browse(partner_id).exists() if partner_id else request.env['res.partner']

    def _line(self, line_id):
        partner = self._partner()
        if not partner:
            return request.env['partner.courier.accounting.line'], partner
        line = request.env['partner.courier.accounting.line'].sudo().search([
            ('id', '=', line_id), ('partner_id', '=', partner.id),
        ], limit=1)
        return line, partner

    def _result(self, title, message, line=None, error=False):
        return request.render('partner_courier_logo.courier_logo_result', {
            'title': title, 'message': message, 'line': line, 'error': error,
        })

    @http.route('/kurye-muhasebe/logo/fatura/<int:line_id>/olustur', type='http', auth='public', methods=['POST'], website=True, csrf=True, sitemap=False)
    def create_invoice(self, line_id, **kw):
        line, partner = self._line(line_id)
        if not partner or not line:
            return request.redirect('/kurye-muhasebe')
        if not partner.logo_invoice_enabled:
            return self._result(
                _('Fatura Oluşturulamadı'),
                _('Bu kurye için fatura oluşturma yetkisi tanımlı değil.'),
                line=line,
                error=True,
            )
        if kw.get('invoice_order_confirmed') != '1':
            return self._result(
                _('Fatura Onayı Gerekli'),
                _(
                    'Fatura oluşturmadan önce geçmiş dönemleri kontrol edin ve '
                    'işleme en eski hakediş döneminden başlayın.'
                ),
                line=line,
                error=True,
            )
        invoice = request.env['partner.courier.logo.invoice'].sudo().get_or_create_for_line(line)
        try:
            invoice.action_create_draft()
        except Exception as exc:
            return self._result(_('Fatura Oluşturulamadı'), str(exc), line=line, error=True)
        return self._result(_('Fatura Gönderildi'), _('Hakediş faturanız Kuryetec İşbaşı hesabına iletildi.'), line=line)

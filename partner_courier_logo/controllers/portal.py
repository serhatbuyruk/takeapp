from urllib.parse import urlencode

from odoo import fields, http, _
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
        invoice = request.env['partner.courier.logo.invoice'].sudo().get_or_create_for_line(line)
        if partner.logo_connection_state != 'connected':
            invoice.write({'state': 'awaiting_connection'})
            return request.redirect('/kurye-muhasebe/logo/bagla/%s' % line.id)
        try:
            invoice.action_create_draft()
        except Exception as exc:
            return self._result(_('Fatura Oluşturulamadı'), str(exc), line=line, error=True)
        return self._result(_('Taslak Fatura Hazır'), _('Taslak faturanız Logo İşbaşı hesabınızda onay bekliyor.'), line=line)

    @http.route('/kurye-muhasebe/logo/bagla/<int:line_id>', type='http', auth='public', methods=['GET'], website=True, sitemap=False)
    def sso_start(self, line_id, **kw):
        line, partner = self._line(line_id)
        if not partner or not line:
            return request.redirect('/kurye-muhasebe')
        logo = request.env['partner.courier.logo.invoice'].sudo()
        if logo._setting('test_mode').lower() == 'true':
            partner.sudo().write({
                'logo_connection_state': 'connected',
                'logo_access_token': 'logo-test-token',
                'logo_tenant_id': 'logo-test-tenant',
                'logo_connected_at': fields.Datetime.now(),
                'logo_connection_error': False,
            })
            return self._result(_('Logo Test Bağlantısı Hazır'), _('Test modunda fatura bağlantısı tamamlandı. Hakedişe dönüp Fatura Kes butonuna basın.'), line=line)
        if logo._setting('enabled').lower() != 'true':
            return self._result(_('Logo İşbaşı Hazır Değil'), _('Yönetici, Logo API ayarlarını tamamlayıp entegrasyonu etkinleştirmelidir.'), line=line, error=True)
        state = request.env['partner.courier.logo.sso.state'].sudo().create_for(partner, line)
        try:
            response = logo._call_logo('GET', logo._setting('sso_start_endpoint'))
            data = logo._data(response)
            redirect_url = logo._value(data, 'url', 'redirectUrl', 'ssoUrl', 'requestUrl') or logo._value(response, 'url', 'redirectUrl', 'ssoUrl', 'requestUrl')
            if not redirect_url:
                raise ValueError(_('Logo SSO başlangıç adresi API yanıtında bulunamadı.'))
            separator = '&' if '?' in redirect_url else '?'
            return request.redirect('%s%s%s' % (redirect_url, separator, urlencode({'state': state.token})), local=False)
        except Exception as exc:
            partner.sudo().write({'logo_connection_state': 'error', 'logo_connection_error': str(exc)})
            return self._result(_('Logo Bağlantısı Başlatılamadı'), str(exc), line=line, error=True)

    @http.route('/kurye-muhasebe/logo/sso/callback', type='http', auth='public', methods=['GET'], website=True, csrf=False, sitemap=False)
    def sso_callback(self, state=None, appUserKey=None, app_user_key=None, **kw):
        sso_state = request.env['partner.courier.logo.sso.state'].sudo().search([
            ('token', '=', state or ''), ('used', '=', False), ('expires_at', '>', fields.Datetime.now()),
        ], limit=1)
        if not sso_state:
            return self._result(_('Logo Bağlantısı Geçersiz'), _('Bağlantı anahtarı geçersiz veya süresi dolmuş.'), error=True)
        app_user_key = appUserKey or app_user_key
        if not app_user_key:
            return self._result(_('Logo Bağlantısı Tamamlanamadı'), _('Logo callback yanıtında appUserKey bulunamadı.'), line=sso_state.line_id, error=True)
        logo = request.env['partner.courier.logo.invoice'].sudo()
        partner = sso_state.partner_id
        try:
            exchange = logo._call_logo('POST', logo._setting('sso_exchange_endpoint'), {'appUserKey': app_user_key})
            second_key = logo._value(logo._data(exchange), 'appUserKey', 'appUserKey2', 'key')
            login_payload = {'username': logo._setting('integration_login'), 'password': logo._setting('integration_password'), 'appUserKey': second_key}
            login = logo._call_logo('POST', logo._setting('sso_login_endpoint'), login_payload)
            data = logo._data(login)
            token = logo._value(data, 'accessToken', 'access_token', 'token')
            tenant_id = logo._value(data, 'tenantId', 'tenant_id')
            if not token or not tenant_id:
                raise ValueError(_('Logo SSO login yanıtında access token veya tenantId bulunamadı.'))
            partner.write({'logo_connection_state': 'connected', 'logo_access_token': token, 'logo_tenant_id': str(tenant_id),
                           'logo_connected_at': fields.Datetime.now(), 'logo_connection_error': False})
            sso_state.write({'used': True})
            return self._result(_('Logo Hesabı Bağlandı'), _('Fatura bağlantısı tamamlandı. Hakedişe dönüp Fatura Kes butonuna basın.'), line=sso_state.line_id)
        except Exception as exc:
            partner.write({'logo_connection_state': 'error', 'logo_connection_error': str(exc)})
            return self._result(_('Logo Bağlantısı Tamamlanamadı'), str(exc), line=sso_state.line_id, error=True)

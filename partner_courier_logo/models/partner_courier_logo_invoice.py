import html
import json
import logging
import re
import secrets
from datetime import timedelta
from urllib import error as url_error
from urllib import request as url_request
from urllib.parse import urlencode

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .logo_http import LogoIPv4HTTPSHandler

_logger = logging.getLogger(__name__)

class LogoApiError(UserError):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        super().__init__(_('Logo API hatası (%s): %s') % (status_code, detail[:800]))


class PartnerCourierLogoInvoice(models.Model):
    _name = 'partner.courier.logo.invoice'
    _description = 'Courier Logo Invoice Draft'
    _order = 'create_date desc, id desc'

    line_id = fields.Many2one('partner.courier.accounting.line', required=True, ondelete='cascade', index=True)
    partner_id = fields.Many2one(related='line_id.partner_id', store=True, readonly=True, index=True)
    state = fields.Selection([
        ('draft', 'Hazırlık'), ('awaiting_connection', 'Logo Bağlantısı Bekliyor'),
        ('creating', 'Taslak Oluşturuluyor'), ('ready', 'Onay Bekliyor'),
        ('completed', 'Kesildi'), ('cancelled', 'Geri Alındı'), ('failed', 'Hatalı'),
    ], default='draft', required=True, copy=False, index=True)
    logo_invoice_id = fields.Char(string='Logo Fatura ID', readonly=True, copy=False)
    external_reference = fields.Char(string='Dış Referans', readonly=True, copy=False)
    request_payload = fields.Text(string='İstek Gövdesi', readonly=True, copy=False)
    response_payload = fields.Text(string='Logo Yanıtı', readonly=True, copy=False)
    error_message = fields.Text(string='Hata', readonly=True, copy=False)
    created_at = fields.Datetime(string='Taslak Tarihi', readonly=True, copy=False)
    cancelled_at = fields.Datetime(string='Geri Alma Tarihi', readonly=True, copy=False)
    logo_invoice_number = fields.Char(string='Logo Fatura Numarası', readonly=True, copy=False)
    logo_ettn = fields.Char(string='ETTN', readonly=True, copy=False)
    logo_status_code = fields.Integer(string='Logo Durum Kodu', readonly=True, copy=False)
    logo_status_text = fields.Char(string='Logo Durumu', readonly=True, copy=False)
    last_status_check_at = fields.Datetime(string='Son Durum Kontrolü', readonly=True, copy=False)

    _sql_constraints = [
        ('line_unique', 'unique(line_id)', 'Her hakediş için yalnızca bir Logo fatura talebi oluşturulabilir.'),
    ]

    @api.model
    def get_or_create_for_line(self, line):
        invoice = self.search([('line_id', '=', line.id)], limit=1)
        return invoice or self.create({'line_id': line.id})

    def _params(self):
        return self.env['ir.config_parameter'].sudo()

    def _setting(self, key, default=''):
        return (self._params().get_param('partner_courier_logo.%s' % key, default) or '').strip()

    def _url(self, endpoint, base_url=None):
        base_url = (base_url or self._setting('base_url')).rstrip('/')
        endpoint = (endpoint or '').strip()
        if not base_url or not endpoint:
            raise UserError(_('Logo API URL ayarlarını tamamlayın.'))
        return endpoint if endpoint.startswith('http') else '%s/%s' % (base_url, endpoint.lstrip('/'))

    @staticmethod
    def _http_error_detail(status_code, detail):
        """Turn proxy/WAF HTML pages into a safe, actionable portal message."""
        detail = detail or ''
        if status_code == 403 and (
            'cloudflare' in detail.lower()
            or 'you have been blocked' in detail.lower()
        ):
            plain_detail = re.sub(r'<[^>]+>', ' ', html.unescape(detail))
            plain_detail = re.sub(r'\s+', ' ', plain_detail).strip()
            ray_match = re.search(
                r'Cloudflare Ray ID:\s*([0-9a-f]+)', plain_detail, re.IGNORECASE)
            reference = ray_match.group(1) if ray_match else False
            message = _(
                'Logo İşbaşı güvenlik servisi bağlantıyı geçici olarak engelledi. '
                'Fatura oluşturulmadı. Lütfen Kuryetec destek ekibine bildirin ve '
                'daha sonra yeniden deneyin.'
            )
            if reference:
                message = _('%s Cloudflare referansı: %s') % (message, reference)
            return message
        return detail[:800]

    def _call_logo(self, method, endpoint, payload=None, headers=None, base_url=None):
        api_key = self._setting('api_key')
        if not api_key:
            raise UserError(_('Logo API Key ayarını doldurun.'))
        body = json.dumps(payload).encode('utf-8') if payload is not None else None
        request_headers = {
            'apiKey': api_key,
            'Accept': 'application/json',
            # Logo's Cloudflare layer rejects Python's default urllib signature.
            'User-Agent': 'Mozilla/5.0 (compatible; KuryetecLogoIntegration/1.0)',
        }
        if body:
            request_headers['Content-Type'] = 'application/json'
        request_headers.update(headers or {})
        url = self._url(endpoint, base_url=base_url)
        request_object = url_request.Request(
            url,
            data=body,
            headers=request_headers,
            method=method,
        )
        try:
            # Logo allows our IPv4 egress but still blocks the server's IPv6.
            opener = url_request.build_opener(LogoIPv4HTTPSHandler())
            with opener.open(request_object, timeout=30) as response:
                text = response.read().decode('utf-8')
        except url_error.HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='replace')
            safe_detail = self._http_error_detail(exc.code, detail)
            _logger.warning(
                'Logo API HTTP error %s for %s: %s',
                exc.code, url, safe_detail,
            )
            raise LogoApiError(exc.code, safe_detail) from exc
        except url_error.URLError as exc:
            raise UserError(_('Logo API bağlantısı kurulamadı: %s') % exc.reason) from exc
        try:
            return json.loads(text) if text else {}
        except ValueError as exc:
            raise UserError(_('Logo API geçerli JSON yanıtı döndürmedi.')) from exc

    @staticmethod
    def _data(response):
        return response.get('data', response) if isinstance(response, dict) else {}

    @staticmethod
    def _value(data, *names):
        if not isinstance(data, dict):
            return False
        for name in names:
            value = data.get(name)
            if value not in (None, ''):
                return value
        return False

    @staticmethod
    def _as_bool(value):
        return str(value or '').strip().lower() in ('1', 'true', 'yes', 'on')

    def _clear_logo_authentication(self):
        self._params().set_param('partner_courier_logo.access_token', '')
        self._params().set_param('partner_courier_logo.tenant_id', '')
        self._params().set_param('partner_courier_logo.user_id', '')
        self._params().set_param('partner_courier_logo.user_name', '')
        self._params().set_param('partner_courier_logo.api_base_url', '')

    def _supplier_tax_number(self):
        """Logo's courier API creates the draft for this invoice issuer."""
        self.ensure_one()
        return (self.partner_id.invoice_person_tc or self.partner_id.courier_tc or '').strip()

    def _get_logo_authentication(self, supplier_tax_number=False, force_refresh=False):
        login = self._setting('integration_login')
        password = self._setting('integration_password')
        if not login or not password:
            raise UserError(_('Logo İşbaşı hesap e-postası ve parolasını ayarlardan doldurun.'))

        login_payload = {
            'username': login,
            'password': password,
        }
        # Logo's courier integration selects the issuer through this value.
        # Do not reuse a token from another courier for invoice creation.
        if supplier_tax_number:
            login_payload['suplierTaxNumber'] = supplier_tax_number
            login_payload['childUserName'] = ''
        response = self._call_logo(
            'POST', self._setting('login_endpoint', '/api/v1.0/user/integrationLogin'), login_payload)
        data = self._data(response)
        if isinstance(response, dict) and response.get('isError'):
            raise UserError(response.get('message') or _('Logo İşbaşı giriş işlemi başarısız oldu.'))
        access_token = self._value(data, 'accessToken', 'access_token', 'token')
        tenant_id = self._value(data, 'tenantId', 'tenant_id')
        user_id = self._value(data, 'userId', 'user_id', 'id', 'UserId')
        user_name = self._value(data, 'userName', 'user_name', 'fullName', 'name', 'UserName') or login
        api_base_url = self._value(data, 'baseUrl', 'base_url') or self._setting('base_url')
        if not access_token or not tenant_id:
            raise UserError(_('Logo giriş yanıtında accessToken veya tenantId bulunamadı.'))
        if not supplier_tax_number:
            self._params().set_param('partner_courier_logo.access_token', str(access_token))
            self._params().set_param('partner_courier_logo.tenant_id', str(tenant_id))
            self._params().set_param('partner_courier_logo.user_id', str(user_id or ''))
            self._params().set_param('partner_courier_logo.user_name', str(user_name))
            self._params().set_param('partner_courier_logo.api_base_url', str(api_base_url))
        return {
            'access_token': str(access_token),
            'tenant_id': str(tenant_id),
            'user_id': str(user_id or ''),
            'user_email': login,
            'user_name': str(user_name),
            'api_base_url': str(api_base_url),
        }

    def _invoice_headers(self, authentication):
        headers = {
            # Logo support explicitly requires the raw token for this service.
            'Authorization': authentication['access_token'],
            'tenantId': authentication['tenant_id'],
            'lang': 'tr-TR',
            'UserEmail': authentication['user_email'],
        }
        if authentication['user_id']:
            headers['UserId'] = authentication['user_id']
        return headers

    def _buyer(self):
        """Build the buyer shown in the courier's outgoing invoice."""
        required = {
            'code': self._setting('buyer_code'),
            'name': self._setting('buyer_name'),
            'tcknVkn': self._setting('buyer_vkn'),
            'taxOffice': self._setting('buyer_tax_office'),
            'country': self._setting('buyer_country', 'TÜRKİYE'),
            'postalCode': self._setting('buyer_postal_code'),
            'city': self._setting('buyer_city'),
            'district': self._setting('buyer_district'),
            'address': self._setting('buyer_address'),
            'phone': self._setting('buyer_phone'),
        }
        missing = [label for label, value in required.items() if not value]
        if missing:
            raise UserError(_(
                'Logo fatura alıcı ayarlarında şu alanları doldurun: %s'
            ) % ', '.join(missing))
        required.update({'isPerson': False})
        return required

    @staticmethod
    def _invoice_date_for_period_end(period_end):
        """Use the next day unless it would move the invoice to another month."""
        if not period_end:
            raise ValidationError(_('Fatura oluşturmak için hakediş bitiş tarihi gerekir.'))
        next_day = period_end + timedelta(days=1)
        changes_month = (
            next_day.year != period_end.year
            or next_day.month != period_end.month
        )
        return period_end if changes_month else next_day

    def _invoice_date(self):
        self.ensure_one()
        return self._invoice_date_for_period_end(self.line_id.date_end)

    def _payload(self):
        self.ensure_one()
        line = self.line_id
        base = line.bonus_included_total_payment_tax_excluded or line.total_payment_tax_excluded or line.earning_amount_tax_excluded
        if base <= 0:
            raise ValidationError(_('Fatura oluşturmak için KDV hariç pozitif hakediş tutarı gerekir.'))
        has_withholding = base > 10000
        supplier_tax_number = self._supplier_tax_number()
        if not supplier_tax_number:
            raise ValidationError(_(
                'Fatura oluşturmak için kurye contactında Fatura Kesecek Kişi T.C. No veya Kurye T.C. No girilmelidir.'
            ))
        customer = self._buyer()
        service_code = 'Hizmet 110' if has_withholding else 'Hizmet 101'
        product = {
            'itemCode': service_code,
            'itemType': 2,
            'name': 'Kurye Hizmet Bedeli',
            'vat': 20,
            'unit': 'ADET',
        }
        description = '%s - %s Hakediş Haftası' % (
            fields.Date.to_string(line.date_start), fields.Date.to_string(line.date_end))
        detail = {
            'quantity': 1,
            'price': base,
            'taxRate': 20,
            'description': description,
            'discountRate': 0,
            'discountValue': 0,
            'productDetail': product,
        }
        if has_withholding:
            withholding = {
                'code': '624',
                'rateText': '2/10',
            }
            product['withholding'] = withholding
        return {
            'invoiceId': 0,
            'invoiceDate': '%s 00:00:00' % fields.Date.to_string(self._invoice_date()),
            'currency': 'TL',
            'exchangeRate': 1,
            'vatIncluded': False,
            'description': description,
            'customer': customer,
            'salesInvoiceDetails': [detail],
            # The value is consumed only by _send_to_logo while opening the
            # courier-specific integration session; it is not sent as invoice data.
            '_supplier_tax_number': supplier_tax_number,
        }

    def _send_to_logo(self, payload):
        payload = dict(payload)
        supplier_tax_number = payload.pop('_supplier_tax_number', False)
        authentication = self._get_logo_authentication(supplier_tax_number=supplier_tax_number)
        try:
            return self._call_logo(
                'POST',
                self._setting('invoice_endpoint'),
                payload,
                self._invoice_headers(authentication),
                base_url=authentication['api_base_url'],
            )
        except LogoApiError as exc:
            if exc.status_code != 401:
                raise
            self._clear_logo_authentication()
            authentication = self._get_logo_authentication(
                supplier_tax_number=supplier_tax_number, force_refresh=True)
            return self._call_logo(
                'POST',
                self._setting('invoice_endpoint'),
                payload,
                self._invoice_headers(authentication),
                base_url=authentication['api_base_url'],
            )

    def _delete_from_logo(self):
        self.ensure_one()
        if not self.logo_invoice_id:
            raise UserError(_('Logo fatura kimliği bulunmadığı için taslak geri alınamaz.'))
        supplier_tax_number = self._supplier_tax_number()
        authentication = self._get_logo_authentication(supplier_tax_number=supplier_tax_number)
        endpoint = '/api/v1.0/invoices/deleteInvoice?%s' % urlencode({'Ids': self.logo_invoice_id})
        try:
            return self._call_logo(
                'DELETE', endpoint, headers=self._invoice_headers(authentication),
                base_url=authentication['api_base_url'])
        except LogoApiError as exc:
            if exc.status_code != 401:
                raise
            authentication = self._get_logo_authentication(
                supplier_tax_number=supplier_tax_number, force_refresh=True)
            return self._call_logo(
                'DELETE', endpoint, headers=self._invoice_headers(authentication),
                base_url=authentication['api_base_url'])

    def _read_logo_invoice(self, authentication=None):
        self.ensure_one()
        if not self.logo_invoice_id:
            raise UserError(_('Logo fatura kimliği bulunmadığı için fatura durumu sorgulanamaz.'))
        supplier_tax_number = self._supplier_tax_number()
        authentication = authentication or self._get_logo_authentication(
            supplier_tax_number=supplier_tax_number)
        endpoint = '/api/v1.0/invoices/%s' % self.logo_invoice_id
        try:
            return self._call_logo(
                'GET', endpoint, headers=self._invoice_headers(authentication),
                base_url=authentication['api_base_url'])
        except LogoApiError as exc:
            if exc.status_code != 401:
                raise
            authentication = self._get_logo_authentication(
                supplier_tax_number=supplier_tax_number, force_refresh=True)
            return self._call_logo(
                'GET', endpoint, headers=self._invoice_headers(authentication),
                base_url=authentication['api_base_url'])

    @staticmethod
    def _logo_status_values(data):
        e_government = data.get('eGovernmentInvoice') or {}
        accounting_status = data.get('accountingStatus') or {}
        status_code = e_government.get('eStatus')
        try:
            status_code = int(status_code) if status_code is not None else 0
        except (TypeError, ValueError):
            status_code = 0
        status_text = (
            accounting_status.get('statusText')
            or e_government.get('appResponseDescription')
            or e_government.get('description')
            or ('Logo durum kodu: %s' % status_code if status_code else False)
        )
        return {
            'logo_invoice_number': data.get('invoiceNumber') or False,
            'logo_ettn': data.get('guid') or data.get('uuid') or False,
            'logo_status_code': status_code,
            'logo_status_text': status_text,
            'last_status_check_at': fields.Datetime.now(),
        }

    @staticmethod
    def _is_logo_invoice_completed(data, status_code):
        """Recognize Logo's successful send state across its API variants."""
        e_government = data.get('eGovernmentInvoice') or {}
        description = (e_government.get('description') or '').strip().upper()
        return status_code == 10 or (
            e_government.get('isSended')
            and 'BAŞARIYLA TAMAMLANDI' in description
        )

    def _sync_logo_status(self, authentication=None):
        """Synchronize one draft using its Logo ID without touching invoice data."""
        self.ensure_one()
        response = self._read_logo_invoice(authentication=authentication)
        if isinstance(response, dict) and response.get('isError'):
            raise UserError(response.get('message') or _('Logo fatura durumu alınamadı.'))
        data = self._data(response)
        if not isinstance(data, dict):
            raise UserError(_('Logo fatura durumu geçerli bir kayıt olarak dönmedi.'))
        values = self._logo_status_values(data)
        if data.get('isCancelled'):
            values['state'] = 'cancelled'
            values['cancelled_at'] = fields.Datetime.now()
        elif self._is_logo_invoice_completed(data, values['logo_status_code']):
            values['state'] = 'completed'
            values['logo_status_text'] = (
                (data.get('eGovernmentInvoice') or {}).get('description')
                or values['logo_status_text']
            )
        self.write(values)
        return values

    def action_sync_logo_status(self):
        if not self.env.user.has_group('partner_courier_accounting.group_partner_courier_accounting_admin'):
            raise UserError(_('Bu işlem yalnızca kurye muhasebe yöneticileri tarafından yapılabilir.'))
        for invoice in self.filtered(lambda record: record.state == 'ready'):
            invoice._sync_logo_status()
        return True

    def _status_check_interval_minutes(self):
        """Use a fast first check without consuming the Logo read quota indefinitely."""
        self.ensure_one()
        reference = self.created_at or self.create_date or fields.Datetime.now()
        age = fields.Datetime.now() - reference
        if age <= timedelta(hours=3):
            return 10
        if age <= timedelta(days=1):
            return 30
        return 120

    @api.model
    def _consume_status_sync_quota(self):
        """Reserve one of the 90 daily Logo reads (2,700/month maximum)."""
        parameter = self._params()
        today = fields.Date.to_string(fields.Date.today())
        stored = parameter.get_param('partner_courier_logo.status_sync_daily_usage', '')
        stored_date, separator, stored_count = stored.partition(':')
        try:
            used = int(stored_count) if separator and stored_date == today else 0
        except ValueError:
            used = 0
        if used >= 90:
            return False
        parameter.set_param('partner_courier_logo.status_sync_daily_usage', '%s:%s' % (today, used + 1))
        return True

    @api.model
    def cron_sync_logo_invoice_status(self):
        """Quota-aware status sync, scheduled every 10 minutes."""
        if not self._as_bool(self._setting('enabled')):
            return True
        invoices = self.sudo().search([
            ('state', '=', 'ready'), ('logo_invoice_id', '!=', False),
            ('logo_invoice_id', 'not ilike', 'TEST-%'),
        ], order='created_at desc, id desc', limit=20)
        authentications = {}
        for invoice in invoices:
            last_check = invoice.last_status_check_at
            if last_check:
                elapsed_minutes = (fields.Datetime.now() - last_check).total_seconds() / 60
                if elapsed_minutes < invoice._status_check_interval_minutes():
                    continue
            if not self._consume_status_sync_quota():
                _logger.info('Logo invoice status sync stopped: daily read quota reserved.')
                break
            try:
                supplier_tax_number = invoice._supplier_tax_number()
                authentication = authentications.get(supplier_tax_number)
                if not authentication:
                    authentication = invoice._get_logo_authentication(
                        supplier_tax_number=supplier_tax_number)
                    authentications[supplier_tax_number] = authentication
                invoice._sync_logo_status(authentication=authentication)
            except Exception as exc:
                invoice.write({
                    'last_status_check_at': fields.Datetime.now(),
                    'logo_status_text': _('Durum sorgusu yapılamadı: %s') % str(exc)[:240],
                })
                _logger.warning('Logo status sync failed for courier invoice %s: %s', invoice.id, exc)
        return True

    def action_cancel_logo_draft(self):
        if not self.env.user.has_group('partner_courier_accounting.group_partner_courier_accounting_admin'):
            raise UserError(_('Bu işlem yalnızca kurye muhasebe yöneticileri tarafından yapılabilir.'))
        for invoice in self:
            if invoice.state != 'ready':
                raise UserError(_('Yalnızca Logo tarafında onay bekleyen taslak faturalar geri alınabilir.'))
            if self._as_bool(self._setting('test_mode')):
                response = {'test_mode': True, 'message': 'Yerel Logo taslağı geri alındı.'}
            else:
                if self._setting('enabled').lower() != 'true':
                    raise UserError(_('Logo İşbaşı entegrasyonunu Ayarlar ekranından etkinleştirin.'))
                response = invoice._delete_from_logo()
                if isinstance(response, dict) and response.get('isError'):
                    raise UserError(response.get('message') or _('Logo taslağı geri alınamadı.'))
            invoice.write({
                'state': 'cancelled',
                'cancelled_at': fields.Datetime.now(),
                'error_message': False,
                'response_payload': json.dumps(response, ensure_ascii=False),
            })
        return True

    def action_create_draft(self):
        for invoice in self:
            if invoice.state in ('ready', 'completed'):
                continue
            if invoice.state == 'creating':
                raise UserError(_('Bu hakediş için fatura taslağı zaten oluşturuluyor. Lütfen bekleyin.'))
            invoice.line_id._check_logo_invoice_order()
            if self._as_bool(self._setting('test_mode')):
                payload = invoice._payload()
                stored_payload = dict(payload)
                stored_payload.pop('_supplier_tax_number', None)
                invoice.write({
                    'state': 'ready',
                    'logo_invoice_id': 'TEST-%s' % invoice.id,
                    'external_reference': 'KURYE-HAKEDIS-%s' % invoice.line_id.id,
                    'request_payload': json.dumps(stored_payload, ensure_ascii=False),
                    'response_payload': json.dumps({'test_mode': True, 'message': 'Yerel taslak oluşturuldu.'}, ensure_ascii=False),
                    'created_at': fields.Datetime.now(), 'error_message': False,
                })
                continue
            if self._setting('enabled').lower() != 'true':
                raise UserError(_('Logo İşbaşı entegrasyonunu Ayarlar ekranından etkinleştirin.'))
            payload = invoice._payload()
            stored_payload = dict(payload)
            stored_payload.pop('_supplier_tax_number', None)
            invoice.write({'state': 'creating', 'request_payload': json.dumps(stored_payload, ensure_ascii=False)})
            try:
                response = invoice._send_to_logo(payload)
            except Exception as exc:
                invoice.write({
                    'state': 'failed',
                    'error_message': str(exc),
                })
                raise
            data = invoice._data(response)
            logo_invoice_id = invoice._value(data, 'invoiceId', 'id')
            if (isinstance(response, dict) and response.get('isError')):
                message = response.get('message', _('Logo faturayı oluşturmadı.')) if isinstance(response, dict) else _('Logo faturayı oluşturmadı.')
                invoice.write({'state': 'failed', 'response_payload': json.dumps(response, ensure_ascii=False), 'error_message': message})
                raise UserError(message)
            invoice.write({'state': 'ready', 'logo_invoice_id': str(logo_invoice_id or ''),
                           'external_reference': 'KURYE-HAKEDIS-%s' % invoice.line_id.id,
                           'response_payload': json.dumps(response, ensure_ascii=False),
                           'created_at': fields.Datetime.now(), 'error_message': False})
        return True


class PartnerCourierLogoSsoState(models.Model):
    _name = 'partner.courier.logo.sso.state'
    _description = 'Courier Logo SSO State'
    _order = 'create_date desc'

    token = fields.Char(required=True, readonly=True, index=True, copy=False)
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', index=True)
    line_id = fields.Many2one('partner.courier.accounting.line', required=True, ondelete='cascade')
    expires_at = fields.Datetime(required=True, readonly=True)
    used = fields.Boolean(default=False, readonly=True)

    _sql_constraints = [('token_unique', 'unique(token)', 'SSO durum anahtarı benzersiz olmalıdır.')]

    @api.model
    def create_for(self, partner, line):
        return self.create({'token': secrets.token_urlsafe(32), 'partner_id': partner.id, 'line_id': line.id,
                            'expires_at': fields.Datetime.now() + timedelta(minutes=10)})

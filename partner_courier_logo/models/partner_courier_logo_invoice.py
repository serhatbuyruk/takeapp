import json
import logging
import secrets
from datetime import timedelta
from urllib import error as url_error
from urllib import request as url_request

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PartnerCourierLogoInvoice(models.Model):
    _name = 'partner.courier.logo.invoice'
    _description = 'Courier Logo Invoice Draft'
    _order = 'create_date desc, id desc'

    line_id = fields.Many2one('partner.courier.accounting.line', required=True, ondelete='cascade', index=True)
    partner_id = fields.Many2one(related='line_id.partner_id', store=True, readonly=True, index=True)
    state = fields.Selection([
        ('draft', 'Hazırlık'), ('awaiting_connection', 'Logo Bağlantısı Bekliyor'),
        ('creating', 'Taslak Oluşturuluyor'), ('ready', 'Onay Bekliyor'),
        ('completed', 'Kesildi'), ('failed', 'Hatalı'),
    ], default='draft', required=True, copy=False, index=True)
    logo_invoice_id = fields.Char(string='Logo Fatura ID', readonly=True, copy=False)
    external_reference = fields.Char(string='Dış Referans', readonly=True, copy=False)
    request_payload = fields.Text(string='İstek Gövdesi', readonly=True, copy=False, groups='base.group_system')
    response_payload = fields.Text(string='Logo Yanıtı', readonly=True, copy=False, groups='base.group_system')
    error_message = fields.Text(string='Hata', readonly=True, copy=False)
    created_at = fields.Datetime(string='Taslak Tarihi', readonly=True, copy=False)

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

    def _url(self, endpoint):
        base_url = self._setting('base_url').rstrip('/')
        endpoint = (endpoint or '').strip()
        if not base_url or not endpoint:
            raise UserError(_('Logo API URL ayarlarını tamamlayın.'))
        return endpoint if endpoint.startswith('http') else '%s/%s' % (base_url, endpoint.lstrip('/'))

    def _call_logo(self, method, endpoint, payload=None, headers=None):
        api_key = self._setting('api_key')
        if not api_key:
            raise UserError(_('Logo API Key ayarını doldurun.'))
        body = json.dumps(payload).encode('utf-8') if payload is not None else None
        request_headers = {'apiKey': api_key, 'Accept': 'application/json'}
        if body:
            request_headers['Content-Type'] = 'application/json'
        request_headers.update(headers or {})
        request_object = url_request.Request(self._url(endpoint), data=body, headers=request_headers, method=method)
        try:
            with url_request.urlopen(request_object, timeout=30) as response:
                text = response.read().decode('utf-8')
        except url_error.HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='replace')
            raise UserError(_('Logo API hatası (%s): %s') % (exc.code, detail[:800])) from exc
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

    def _payload(self, test_mode=False):
        self.ensure_one()
        line = self.line_id
        base = line.bonus_included_total_payment_tax_excluded or line.total_payment_tax_excluded or line.earning_amount_tax_excluded
        if base <= 0:
            raise ValidationError(_('Fatura oluşturmak için KDV hariç pozitif hakediş tutarı gerekir.'))
        has_withholding = base > 10000
        partner = line.partner_id
        customer = {
            'code': '', 'isPerson': False, 'name': self._setting('buyer_name'),
            'tcknVkn': self._setting('buyer_vkn'), 'taxOffice': self._setting('buyer_tax_office'),
        }
        if test_mode:
            customer.update({
                'name': customer['name'] or 'Kuryetec Test',
                'tcknVkn': customer['tcknVkn'] or '1111111111',
                'taxOffice': customer['taxOffice'] or 'Test Vergi Dairesi',
            })
        if not all((customer['name'], customer['tcknVkn'], customer['taxOffice'])):
            raise UserError(_('Logo alıcı firma ayarlarını tamamlayın.'))
        product = {'itemCode': 'Hizmet 110' if has_withholding else 'Hizmet 101',
                   'name': 'Kurye Hizmet Bedeli', 'vat': 20, 'unit': 'Adet'}
        if has_withholding:
            product['withholding'] = {'code': '624', 'description': 'Yük Taşımacılığı Hizmeti', 'rate': 0.20}
        description = '%s - %s Hakediş Haftası' % (
            fields.Date.to_string(line.date_start), fields.Date.to_string(line.date_end))
        return {
            'invoiceId': 0, 'invoiceDate': fields.Datetime.to_string(fields.Datetime.now()),
            'currency': 'TL', 'exchangeRate': 1, 'vatIncluded': False,
            'accountingStatus': {'status': 'Draft'},
            'description': description, 'customer': customer,
            'salesInvoiceDetails': [{'quantity': 1, 'price': base, 'taxRate': 20,
                                     'description': description, 'productDetail': product}],
        }

    def action_create_draft(self):
        for invoice in self:
            if invoice.state in ('ready', 'completed'):
                continue
            if self._setting('test_mode').lower() == 'true':
                payload = invoice._payload(test_mode=True)
                invoice.write({
                    'state': 'ready',
                    'logo_invoice_id': 'TEST-%s' % invoice.id,
                    'external_reference': 'KURYE-HAKEDIS-%s' % invoice.line_id.id,
                    'request_payload': json.dumps(payload, ensure_ascii=False),
                    'response_payload': json.dumps({'test_mode': True, 'message': 'Yerel taslak oluşturuldu.'}, ensure_ascii=False),
                    'created_at': fields.Datetime.now(), 'error_message': False,
                })
                continue
            if self._setting('enabled').lower() != 'true':
                raise UserError(_('Logo İşbaşı entegrasyonunu Ayarlar ekranından etkinleştirin.'))
            partner = invoice.partner_id
            if partner.logo_connection_state != 'connected' or not partner.logo_access_token or not partner.logo_tenant_id:
                invoice.write({'state': 'awaiting_connection'})
                raise UserError(_('Kurye Logo İşbaşı hesabını henüz bağlamamış.'))
            payload = invoice._payload()
            invoice.write({'state': 'creating', 'request_payload': json.dumps(payload, ensure_ascii=False)})
            response = invoice._call_logo('POST', invoice._setting('invoice_endpoint'), payload, {
                'Authorization': 'Bearer %s' % partner.logo_access_token,
                'tenantId': partner.logo_tenant_id, 'lang': 'tr-TR',
            })
            data = invoice._data(response)
            logo_invoice_id = invoice._value(data, 'invoiceId', 'id')
            if (isinstance(response, dict) and response.get('isError')) or not logo_invoice_id:
                message = response.get('message', _('Logo taslak fatura oluşturmadı.')) if isinstance(response, dict) else _('Logo taslak fatura oluşturmadı.')
                invoice.write({'state': 'failed', 'response_payload': json.dumps(response, ensure_ascii=False), 'error_message': message})
                raise UserError(message)
            invoice.write({'state': 'ready', 'logo_invoice_id': str(logo_invoice_id),
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

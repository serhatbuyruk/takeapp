import json
import re
import uuid
import base64
from urllib import error as url_error
from urllib import request as url_request

from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import service_account

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class PartnerCourierNotification(models.Model):
    _name = 'partner.courier.notification'
    _description = 'Courier Push Notification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(string='Başlık', required=True, tracking=True)
    message = fields.Text(string='Mesaj', required=True, tracking=True)
    provider = fields.Selection(
        [('onesignal', 'OneSignal'), ('firebase', 'Firebase Cloud Messaging')],
        string='Bildirim Servisi', required=True, default=lambda self: self._default_provider(),
        readonly=True, states={'draft': [('readonly', False)]}, tracking=True,
    )
    target_type = fields.Selection([
        ('all', 'Bildirim cihazı olan tüm kuryeler'), ('partners', 'Seçili kişiler'),
        ('domain', 'Contact filtresi'),
    ], string='Hedef', default='all', required=True, tracking=True)
    partner_ids = fields.Many2many(
        'res.partner', 'partner_courier_notification_res_partner_rel', 'notification_id', 'partner_id',
        string='Kişiler', domain="[('courier_id', '!=', False)]",
    )
    courier_ids_text = fields.Text(string='Kurye ID Listesi', copy=False,
        help='Her satıra bir Kurye ID yapıştırıp seçili kişiler listesine ekleyebilirsiniz.')
    partner_domain = fields.Char(string='Contact Filtresi', default='[]',
        help='res.partner üzerinde uygulanacak Odoo domain filtresi.')
    image_url = fields.Char(string='Bildirim Görsel URL')
    launch_url = fields.Char(string='Açılacak URL')
    additional_data_json = fields.Text(string='Ek Veri JSON',
        help='Mobil uygulamaya iletilecek opsiyonel ek data.')
    state = fields.Selection([
        ('draft', 'Taslak'), ('sent', 'Gönderildi'), ('failed', 'Hatalı'),
    ], string='Durum', default='draft', readonly=True, tracking=True)
    recipient_line_ids = fields.One2many('partner.courier.notification.recipient', 'notification_id',
        string='Alıcılar', readonly=True, copy=False)
    recipient_count = fields.Integer(string='Alıcı Sayısı', compute='_compute_counts', store=True)
    sent_count = fields.Integer(string='Gönderilen', compute='_compute_counts', store=True)
    skipped_count = fields.Integer(string='Atlanan', compute='_compute_counts', store=True)
    failed_count = fields.Integer(string='Hatalı', compute='_compute_counts', store=True)
    onesignal_notification_id = fields.Char(string='OneSignal Bildirim ID', readonly=True, copy=False)
    provider_message_id = fields.Char(string='Servis Bildirim ID', readonly=True, copy=False)
    sent_date = fields.Datetime(string='Gönderim Tarihi', readonly=True, copy=False)
    response_message = fields.Text(string='Servis Yanıtı', readonly=True, copy=False)

    _ONESIGNAL_SUBSCRIPTION_ID_PATTERN = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

    @api.model
    def _default_provider(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'partner_courier_notification.provider', 'onesignal') or 'onesignal'

    @api.depends('recipient_line_ids.state')
    def _compute_counts(self):
        for notification in self:
            lines = notification.recipient_line_ids
            notification.recipient_count = len(lines)
            notification.sent_count = len(lines.filtered(lambda line: line.state == 'sent'))
            notification.skipped_count = len(lines.filtered(lambda line: line.state == 'skipped'))
            notification.failed_count = len(lines.filtered(lambda line: line.state == 'failed'))

    @api.constrains('additional_data_json')
    def _check_additional_data_json(self):
        for notification in self.filtered('additional_data_json'):
            try:
                data = json.loads(notification.additional_data_json)
            except ValueError as exc:
                raise ValidationError(_('Ek Veri JSON geçerli değil: %s') % exc) from exc
            if not isinstance(data, dict):
                raise ValidationError(_('Ek Veri JSON bir obje olmalıdır. Örnek: {"screen": "home"}'))

    def action_reset_to_draft(self):
        self.write({'state': 'draft', 'onesignal_notification_id': False, 'provider_message_id': False,
                    'sent_date': False, 'response_message': False})
        self.mapped('recipient_line_ids').unlink()

    def action_send(self):
        for notification in self:
            notification._send_notification()
        return True

    def action_add_partners_by_courier_ids(self):
        self.ensure_one()
        if self.state == 'sent':
            raise UserError(_('Gönderilmiş bildirimin hedef kişileri değiştirilemez.'))
        courier_ids = self._parse_courier_ids_text()
        if not courier_ids:
            raise UserError(_('Lütfen en az bir Kurye ID girin.'))
        partners = self.env['res.partner'].search([('active', '=', True), ('courier_id', 'in', courier_ids)])
        found = set(partners.mapped('courier_id'))
        missing = [courier_id for courier_id in courier_ids if courier_id not in found]
        if not partners:
            raise UserError(_('Girilen Kurye ID değerleriyle eşleşen aktif contact bulunamadı.'))
        existing = self.partner_ids
        self.write({'target_type': 'partners', 'partner_ids': [(6, 0, (existing | partners).ids)],
                    'courier_ids_text': False})
        message = _('%s kişi seçili kişiler listesine eklendi.') % len(partners - existing)
        if missing:
            message += _(' Bulunamayan Kurye ID: %s') % ', '.join(missing)
        return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {
            'title': _('Kurye ID Listesi'), 'message': message,
            'type': 'warning' if missing else 'success', 'sticky': bool(missing),
            'next': {'type': 'ir.actions.client', 'tag': 'reload'},
        }}

    def _parse_courier_ids_text(self):
        self.ensure_one()
        values, seen = [], set()
        for value in re.split(r'[\s,;]+', self.courier_ids_text or ''):
            courier_id = value.strip()
            if courier_id and courier_id not in seen:
                values.append(courier_id)
                seen.add(courier_id)
        return values

    def _send_notification(self):
        self.ensure_one()
        if self.state == 'sent':
            raise UserError(_('Bu bildirim zaten gönderilmiş. Tekrar göndermek için taslağa alın.'))
        partners = self._get_target_partners()
        if not partners:
            raise UserError(_('Gönderilecek kurye bulunamadı.'))
        self.recipient_line_ids.unlink()
        lines = []
        for partner in partners:
            token = self._partner_device_token(partner, self.provider)
            valid = self._is_valid_device_token(token, self.provider)
            lines.append((0, 0, {'partner_id': partner.id, 'provider': self.provider,
                'device_token': token, 'player_id': token if self.provider == 'onesignal' else False,
                'state': 'sent' if valid else 'skipped',
                'error_message': False if valid else _('Geçerli cihaz tokenı bulunamadı.')}))
        self.write({'recipient_line_ids': lines})
        valid_lines = self.recipient_line_ids.filtered(lambda line: line.state == 'sent')
        if not valid_lines:
            self.write({'state': 'failed', 'response_message': _('Seçilen kişilerde geçerli cihaz tokenı bulunamadı.')})
            raise UserError(_('Seçilen kişilerde geçerli cihaz tokenı bulunamadı.'))
        if self.provider == 'firebase':
            return self._send_firebase(valid_lines)
        return self._send_onesignal(valid_lines)

    def _send_onesignal(self, valid_lines):
        app_id, api_key = self._get_onesignal_settings()
        responses, invalid_tokens = [], set()
        try:
            for chunk in self._split_every(valid_lines.mapped('device_token'), 20000):
                response = self._call_onesignal(api_key, self._prepare_onesignal_payload(app_id, chunk))
                responses.append(response)
                invalid_tokens.update(response.get('errors', {}).get('invalid_player_ids') or [])
        except UserError as exc:
            valid_lines.write({'state': 'failed', 'error_message': str(exc)})
            raise
        failed = valid_lines.filtered(lambda line: line.device_token in invalid_tokens)
        failed.write({'state': 'failed', 'error_message': _('OneSignal invalid_player_ids içinde döndü.')})
        sent = valid_lines - failed
        ids = [response.get('id') for response in responses if response.get('id')]
        sent.write({'onesignal_notification_id': ','.join(ids), 'provider_message_id': ','.join(ids)})
        self.write({'state': 'sent' if ids else 'failed', 'onesignal_notification_id': ','.join(ids),
                    'provider_message_id': ','.join(ids), 'sent_date': fields.Datetime.now(),
                    'response_message': json.dumps(responses, ensure_ascii=False, indent=2)})
        return responses

    def _send_firebase(self, valid_lines):
        project_id, credentials = self._get_firebase_credentials()
        endpoint = 'https://fcm.googleapis.com/v1/projects/%s/messages:send' % project_id
        access_token = credentials.token
        responses, failed = [], self.env['partner.courier.notification.recipient']
        for line in valid_lines:
            try:
                response = self._call_firebase(endpoint, access_token, self._prepare_firebase_payload(line.device_token))
                responses.append({'partner_id': line.partner_id.id, 'response': response})
                line.write({'provider_message_id': response.get('name')})
            except UserError as exc:
                failed |= line
                line.write({'state': 'failed', 'error_message': str(exc)})
                responses.append({'partner_id': line.partner_id.id, 'error': str(exc)})
                if 'UNREGISTERED' in str(exc) and line.partner_id.firebase_token == line.device_token:
                    line.partner_id.sudo().write({'firebase_token': False, 'firebase_token_updated_at': False})
        sent = valid_lines - failed
        message_ids = sent.mapped('provider_message_id')
        self.write({'state': 'sent' if sent else 'failed', 'provider_message_id': ','.join(message_ids),
                    'sent_date': fields.Datetime.now(),
                    'response_message': json.dumps(responses, ensure_ascii=False, indent=2)})
        if not sent:
            raise UserError(_('Firebase hiçbir alıcıya bildirimi teslim edemedi.'))
        return responses

    def _get_target_partners(self):
        self.ensure_one()
        base_domain = [('active', '=', True), ('courier_id', '!=', False)]
        if self.target_type == 'all':
            token_field = 'firebase_token' if self.provider == 'firebase' else 'player_id'
            return self.env['res.partner'].search(expression.AND([base_domain, [(token_field, '!=', False)]]))
        if self.target_type == 'partners':
            return self.partner_ids
        return self.env['res.partner'].search(expression.AND([base_domain, self._parse_partner_domain()]))

    def _parse_partner_domain(self):
        try:
            domain = safe_eval((self.partner_domain or '[]').strip())
        except Exception as exc:
            raise UserError(_('Contact filtresi geçerli bir domain değil: %s') % exc) from exc
        if not isinstance(domain, (list, tuple)):
            raise UserError(_('Contact filtresi liste formatında olmalıdır.'))
        return list(domain)

    def _partner_device_token(self, partner, provider):
        token = partner.firebase_token if provider == 'firebase' else partner.player_id
        return (token or '').strip()

    def _partner_has_push_target(self, partner, provider=None):
        provider = provider or self._default_provider()
        return self._is_valid_device_token(self._partner_device_token(partner, provider), provider)

    def _is_valid_device_token(self, token, provider):
        if provider == 'onesignal':
            return bool(token and self._ONESIGNAL_SUBSCRIPTION_ID_PATTERN.match(token))
        return bool(token and len(token) >= 20 and len(token) <= 4096 and not re.search(r'\s', token))

    def _get_onesignal_settings(self):
        params = self.env['ir.config_parameter'].sudo()
        app_id = (params.get_param('partner_courier_notification.onesignal_app_id') or '').strip()
        api_key = (params.get_param('partner_courier_notification.onesignal_api_key') or '').strip()
        if not app_id or not api_key:
            raise UserError(_('OneSignal App ID ve API Key ayarlarını doldurun.'))
        return app_id, api_key

    def _get_firebase_credentials(self):
        params = self.env['ir.config_parameter'].sudo()
        project_id = (params.get_param('partner_courier_notification.firebase_project_id') or '').strip()
        attachment_id = params.get_param('partner_courier_notification.firebase_service_account_attachment_id')
        attachment = self.env['ir.attachment'].sudo().browse(int(attachment_id or 0)).exists()
        if not project_id or not attachment or not attachment.datas:
            raise UserError(_('Firebase proje ID ve servis hesabı JSON dosyasını ayarlayın.'))
        try:
            raw_data = base64.b64decode(attachment.datas)
            credentials = service_account.Credentials.from_service_account_info(
                json.loads(raw_data.decode('utf-8')),
                scopes=['https://www.googleapis.com/auth/firebase.messaging'],
            )
            credentials.refresh(GoogleAuthRequest())
        except Exception as exc:
            raise UserError(_('Firebase servis hesabı doğrulanamadı: %s') % exc) from exc
        return project_id, credentials

    def _prepare_onesignal_payload(self, app_id, subscription_ids):
        payload = {'app_id': app_id, 'include_subscription_ids': subscription_ids,
                   'headings': {'en': self.name, 'tr': self.name},
                   'contents': {'en': self.message, 'tr': self.message}, 'idempotency_key': str(uuid.uuid4())}
        if self.launch_url:
            payload['app_url'] = self.launch_url
        if self.image_url:
            payload['big_picture'] = self.image_url
            payload['ios_attachments'] = {'image': self.image_url}
        if self.additional_data_json:
            payload['data'] = json.loads(self.additional_data_json)
        return payload

    def _prepare_firebase_payload(self, token):
        data = {'launch_url': self.launch_url or ''}
        additional_data = {}
        if self.additional_data_json:
            additional_data = json.loads(self.additional_data_json)
            for key, value in additional_data.items():
                data[str(key)] = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)

        notification = {'title': self.name, 'body': self.message}
        if self.image_url:
            notification['image'] = self.image_url

        actions = additional_data.get('notification_actions')
        if isinstance(actions, list) and actions:
            # Android must receive this as a data message so the mobile app can
            # render its own answer/reject action buttons. iOS uses a fixed APNs
            # category registered by the app, while retaining the same data.
            data['notification_type'] = 'courier_call'
            data['android_notification_mode'] = 'local'
            data['title'] = str(self.name or '')
            data['body'] = str(self.message or '')
            return {'message': {
                'token': token,
                'data': data,
                'android': {'priority': 'high'},
                'apns': {
                    'headers': {
                        'apns-priority': '10',
                        'apns-push-type': 'alert',
                    },
                    'payload': {'aps': {
                        'alert': notification,
                        'sound': 'courier_call_ring.wav',
                        'category': 'COURIER_CALL',
                    }},
                },
            }}

        return {'message': {'token': token, 'notification': notification, 'data': data,
                'android': {'priority': 'high'}, 'apns': {'payload': {'aps': {'sound': 'default'}}}}}

    def _split_every(self, values, size):
        for index in range(0, len(values), size):
            yield values[index:index + size]

    def _call_onesignal(self, api_key, payload):
        return self._call_json('https://onesignal.com/api/v1/notifications', payload, {
            'Authorization': 'Key %s' % api_key,
        }, 'OneSignal')

    def _call_firebase(self, endpoint, access_token, payload):
        return self._call_json(endpoint, payload, {'Authorization': 'Bearer %s' % access_token}, 'Firebase')

    def _call_json(self, endpoint, payload, headers, provider_name):
        headers.update({'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'})
        request = url_request.Request(endpoint, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        try:
            with url_request.urlopen(request, timeout=30) as response:
                body = response.read().decode('utf-8')
        except url_error.HTTPError as exc:
            body = exc.read().decode('utf-8')
            raise UserError(_('%s hata döndürdü (%s): %s') % (provider_name, exc.code, body)) from exc
        except url_error.URLError as exc:
            raise UserError(_('%s bağlantı hatası: %s') % (provider_name, exc)) from exc
        try:
            return json.loads(body or '{}')
        except ValueError as exc:
            raise UserError(_('%s yanıtı JSON değil: %s') % (provider_name, body)) from exc


class PartnerCourierNotificationRecipient(models.Model):
    _name = 'partner.courier.notification.recipient'
    _description = 'Courier Push Notification Recipient'
    _order = 'notification_id desc, id'

    notification_id = fields.Many2one('partner.courier.notification', string='Bildirim', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Kurye', required=True, ondelete='cascade')
    provider = fields.Selection([('onesignal', 'OneSignal'), ('firebase', 'Firebase Cloud Messaging')],
                                string='Servis', required=True, default='onesignal', readonly=True)
    device_token = fields.Char(string='Cihaz Tokenı', readonly=True)
    player_id = fields.Char(string='Player ID', readonly=True)
    state = fields.Selection([('sent', 'Gönderildi'), ('skipped', 'Cihaz Tokenı Yok / Geçersiz'), ('failed', 'Hatalı')],
                             string='Durum', required=True, default='sent', readonly=True)
    onesignal_notification_id = fields.Char(string='OneSignal Bildirim ID', readonly=True)
    provider_message_id = fields.Char(string='Servis Bildirim ID', readonly=True)
    error_message = fields.Char(string='Hata', readonly=True)

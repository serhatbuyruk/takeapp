import json
import uuid
from urllib import error as url_error
from urllib import request as url_request

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class PartnerCourierNotification(models.Model):
    _name = 'partner.courier.notification'
    _description = 'Courier OneSignal Notification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(string='Başlık', required=True, tracking=True)
    message = fields.Text(string='Mesaj', required=True, tracking=True)
    target_type = fields.Selection(
        [
            ('all', 'Player ID olan tüm kuryeler'),
            ('partners', 'Seçili kişiler'),
            ('domain', 'Contact filtresi'),
        ],
        string='Hedef',
        default='all',
        required=True,
        tracking=True,
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'partner_courier_notification_res_partner_rel',
        'notification_id',
        'partner_id',
        string='Kişiler',
        domain="[('player_id', '!=', False)]",
    )
    partner_domain = fields.Char(
        string='Contact Filtresi',
        default="[]",
        help='res.partner üzerinde uygulanacak Odoo domain filtresi.',
    )
    image_url = fields.Char(string='Bildirim Görsel URL')
    launch_url = fields.Char(string='Açılacak URL')
    additional_data_json = fields.Text(
        string='Ek Veri JSON',
        help='React Native uygulamasına iletilecek opsiyonel ek data.',
    )
    state = fields.Selection(
        [
            ('draft', 'Taslak'),
            ('sent', 'Gönderildi'),
            ('failed', 'Hatalı'),
        ],
        string='Durum',
        default='draft',
        readonly=True,
        tracking=True,
    )
    recipient_line_ids = fields.One2many(
        'partner.courier.notification.recipient',
        'notification_id',
        string='Alıcılar',
        readonly=True,
        copy=False,
    )
    recipient_count = fields.Integer(string='Alıcı Sayısı', compute='_compute_counts', store=True)
    sent_count = fields.Integer(string='Gönderilen', compute='_compute_counts', store=True)
    skipped_count = fields.Integer(string='Atlanan', compute='_compute_counts', store=True)
    failed_count = fields.Integer(string='Hatalı', compute='_compute_counts', store=True)
    onesignal_notification_id = fields.Char(string='OneSignal Bildirim ID', readonly=True, copy=False)
    sent_date = fields.Datetime(string='Gönderim Tarihi', readonly=True, copy=False)
    response_message = fields.Text(string='OneSignal Yanıtı', readonly=True, copy=False)

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
        self.write({
            'state': 'draft',
            'onesignal_notification_id': False,
            'sent_date': False,
            'response_message': False,
        })
        self.mapped('recipient_line_ids').unlink()

    def action_send(self):
        for notification in self:
            notification._send_notification()
        return True

    def _send_notification(self):
        self.ensure_one()
        if self.state == 'sent':
            raise UserError(_('Bu bildirim zaten gönderilmiş. Tekrar göndermek için taslağa alın.'))

        app_id, api_key = self._get_onesignal_settings()
        partners = self._get_target_partners()
        if not partners:
            raise UserError(_('Gönderilecek kurye bulunamadı.'))

        self.recipient_line_ids.unlink()
        recipient_lines = []
        subscription_ids = []
        for partner in partners:
            player_id = (partner.player_id or '').strip()
            state = 'sent' if player_id else 'skipped'
            if player_id:
                subscription_ids.append(player_id)
            recipient_lines.append((0, 0, {
                'partner_id': partner.id,
                'player_id': player_id,
                'state': state,
            }))
        self.write({'recipient_line_ids': recipient_lines})

        if not subscription_ids:
            self.write({
                'state': 'failed',
                'response_message': _('Seçilen kişilerde player_id bulunamadı.'),
            })
            raise UserError(_('Seçilen kişilerde player_id bulunamadı.'))

        responses = []
        invalid_player_ids = set()
        try:
            for chunk in self._split_every(subscription_ids, 20000):
                payload = self._prepare_onesignal_payload(app_id, chunk)
                response = self._call_onesignal(api_key, payload)
                responses.append(response)
                invalid_player_ids.update(response.get('errors', {}).get('invalid_player_ids') or [])
        except UserError as exc:
            self.recipient_line_ids.filtered(lambda line: line.state == 'sent').write({
                'state': 'failed',
                'error_message': str(exc),
            })
            raise

        failed_lines = self.recipient_line_ids.filtered(lambda line: line.player_id in invalid_player_ids)
        if failed_lines:
            failed_lines.write({
                'state': 'failed',
                'error_message': _('OneSignal invalid_player_ids içinde döndü.'),
            })

        valid_sent_lines = self.recipient_line_ids.filtered(
            lambda line: line.state == 'sent' and line.player_id not in invalid_player_ids
        )
        onesignal_ids = [response.get('id') for response in responses if response.get('id')]
        valid_sent_lines.write({'onesignal_notification_id': ','.join(onesignal_ids)})

        self.write({
            'state': 'sent' if onesignal_ids else 'failed',
            'onesignal_notification_id': ','.join(onesignal_ids),
            'sent_date': fields.Datetime.now(),
            'response_message': json.dumps(responses, ensure_ascii=False, indent=2),
        })
        return responses

    def _get_onesignal_settings(self):
        params = self.env['ir.config_parameter'].sudo()
        app_id = (params.get_param('partner_courier_notification.onesignal_app_id') or '').strip()
        api_key = (params.get_param('partner_courier_notification.onesignal_api_key') or '').strip()
        if not app_id or not api_key:
            raise UserError(_('OneSignal App ID ve API Key ayarlarını doldurun.'))
        return app_id, api_key

    def _get_target_partners(self):
        self.ensure_one()
        partner_model = self.env['res.partner']
        base_domain = [('active', '=', True), ('courier_id', '!=', False)]
        if self.target_type == 'all':
            domain = expression.AND([base_domain, [('player_id', '!=', False)]])
            return partner_model.search(domain)
        if self.target_type == 'partners':
            return self.partner_ids

        user_domain = self._parse_partner_domain()
        domain = expression.AND([base_domain, user_domain])
        return partner_model.search(domain)

    def _parse_partner_domain(self):
        self.ensure_one()
        raw_domain = (self.partner_domain or '[]').strip()
        try:
            domain = safe_eval(raw_domain)
        except Exception as exc:
            raise UserError(_('Contact filtresi geçerli bir domain değil: %s') % exc) from exc
        if not isinstance(domain, (list, tuple)):
            raise UserError(_('Contact filtresi liste formatında olmalıdır.'))
        return list(domain)

    def _prepare_onesignal_payload(self, app_id, subscription_ids):
        self.ensure_one()
        payload = {
            'app_id': app_id,
            'include_subscription_ids': subscription_ids,
            'headings': {'en': self.name, 'tr': self.name},
            'contents': {'en': self.message, 'tr': self.message},
            'idempotency_key': str(uuid.uuid4()),
        }
        if self.launch_url:
            payload['app_url'] = self.launch_url
        if self.image_url:
            payload['big_picture'] = self.image_url
            payload['ios_attachments'] = {'image': self.image_url}
        if self.additional_data_json:
            payload['data'] = json.loads(self.additional_data_json)
        return payload

    def _split_every(self, values, size):
        for index in range(0, len(values), size):
            yield values[index:index + size]

    def _call_onesignal(self, api_key, payload):
        body = json.dumps(payload).encode('utf-8')
        headers = {
            'Authorization': 'Key %s' % api_key,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
        }
        request = url_request.Request(
            'https://onesignal.com/api/v1/notifications',
            data=body,
            headers=headers,
            method='POST',
        )
        try:
            with url_request.urlopen(request, timeout=30) as response:
                response_body = response.read().decode('utf-8')
        except url_error.HTTPError as exc:
            response_body = exc.read().decode('utf-8')
            self.write({
                'state': 'failed',
                'response_message': response_body,
            })
            raise UserError(_('OneSignal hata döndürdü (%s): %s') % (exc.code, response_body)) from exc
        except url_error.URLError as exc:
            self.write({
                'state': 'failed',
                'response_message': str(exc),
            })
            raise UserError(_('OneSignal bağlantı hatası: %s') % exc) from exc

        try:
            return json.loads(response_body or '{}')
        except ValueError as exc:
            self.write({
                'state': 'failed',
                'response_message': response_body,
            })
            raise UserError(_('OneSignal yanıtı JSON değil: %s') % response_body) from exc


class PartnerCourierNotificationRecipient(models.Model):
    _name = 'partner.courier.notification.recipient'
    _description = 'Courier OneSignal Notification Recipient'
    _order = 'notification_id desc, id'

    notification_id = fields.Many2one(
        'partner.courier.notification',
        string='Bildirim',
        required=True,
        ondelete='cascade',
    )
    partner_id = fields.Many2one('res.partner', string='Kurye', required=True, ondelete='cascade')
    player_id = fields.Char(string='Player ID', readonly=True)
    state = fields.Selection(
        [
            ('sent', 'Gönderildi'),
            ('skipped', 'Player ID Yok'),
            ('failed', 'Hatalı'),
        ],
        string='Durum',
        required=True,
        default='sent',
        readonly=True,
    )
    onesignal_notification_id = fields.Char(string='OneSignal Bildirim ID', readonly=True)
    error_message = fields.Char(string='Hata', readonly=True)

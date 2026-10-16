import json
import logging
import secrets
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from odoo import SUPERUSER_ID, api, fields, models, registry, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
_TURKEY_TIMEZONE = ZoneInfo('Europe/Istanbul')


class PartnerCourierCall(models.Model):
    _name = 'partner.courier.call'
    _description = 'Courier Online Call'
    _order = 'create_date desc, id desc'

    name = fields.Char(string='Görüşme', required=True, readonly=True)
    courier_id = fields.Many2one(
        'res.partner',
        string='Kurye',
        required=True,
        readonly=True,
        index=True,
        ondelete='cascade',
    )
    manager_user_id = fields.Many2one(
        'res.users',
        string='Saha Yöneticisi Kullanıcısı',
        readonly=True,
        index=True,
        ondelete='set null',
    )
    manager_partner_id = fields.Many2one(
        'res.partner',
        string='Saha Yöneticisi',
        readonly=True,
        index=True,
        ondelete='restrict',
    )
    channel_id = fields.Many2one(
        'mail.channel',
        string='Discuss Kanalı',
        readonly=True,
        index=True,
        ondelete='set null',
    )
    guest_id = fields.Many2one(
        'mail.guest',
        string='Kurye Misafir Oturumu',
        readonly=True,
        copy=False,
        ondelete='set null',
    )
    manager_guest_id = fields.Many2one(
        'mail.guest',
        string='Yönetici Misafir Oturumu',
        readonly=True,
        copy=False,
        ondelete='set null',
    )
    access_token = fields.Char(
        string='Güvenli Erişim Anahtarı',
        required=True,
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: secrets.token_urlsafe(32),
        groups='base.group_system',
    )
    manager_access_token = fields.Char(
        string='Yönetici Güvenli Erişim Anahtarı',
        required=True,
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: secrets.token_urlsafe(32),
        groups='base.group_system',
    )
    manager_notification_id = fields.Many2one(
        'partner.courier.notification',
        string='Yönetici Bildirimi',
        readonly=True,
        copy=False,
        ondelete='set null',
    )
    manager_push_state = fields.Selection(
        [
            ('pending', 'Bekliyor'),
            ('sent', 'Gönderildi'),
            ('unavailable', 'Bildirim Alınamıyor'),
            ('failed', 'Hatalı'),
        ],
        string='Yönetici Bildirim Durumu',
        required=True,
        readonly=True,
        default='pending',
        copy=False,
    )
    manager_push_error = fields.Text(
        string='Yönetici Bildirim Hatası',
        readonly=True,
        copy=False,
    )
    state = fields.Selection(
        [
            ('waiting', 'Katılım Bekleniyor'),
            ('ringing', 'Yönetici Aranıyor'),
            ('active', 'Görüşme Aktif'),
            ('ended', 'Tamamlandı'),
            ('missed', 'Cevapsız'),
            ('rejected', 'Reddedildi'),
            ('expired', 'Süresi Doldu'),
            ('cancelled', 'İptal Edildi'),
        ],
        string='Durum',
        required=True,
        readonly=True,
        default='waiting',
        index=True,
    )
    expires_at = fields.Datetime(
        string='Bağlantı Son Geçerlilik Zamanı',
        required=True,
        readonly=True,
        default=lambda self: fields.Datetime.now() + timedelta(minutes=15),
    )
    ringing_at = fields.Datetime(string='Arama Başlangıcı', readonly=True)
    answered_at = fields.Datetime(string='Cevaplanma Zamanı', readonly=True)
    ended_at = fields.Datetime(string='Bitiş Zamanı', readonly=True)
    ended_by = fields.Selection(
        [
            ('courier', 'Kurye'),
            ('manager', 'Saha Yöneticisi'),
        ],
        string='Görüşmeyi Sonlandıran',
        readonly=True,
        copy=False,
    )
    duration_seconds = fields.Integer(
        string='Görüşme Süresi (Saniye)',
        compute='_compute_duration',
        store=True,
        readonly=True,
    )
    duration_display = fields.Char(
        string='Görüşme Süresi',
        compute='_compute_duration',
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        ('access_token_unique', 'UNIQUE(access_token)', 'Görüşme erişim anahtarı benzersiz olmalıdır.'),
        ('manager_access_token_unique', 'UNIQUE(manager_access_token)', 'Yönetici erişim anahtarı benzersiz olmalıdır.'),
    ]

    @api.depends('answered_at', 'ended_at')
    def _compute_duration(self):
        for call in self:
            if not call.answered_at or not call.ended_at or call.ended_at < call.answered_at:
                call.duration_seconds = 0
                call.duration_display = False
                continue
            seconds = int((call.ended_at - call.answered_at).total_seconds())
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            call.duration_seconds = hours * 3600 + minutes * 60 + seconds
            call.duration_display = (
                '%02d:%02d:%02d' % (hours, minutes, seconds)
                if hours
                else '%02d:%02d' % (minutes, seconds)
            )

    @api.constrains('manager_user_id')
    def _check_manager_user(self):
        for call in self.filtered('manager_user_id'):
            if not call.manager_user_id.active:
                raise ValidationError(_('Saha yöneticisi kullanıcısı aktif olmalıdır.'))

    def _manager_partner(self):
        self.ensure_one()
        return self.manager_partner_id or self.manager_user_id.partner_id

    def _prepare_manager_guest_join(self):
        for call in self:
            call.channel_id.sudo().channel_member_ids.filtered(
                lambda member: member.partner_id == call._manager_partner()
            ).unlink()
        return True

    @api.model
    def create_courier_call(self, courier, manager_partner=False):
        courier = courier.exists()
        if not courier or not courier.active or not courier.courier_id:
            raise UserError(_('Aktif bir kurye kaydı bulunamadı.'))

        manager = manager_partner or courier.courier_field_manager_partner_id
        if not manager and courier.courier_field_manager_id:
            manager = courier.courier_field_manager_id.partner_id
        if not manager or not manager.active or manager == courier:
            raise UserError(_('Bu kurye için aktif bir saha yöneticisi tanımlanmamış.'))

        manager_user = manager.user_ids.filtered('active')[:1]

        previous_calls = self.sudo().search([
            ('courier_id', '=', courier.id),
            ('state', 'in', ['waiting', 'ringing']),
        ])
        if previous_calls:
            previous_calls.write({
                'state': 'cancelled',
                'ended_at': fields.Datetime.now(),
                'ended_by': 'courier',
            })

        channel_info = self.env['mail.channel'].sudo().create_group(
            partners_to=[manager.id],
            default_display_mode='video_full_screen',
            name=_('Kurye Görüşmesi - %s') % courier.name,
        )
        channel = self.env['mail.channel'].sudo().browse(channel_info['id']).exists()
        if not channel:
            raise UserError(_('Görüşme kanalı oluşturulamadı.'))
        # mail.channel always adds the request user as a member. Courier calls
        # start from a public route, so that automatic member must not join the call.
        channel.channel_member_ids.filtered(
            lambda member: member.partner_id and member.partner_id != manager
        ).unlink()

        return self.sudo().create({
            'name': _('Kurye Görüşmesi - %s') % courier.name,
            'courier_id': courier.id,
            'manager_partner_id': manager.id,
            'manager_user_id': manager_user.id,
            'channel_id': channel.id,
        })

    @api.model
    def is_support_hours_open(self):
        params = self.env['ir.config_parameter'].sudo()
        start = float(params.get_param('partner_courier_call.support_start_hour', '9.0') or 9.0)
        end = float(params.get_param('partner_courier_call.support_end_hour', '18.0') or 18.0)
        now = datetime.now(_TURKEY_TIMEZONE)
        current = now.hour + now.minute / 60 + now.second / 3600
        if start == end:
            return True
        if start < end:
            return start <= current < end
        return current >= start or current < end

    @api.model
    def get_available_support_partner(self):
        provider = self.env['partner.courier.notification'].sudo()._default_provider()
        candidates = self.env['res.partner'].sudo().search([
            ('active', '=', True),
            ('courier_call_support_member', '=', True),
            ('courier_call_support_available', '=', True),
        ], order='id').sorted(
            key=lambda partner: (partner.courier_call_support_last_call_at or datetime.min, partner.id)
        )
        notification_model = self.env['partner.courier.notification'].sudo()
        return next((partner for partner in candidates
                     if notification_model._partner_has_push_target(partner, provider)), self.env['res.partner'])

    def _caller_display_name(self):
        self.ensure_one()
        first_name = (self.courier_id.courier_first_name or '').strip()
        last_name = (self.courier_id.courier_last_name or '').strip()
        return ' '.join(part for part in (last_name, first_name) if part) or self.courier_id.name

    def _manager_join_url(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '').rstrip('/')
        return '%s/kurye-gorusme/yonetici/%s' % (base_url, self.manager_access_token)

    def _manager_reject_url(self):
        self.ensure_one()
        return '%s/reddet' % self._manager_join_url()

    def _send_manager_notification(self):
        self.ensure_one()
        manager_partner = self._manager_partner()
        if not manager_partner:
            self.write({
                'manager_push_state': 'unavailable',
                'manager_push_error': _('Saha yöneticisi contactı bulunamadı.'),
            })
            return False
        notification_model = self.env['partner.courier.notification'].sudo()
        provider = notification_model._default_provider()
        if not notification_model._partner_has_push_target(manager_partner, provider):
            self.write({
                'manager_push_state': 'unavailable',
                'manager_push_error': _(
                    'Saha yöneticisinin seçili bildirim servisi için geçerli cihaz kimliği yok.'
                ),
            })
            return False

        caller_name = self._caller_display_name()
        answer_url = self._manager_join_url()
        reject_url = self._manager_reject_url()
        notification = notification_model.create({
            'name': _('☎ %s Arıyor') % caller_name,
            'message': _('%s seni bekliyor. Tıkla, konuşmaya katıl.') % caller_name,
            'provider': provider,
            'target_type': 'partners',
            'partner_ids': [(6, 0, manager_partner.ids)],
            'launch_url': answer_url,
            'additional_data_json': json.dumps({
                'screen': 'courier_call',
                'call_id': self.id,
                'launch_url': answer_url,
                'notification_actions': [
                    {
                        'id': 'courier_call_answer',
                        'text': 'Cevapla',
                        'url': answer_url,
                    },
                    {
                        'id': 'courier_call_reject',
                        'text': 'Reddet',
                        'url': reject_url,
                    },
                ],
            }),
        })
        self.manager_notification_id = notification.id
        try:
            notification._send_notification()
        except UserError as exc:  # The call remains usable when the push provider is unavailable.
            _logger.exception('Courier call manager notification failed for call %s', self.id)
            self.write({
                'manager_push_state': 'failed',
                'manager_push_error': str(exc),
            })
            return False

        if notification.state != 'sent':
            self.write({
                'manager_push_state': 'failed',
                'manager_push_error': notification.response_message or _('OneSignal bildirimi kabul etmedi.'),
            })
            return False

        self.write({
            'manager_push_state': 'sent',
            'manager_push_error': False,
        })
        return True

    def schedule_manager_notification(self):
        call_ids = self.ids
        dbname = self.env.cr.dbname

        def send_after_commit():
            with registry(dbname).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                calls = env['partner.courier.call'].browse(call_ids).exists()
                try:
                    for call in calls:
                        call._send_manager_notification()
                    cr.commit()
                except Exception as exc:
                    cr.rollback()
                    env.invalidate_all()
                    _logger.exception('Unexpected manager notification error for calls %s', call_ids)
                    failed_calls = env['partner.courier.call'].browse(call_ids).exists()
                    failed_calls.write({
                        'manager_push_state': 'failed',
                        'manager_push_error': str(exc),
                    })
                    cr.commit()

        self.env.cr.postcommit.add(send_after_commit)
        return True

    def action_end_call(self, ended_by=False):
        if ended_by and ended_by not in ('courier', 'manager'):
            raise ValidationError(_('Görüşmeyi sonlandıran taraf geçersiz.'))
        now = fields.Datetime.now()
        for call in self:
            if call.state in ['ended', 'missed', 'rejected', 'expired', 'cancelled']:
                continue
            rtc_sessions = call.channel_id.sudo().rtc_session_ids
            call.write({
                'state': 'ended',
                'ended_at': now,
                'ended_by': ended_by,
            })
            if rtc_sessions:
                rtc_sessions.unlink()
        return True

    def action_reject_call(self):
        now = fields.Datetime.now()
        rejected = False
        for call in self:
            if call.state not in ['waiting', 'ringing']:
                continue
            rtc_sessions = call.channel_id.sudo().rtc_session_ids
            call.write({
                'state': 'rejected',
                'ended_at': now,
                'ended_by': 'manager',
            })
            if rtc_sessions:
                rtc_sessions.unlink()
            rejected = True
        return rejected

    @api.model
    def _cron_expire_calls(self):
        now = fields.Datetime.now()
        calls = self.sudo().search([
            ('state', 'in', ['waiting', 'ringing']),
            ('expires_at', '<', now),
        ])
        for call in calls:
            call.write({
                'state': 'missed' if call.ringing_at else 'expired',
                'ended_at': now,
            })

        stale_calls = self.sudo().search([
            ('state', 'in', ['ended', 'missed', 'rejected', 'expired', 'cancelled']),
            ('ended_at', '<', now - timedelta(minutes=10)),
            ('channel_id', '!=', False),
        ])
        channels = stale_calls.channel_id
        guests = stale_calls.guest_id | stale_calls.manager_guest_id
        stale_calls.write({
            'channel_id': False,
            'guest_id': False,
            'manager_guest_id': False,
        })
        channels.unlink()
        guests.filtered(lambda guest: not guest.channel_ids).unlink()
        return True

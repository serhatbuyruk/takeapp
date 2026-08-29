from datetime import timedelta

from odoo import fields, http
from odoo.http import request


class KuryetecNotificationsController(http.Controller):

    @staticmethod
    def _display_datetime(value):
        if not value:
            return ''
        localized = fields.Datetime.context_timestamp(
            request.env.user,
            value,
        )
        return localized.strftime('%d.%m.%Y %H:%M')

    @http.route(
        '/bildirimler',
        type='http',
        auth='user',
        website=True,
        methods=['GET'],
        sitemap=False,
    )
    def courier_notifications(self, **params):
        courier = request.env.user.partner_id
        cutoff = fields.Datetime.now() - timedelta(hours=12)

        delivery_logs = request.env['notifier.delivery.log'].sudo().search(
            [
                ('partner_id', '=', courier.id),
                ('sent_at', '>=', cutoff),
            ],
            limit=50,
            order='sent_at desc, id desc',
        )
        items = [
            {
                'name': delivery.title,
                'content': delivery.message,
                'created_at': delivery.sent_at,
                'display_date': self._display_datetime(delivery.sent_at),
                'channel': delivery.channel,
            }
            for delivery in delivery_logs
        ]

        # Upgrade öncesindeki doğrudan kullanıcı bildirimlerini 12 saat boyunca
        # görünür tut. Yeni kayıtlar delivery log üzerinden gelir.
        source_ids = delivery_logs.mapped('source_notification_id').ids
        notifier_model = request.env['notifier.profile'].sudo()
        if {'x_user', 'x_notification_type', 'x_icerik'} <= set(
            notifier_model._fields
        ):
            legacy_domain = [
                ('create_date', '>=', cutoff),
                ('x_notification_type', '=', 'kullanici'),
                ('x_user', '=', request.env.user.id),
            ]
            if source_ids:
                legacy_domain.append(('id', 'not in', source_ids))
            legacy_notifications = notifier_model.search(
                legacy_domain,
                limit=50,
                order='create_date desc, id desc',
            )
            items.extend(
                {
                    'name': notification.name,
                    'content': notification.x_icerik,
                    'created_at': notification.create_date,
                    'display_date': self._display_datetime(
                        notification.create_date
                    ),
                    'channel': 'push',
                }
                for notification in legacy_notifications
            )

        items.sort(
            key=lambda item: item['created_at'] or fields.Datetime.now(),
            reverse=True,
        )
        return request.render(
            'website.bildirimler',
            {
                'bildirimler': items[:50],
                'notification_window_hours': 12,
            },
        )


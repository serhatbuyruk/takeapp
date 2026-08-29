from datetime import timedelta

from odoo import fields
from odoo.tests import HttpCase, new_test_user, tagged


@tagged('post_install', '-at_install', 'kuryetec_notifications')
class TestCourierNotificationsPage(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tested_models = cls.env['ir.model'].search([
            (
                'model',
                'in',
                ['notifier.profile', 'res.partner', 'res.users'],
            )
        ])
        cls.env['base.automation'].search([
            ('model_id', 'in', tested_models.ids),
            ('active', '=', True),
        ]).write({'active': False})

        cls.user = new_test_user(
            cls.env,
            login='notification-courier',
            password='notification-courier',
            groups='base.group_user',
        )
        cls.user.partner_id.write({
            'name': 'Bildirim Test Kuryesi',
            'user_role': 'kurye',
        })
        cls.other_courier = cls.env['res.partner'].create({
            'name': 'Başka Bildirim Kuryesi',
            'user_role': 'kurye',
        })
        log_model = cls.env['notifier.delivery.log']
        log_model.create({
            'partner_id': cls.user.partner_id.id,
            'title': 'OWN-RECENT-NOTIFICATION',
            'message': 'Bu bildirim görünmeli.',
            'sent_at': fields.Datetime.now(),
        })
        log_model.create({
            'partner_id': cls.other_courier.id,
            'title': 'OTHER-COURIER-NOTIFICATION',
            'message': 'Bu bildirim görünmemeli.',
            'sent_at': fields.Datetime.now(),
        })
        log_model.create({
            'partner_id': cls.user.partner_id.id,
            'title': 'OWN-OLD-NOTIFICATION',
            'message': 'On iki saatten eski.',
            'sent_at': fields.Datetime.now() - timedelta(hours=13),
        })

    def setUp(self):
        super().setUp()
        self.authenticate(
            'notification-courier',
            'notification-courier',
        )

    def test_page_lists_only_own_last_twelve_hours(self):
        response = self.url_open('/bildirimler')

        self.assertEqual(response.status_code, 200)
        self.assertIn('OWN-RECENT-NOTIFICATION', response.text)
        self.assertNotIn('OTHER-COURIER-NOTIFICATION', response.text)
        self.assertNotIn('OWN-OLD-NOTIFICATION', response.text)
        self.assertIn('Son 12 saat', response.text)


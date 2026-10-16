from datetime import timedelta
import json

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPartnerCourierCall(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager_partner = cls.env['res.partner'].create({
            'name': 'Call Test Manager',
            'courier_id': 'CALL-MANAGER-1',
        })
        cls.manager = cls.env['res.users'].with_context(no_reset_password=True).create({
            'partner_id': cls.manager_partner.id,
            'login': 'call-test-manager',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])],
        })
        cls.courier = cls.env['res.partner'].create({
            'name': 'Call Test Courier',
            'courier_id': 'CALL-TEST-1',
            'courier_first_name': 'Test Call',
            'courier_last_name': 'Courier',
            'courier_field_manager_partner_id': cls.manager_partner.id,
        })

    def test_create_courier_call(self):
        call = self.env['partner.courier.call'].create_courier_call(self.courier)

        self.assertEqual(call.courier_id, self.courier)
        self.assertEqual(call.manager_partner_id, self.manager_partner)
        self.assertEqual(call.manager_user_id, self.manager)
        self.assertEqual(call.channel_id.channel_type, 'group')
        self.assertEqual(call.channel_id.default_display_mode, 'video_full_screen')
        self.assertIn(self.manager_partner, call.channel_id.channel_member_ids.partner_id)
        self.assertEqual(call.channel_id.channel_member_ids.partner_id, self.manager_partner)
        self.assertEqual(call.state, 'waiting')

        call._prepare_manager_guest_join()

        self.assertFalse(call.channel_id.channel_member_ids.partner_id)

    def test_new_call_cancels_previous_waiting_call(self):
        first_call = self.env['partner.courier.call'].create_courier_call(self.courier)
        second_call = self.env['partner.courier.call'].create_courier_call(self.courier)

        self.assertEqual(first_call.state, 'cancelled')
        self.assertEqual(second_call.state, 'waiting')

    def test_another_courier_without_odoo_user_can_be_manager(self):
        manager = self.env['res.partner'].create({
            'name': 'Courier Manager Without User',
            'courier_id': 'CALL-MANAGER-2',
        })
        self.courier.courier_field_manager_partner_id = manager

        call = self.env['partner.courier.call'].create_courier_call(self.courier)

        self.assertEqual(call.manager_partner_id, manager)
        self.assertFalse(call.manager_user_id)
        self.assertIn(manager, call.channel_id.channel_member_ids.partner_id)

    def test_courier_cannot_manage_itself(self):
        with self.assertRaises(ValidationError):
            self.courier.courier_field_manager_partner_id = self.courier

    def test_manager_without_player_id_is_not_notified(self):
        call = self.env['partner.courier.call'].create_courier_call(self.courier)

        self.assertFalse(call._send_manager_notification())
        self.assertEqual(call.manager_push_state, 'unavailable')
        self.assertFalse(call.manager_notification_id)

    def test_end_call_disconnects_all_rtc_sessions(self):
        call = self.env['partner.courier.call'].create_courier_call(self.courier)
        manager_member = call.channel_id.channel_member_ids.filtered(
            lambda member: member.partner_id == self.manager_partner
        )
        rtc_session = self.env['mail.channel.rtc.session'].create({
            'channel_member_id': manager_member.id,
        })

        call.action_end_call(ended_by='courier')

        self.assertEqual(call.state, 'ended')
        self.assertEqual(call.ended_by, 'courier')
        self.assertTrue(call.ended_at)
        self.assertFalse(rtc_session.exists())

    def test_reject_waiting_call(self):
        call = self.env['partner.courier.call'].create_courier_call(self.courier)

        self.assertTrue(call.action_reject_call())

        self.assertEqual(call.state, 'rejected')
        self.assertTrue(call.ended_at)
        self.assertFalse(call.action_reject_call())

    def test_completed_call_duration_is_computed(self):
        call = self.env['partner.courier.call'].create_courier_call(self.courier)
        answered_at = fields.Datetime.now()

        call.write({
            'answered_at': answered_at,
            'ended_at': answered_at + timedelta(minutes=3, seconds=8),
        })

        self.assertEqual(call.duration_seconds, 188)
        self.assertEqual(call.duration_display, '03:08')

    def test_manager_notification_content_and_link(self):
        self.manager_partner.player_id = '215c5815-02f9-4049-a525-cb5e172d4db2'
        call = self.env['partner.courier.call'].create_courier_call(self.courier)
        notification_model = self.env['partner.courier.notification']
        original_send = type(notification_model)._send_notification

        def fake_send(notification):
            notification.write({'state': 'sent'})
            return [{'id': 'test-notification'}]

        try:
            type(notification_model)._send_notification = fake_send
            self.assertTrue(call._send_manager_notification())
        finally:
            type(notification_model)._send_notification = original_send

        notification = call.manager_notification_id
        self.assertEqual(notification.name, '☎ Courier Test Call Arıyor')
        self.assertIn('seni bekliyor', notification.message)
        self.assertIn(call.manager_access_token, notification.launch_url)
        self.assertEqual(notification.partner_ids, self.manager_partner)
        self.assertEqual(call.manager_push_state, 'sent')

        data = json.loads(notification.additional_data_json)
        self.assertEqual(
            [action['id'] for action in data['notification_actions']],
            ['courier_call_answer', 'courier_call_reject'],
        )
        self.assertIn(call.manager_access_token, data['notification_actions'][1]['url'])

        payload = notification._prepare_onesignal_payload(
            'test-app-id',
            [self.manager_partner.player_id],
        )
        self.assertEqual(
            payload['buttons'],
            [
                {'id': 'courier_call_answer', 'text': 'Cevapla'},
                {'id': 'courier_call_reject', 'text': 'Reddet'},
            ],
        )
        self.assertEqual(payload['web_buttons'][0]['url'], call._manager_join_url())
        self.assertEqual(payload['web_buttons'][1]['url'], call._manager_reject_url())

        self.env['ir.config_parameter'].sudo().set_param(
            'partner_courier_call.mobile_notification_actions_enabled',
            'False',
        )
        mobile_payload = notification._prepare_onesignal_payload(
            'test-app-id',
            [self.manager_partner.player_id],
        )
        self.assertNotIn('buttons', mobile_payload)

        firebase_payload = notification._prepare_firebase_payload(
            'f' * 152,
        )
        message = firebase_payload['message']
        self.assertNotIn('notification', message)
        self.assertEqual(message['data']['notification_type'], 'courier_call')
        self.assertEqual(message['data']['android_notification_mode'], 'local')
        self.assertEqual(message['data']['title'], notification.name)
        self.assertEqual(message['data']['body'], notification.message)
        self.assertEqual(message['apns']['headers']['apns-push-type'], 'alert')
        self.assertEqual(message['apns']['payload']['aps']['category'], 'COURIER_CALL')
        self.assertEqual(message['apns']['payload']['aps']['sound'], 'courier_call_ring.wav')

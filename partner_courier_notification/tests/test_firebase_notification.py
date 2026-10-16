from odoo.tests.common import TransactionCase


class TestFirebaseNotification(TransactionCase):

    def setUp(self):
        super().setUp()
        self.env['ir.config_parameter'].sudo().set_param(
            'partner_courier_notification.provider', 'firebase')
        self.partner = self.env['res.partner'].create({
            'name': 'Firebase Test Courier',
            'courier_id': 'firebase-test-courier',
            'firebase_token': 'f' * 152,
        })
        self.notification = self.env['partner.courier.notification'].create({
            'name': 'Test', 'message': 'Firebase test', 'provider': 'firebase',
            'target_type': 'partners', 'partner_ids': [(6, 0, self.partner.ids)],
            'launch_url': 'https://example.test/call',
            'additional_data_json': '{"count": 2, "actions": ["answer", "reject"]}',
        })

    def test_firebase_target_and_payload(self):
        self.assertEqual(self.notification._get_target_partners(), self.partner)
        self.assertTrue(self.notification._partner_has_push_target(self.partner, 'firebase'))
        payload = self.notification._prepare_firebase_payload(self.partner.firebase_token)
        data = payload['message']['data']
        self.assertEqual(data['launch_url'], 'https://example.test/call')
        self.assertEqual(data['count'], '2')
        self.assertEqual(data['actions'], '["answer", "reject"]')

    def test_invalid_firebase_token_is_not_a_target(self):
        self.partner.firebase_token = 'short'
        self.assertFalse(self.notification._partner_has_push_target(self.partner, 'firebase'))

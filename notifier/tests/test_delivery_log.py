from unittest.mock import patch

import requests

from odoo.tests.common import TransactionCase


class TestNotifierDeliveryLog(TransactionCase):

    def setUp(self):
        super().setUp()
        self.notifier = self.env['notifier.profile']
        self.courier = self.env['res.partner'].create({
            'name': 'Notifier Test Courier',
            'user_role': 'kurye',
            'player_id': 'player-courier-1',
        })

    @staticmethod
    def _successful_response(mocked_request):
        response = mocked_request.return_value
        response.status_code = 200
        response.raise_for_status.return_value = None
        return response

    @patch('odoo.addons.notifier.models.notifier.requests.request')
    def test_successful_push_creates_recipient_delivery_log(
        self,
        mocked_request,
    ):
        self._successful_response(mocked_request)

        result = self.notifier.send_Push_Notification_With_Playerid_V1(
            'test-auth',
            'test-app',
            [self.courier.player_id],
            'Yeni Teslimat',
            'Paket restoranda hazır.',
        )

        self.assertTrue(result)
        delivery = self.env['notifier.delivery.log'].search([])
        self.assertEqual(delivery.partner_id, self.courier)
        self.assertEqual(delivery.title, 'Yeni Teslimat')
        self.assertEqual(delivery.message, 'Paket restoranda hazır.')
        self.assertEqual(delivery.channel, 'push')

    @patch('odoo.addons.notifier.models.notifier.requests.request')
    def test_voice_push_is_marked_with_voice_channel(
        self,
        mocked_request,
    ):
        self._successful_response(mocked_request)

        self.notifier.send_Push_Notification_With_Playerid_Voice(
            'test-auth',
            'test-app',
            [self.courier.player_id],
            'test-channel',
            'warning',
            'test.wav',
            'test',
            'Slotun Yaklaşıyor',
            '30 dakika sonra slotun başlayacak.',
        )

        delivery = self.env['notifier.delivery.log'].search([])
        self.assertEqual(delivery.channel, 'voice_push')

    @patch('odoo.addons.notifier.models.notifier.requests.request')
    def test_unknown_player_id_does_not_create_delivery_log(
        self,
        mocked_request,
    ):
        self._successful_response(mocked_request)

        self.notifier.send_Push_Notification_With_Playerid_V1(
            'test-auth',
            'test-app',
            ['unknown-player'],
            'Başlık',
            'İçerik',
        )

        self.assertFalse(self.env['notifier.delivery.log'].search([]))

    @patch(
        'odoo.addons.notifier.models.notifier.requests.request',
        side_effect=requests.Timeout('provider timeout'),
    )
    def test_failed_push_does_not_create_delivery_log(
        self,
        mocked_request,
    ):
        result = self.notifier.send_Push_Notification_With_Playerid_V1(
            'test-auth',
            'test-app',
            [self.courier.player_id],
            'Başlık',
            'İçerik',
        )

        self.assertFalse(result)
        self.assertFalse(self.env['notifier.delivery.log'].search([]))

    @patch('odoo.addons.notifier.models.notifier.requests.request')
    def test_manual_source_is_linked_to_delivery(
        self,
        mocked_request,
    ):
        self._successful_response(mocked_request)
        source = self.env['notifier.profile'].create({
            'name': 'Kaynak Bildirim',
        })

        self.notifier.with_context(
            notifier_source_id=source.id
        ).send_Push_Notification_With_Playerid_V1(
            'test-auth',
            'test-app',
            [self.courier.player_id],
            'Kaynak Bildirim',
            'Kaynak içerik',
        )

        delivery = self.env['notifier.delivery.log'].search([])
        self.assertEqual(delivery.source_notification_id, source)


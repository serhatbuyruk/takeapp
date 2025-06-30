# -*- coding: utf-8 -*-

import logging
import pprint
from odoo import http, _
from odoo.http import request, route
from werkzeug.exceptions import Forbidden
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentPaytr(http.Controller):
    _process_url = '/payment/trpay/process'
    _webhook_url = '/payment/trpay/webhook'

    @route(_process_url, type='http', auth='public', methods=['POST'], website=True, csrf=False, sitemap=False)
    def paytr_process_transaction(self, **post):
        _logger.info("Handling custom processing with data:\n%s", pprint.pformat(post))
        return request.render('payment_trpay.paytr_checkout_form', post)

    @route(_webhook_url, type='http', auth='public', methods=['POST'], csrf=False, sitemap=False)
    def paytr_webhook(self, **data):
        """ Process the notification data sent by PayTr to the webhook.

              See https://dev.paytr.com/iframe-api/iframe-api-2-adim

              :param dict data: The notification data.
              :return: The 'SUCCESS' string to acknowledge the notification
              :rtype: str
              """
        _logger.info("Notification received from PayTr with data:\n%s", pprint.pformat(data))
        try:
            # Check the integrity of the notification.
            tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data('paytr', data)
            self._verify_notification_hash(data, tx_sudo)
            # Handle the notification data.
            tx_sudo._handle_notification_data('paytr', data)
        except ValidationError:  # Acknowledge the notification to avoid getting spammed.
            _logger.exception("Unable to handle the notification data; skipping to acknowledge.")
        return request.make_response('OK', headers=None, cookies=None, status=200)  # Acknowledge the notification.

    @staticmethod
    def _verify_notification_hash(notification_data, tx_sudo):
        received_hash = notification_data.get('hash').replace('\\', '')
        if not received_hash:
            _logger.warning("received notification with missing hash")
            raise Forbidden(_('PAYTR notification failed: missing hash'))
        expected_hash = tx_sudo.provider_id._paytr_calculate_hash(notification_data).decode()
        if expected_hash != received_hash:
            _logger.warning("received notification with invalid hash")
            raise Forbidden(_('PAYTR notification failed: bad hash'))

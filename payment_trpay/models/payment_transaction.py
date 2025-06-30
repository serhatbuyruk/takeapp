import logging
from odoo import _, fields, models, api
from odoo.addons.payment_trpay.controllers.controllers import PaymentPaytr
from odoo.addons.payment import utils as payment_utils
import base64
import hmac
import hashlib
import requests
import json
from odoo import http
from odoo.exceptions import ValidationError, UserError
import pprint
from werkzeug.urls import url_encode, url_join, url_parse
from werkzeug import urls
import phonenumbers
from decimal import *

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    refund_amount = fields.Monetary(
        string="Refund Amount", currency_field='currency_id', readonly=True, required=False, store=True)

    @api.model
    def _compute_reference(self, provider_code, prefix=None, separator='-', **kwargs):
        """ Override of `payment` to ensure that APS' requirements for references are satisfied.

                APS' requirements for transaction are as follows:
                - References can only be made of alphanumeric characters and/or '-' and '_'.
                  The prefix is generated with 'tx' as default. This prevents the prefix from being
                  generated based on document names that may contain non-allowed characters
                  (eg: INV/2020/...).

                :param str provider_code: The code of the provider handling the transaction.
                :param str prefix: The custom prefix used to compute the full reference.
                :param str separator: The custom separator used to separate the prefix from the suffix.
                :return: The unique reference for the transaction.
                :rtype: str
                """
        if provider_code == 'paytr':
            separator = "X"
            if not prefix:
                prefix = payment_utils.singularize_reference_prefix(prefix='S', separator='', max_length=64)
        return super(PaymentTransaction, self)._compute_reference(provider_code, prefix, separator, **kwargs)

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Paypal-specific rendering values.

               Note: self.ensure_one() from `_get_processing_values`

               :param dict processing_values: The generic and specific processing values of the transaction
               :return: The dict of provider-specific processing values
               :rtype: dict
               """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'paytr':
            return res
        result = self._generate_token()
        return {
            'api_url': PaymentPaytr._process_url,
            'token': result.get("token"),
            'error': result.get("error")
        }

    def _process_notification_data(self, notification_data):
        """ Override of `payment' to process the transaction based on APS data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data are received.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'paytr':
            return
        status = notification_data.get('status')
        if not status:
            raise ValidationError("Cant find status value")
        self.provider_reference = f'paytr-{self.reference}'
        failed_reason_msg = ''
        total_amount = None
        payment_amount = None
        if notification_data.get('failed_reason_msg'):
            failed_reason_msg = notification_data.get('failed_reason_msg')
        currency_id = self.provider_id.paytr_currency_id
        if notification_data.get('total_amount'):
            total_amount = int(notification_data.get('total_amount'))
            total_amount = payment_utils.to_major_currency_units(total_amount, currency_id, 2)

        if notification_data.get('payment_amount'):
            payment_amount = int(notification_data.get('payment_amount'))
            payment_amount = payment_utils.to_major_currency_units(payment_amount, currency_id, 2)

        interest = False
        if total_amount and payment_amount and (total_amount > payment_amount):  # Vade farkı ekleyelim
            interest = True
            # price_unit = total_amount - self.amount
            price_unit = float(format((Decimal(total_amount) - Decimal(payment_amount)), '.2f'))
            self._add_order_line(price_unit)
            self.update({'amount': total_amount})
            self.update({'refund_amount': payment_amount})
        self._add_order_payment_term(interest)

        if status == 'success':
            self._set_done()
            # Immediately post-process the transaction if it is a refund, as the post-processing
            # will not be triggered by a customer browsing the transaction from the portal.
            if self.operation == 'refund':
                self.env.ref('payment.cron_post_process_payment_tx')._trigger()
        else:
            self._set_error(str(failed_reason_msg))

    def _add_order_line(self, price_unit):
        self.ensure_one()
        product_6002 = self.provider_id.paytr_payment_interest_product_id
        if product_6002 and self.sale_order_ids.id:
            self.env['sale.order.line'].sudo().create({
                'product_id': product_6002.id,
                'order_id': self.sale_order_ids.id,
                'price_unit': price_unit
            })

    def _add_order_payment_term(self, interest=False):
        term_id = self.provider_id.paytr_payment_interest_term_id \
            if interest else self.provider_id.paytr_payment_term_id
        if term_id:
            self.sale_order_ids.payment_term_id = term_id

    def _generate_token(self):
        result = {}
        error_str = []
        merchant_id = self.provider_id.paytr_merchant_id
        merchant_key = self.provider_id.paytr_merchant_key.encode()
        merchant_salt = self.provider_id.paytr_merchant_salt.encode()
        if not self.partner_email:
            error_str.append(_('Your email address was not found!'))
        if not self.partner_phone:
            error_str.append(_('Your phone number was not found!'))
        try:
            phone_parse = phonenumbers.parse(self.partner_phone, 'TR')
            user_phone = str(phone_parse.national_number)
        except:
            error_str.append(_('Your phone number is not in the desired format'))
            user_phone = self.partner_phone
        email = self.partner_email
        user_address = self.partner_address
        merchant_oid = self.reference
        payment_amount = str(payment_utils.to_minor_currency_units(
            self.amount, self.provider_id.paytr_currency_id, 2
        ))
        user_name = self.env.user.name
        user_ip = payment_utils.get_customer_ip_address()
        all_product_list = self._generate_user_basket()
        user_basket = base64.b64encode(json.dumps(all_product_list).encode())
        test_mode = '1' if self.provider_id.state == 'test' else '0'
        no_installment = self.provider_id.paytr_no_installment
        max_installment = self.provider_id.paytr_max_installmentt
        currency = self.provider_id.paytr_currency_id.name
        timeout_limit = self.provider_id.paytr_timeout_limit
        merchant_ok_url = self._get_status_url()
        merchant_fail_url = self._get_status_url()
        debug_on = '1' if self.provider_id.state == 'test' else '0'
        lang = self.partner_lang[:2]
        hash_str = merchant_id + user_ip + merchant_oid + email + payment_amount + user_basket.decode() + no_installment + max_installment + currency + test_mode
        paytr_token = base64.b64encode(
            hmac.new(merchant_key, hash_str.encode() + merchant_salt, hashlib.sha256).digest())
        params = {
            'merchant_id': merchant_id,
            'user_ip': user_ip,
            'merchant_oid': merchant_oid,
            'email': email,
            'payment_amount': payment_amount,
            'paytr_token': paytr_token,
            'user_basket': user_basket,
            'debug_on': debug_on,
            'no_installment': no_installment,
            'max_installment': max_installment,
            'user_name': user_name,
            'user_address': user_address,
            'user_phone': user_phone,
            'merchant_ok_url': merchant_ok_url,
            'merchant_fail_url': merchant_fail_url,
            'timeout_limit': timeout_limit,
            'currency': currency,
            'lang': lang,
            'test_mode': test_mode
        }
        _logger.info("PAYTR PARAMS:\n%s", pprint.pformat(params))

        if len(error_str) > 0:  # demekki hata var
            error = "<br />".join(error_str)
            result['error'] = error
            return result
        res = self._paytr_make_request('odeme/api/get-token', params)
        if res['status'] == 'success':
            result['token'] = res['token']
        else:
            _logger.error(res)
            result['error'] = res["reason"]
        return result

    def _paytr_make_request(self, endpoint, payload=None):
        self.ensure_one()
        url = url_join('https://www.paytr.com/', endpoint)
        try:
            response = requests.post(url, payload)
        except requests.exceptions.ConnectionError:
            _logger.exception("unable to reach endpoint at %s", url)
            raise UserError(_("Could not connect to Payment Provider. Please try again later"))
        return json.loads(response.text)

    def _generate_user_basket(self):
        order_lines = self.sale_order_ids.order_line
        all_product_list = []
        if order_lines:
            for order in order_lines:
                product_list = [str(order.name), str(order.price_unit), int(order.product_uom_qty)]
                all_product_list.append(product_list)
        return all_product_list

    def _get_status_url(self):
        base_url = self.provider_id.get_base_url()
        return urls.url_join(base_url, '/payment/status')

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of `payment` to find the transaction based on PayTr data.
             :param str provider_code: The code of the provider that handled the transaction.
             :param dict notification_data: The notification data sent by the provider.
             :return: The transaction if found.
             :rtype: recordset of `payment.transaction`
             :raise ValidationError: If inconsistent data are received.
             :raise ValidationError: If the data match no transaction.
             """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'paytr' or len(tx) == 1:
            return tx
        reference = notification_data.get('merchant_oid')
        if not reference:
            raise ValidationError(
                "PayTr: " + _("Received data with missing reference %(ref)s.", ref=reference)
            )
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'paytr')])
        if not tx:
            raise ValidationError(
                "PayTr: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _send_refund_request(self, amount_to_refund=None):
        """ Override of `payment` to send a refund request to paytr.

        Note: self.ensure_one()

        :param float amount_to_refund: The amount to refund.
        :return: The refund transaction created to process the refund request.
        :rtype: recordset of `payment.transaction`
        """
        refund_tx = super()._send_refund_request(amount_to_refund=amount_to_refund)
        if self.provider_code != 'paytr':
            return refund_tx
        # generate token
        merchant_id = self.provider_id.paytr_merchant_id
        merchant_key = self.provider_id.paytr_merchant_key.encode()
        merchant_salt = self.provider_id.paytr_merchant_salt
        merchant_oid = self.reference
        return_amount = str(-refund_tx.amount)

        # Make the refund request to paytr

        hash_str = merchant_id + merchant_oid + return_amount + merchant_salt
        paytr_token = base64.b64encode(hmac.new(merchant_key, hash_str.encode(), hashlib.sha256).digest())

        payload = {
            'merchant_id': self.provider_id.paytr_merchant_id,
            'merchant_oid': merchant_oid,
            'return_amount': return_amount,
            'paytr_token': paytr_token
        }
        _logger.info(
            "Payload of paytr Refund %s:\n%s",
            self.reference, pprint.pformat(payload)
        )
        response = self._paytr_make_request('odeme/iade', payload)
        _logger.info(
            "Response of paytr refund %s:\n%s",
            self.reference, pprint.pformat(response)
        )
        refund_tx._handle_notification_data('paytr', response)

        return refund_tx

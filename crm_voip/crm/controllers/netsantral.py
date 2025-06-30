# -*- coding: utf-8 -*-
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_TIME_FORMAT, calendar
from odoo.http import request
from odoo import http, api
from datetime import datetime, timedelta
from os import path
import json
import logging
import requests
import time
from ...library.tools import to_2d_float

_logger = logging.getLogger(__name__)

quene_response = {}


class NetsantralController(http.Controller):

    @http.route('/crm/netsantral/calllog/<string:token>', type='http', auth="public", methods=['POST'], csrf=False)
    def call_logs(self, token, **param):
        operator = request.env['crm_voip.providers.pbx'].sudo().search([('token', '=', token)], limit=1)

        if not operator:
            return "Token Error"

        partner_id = operator.partner_id

        if len(param) > 0:
            log_db = request.env['crm_voip.crm.customer.call_log'].sudo()
            call_db = request.env['crm_voip.crm.customer.call'].sudo()
            seller_db = request.env['crm_voip.seller'].sudo()
            phone_db = request.env['crm_voip.crm.customer.phone'].sudo()
            user_db = request.env['res.users'].sudo()

            _logger.warning(json.dumps(param))

            call_map = {
                'unique_id': 'unique_id',
                'incoming_number': 'incoming_phone',
                # 'talktime': 'duration',
                'internal_num': 'internal_number',
                'customer_num': 'phone',
            }
            log_map = {
                'unique_id': 'unique_id',
                'pbx_num': 'pbx_num',
                'internal_num': 'internal_num',
                'customer_num': 'customer_num',
                'incoming_number': 'incoming_number',
                'scenario': 'scenario',
                'context': 'context',
                'context_name': 'context_name',
                'digit': 'digit',
                'type': 'type',
                'queue_name': 'queue_name',
                # 'talktime': 'talktime',
                # 'holdtime': 'holdtime',
            }

            log_param = {
                'partner_id': partner_id.id
            }

            call_param = {
                'partner_id': partner_id.id
            }

            param_list = list(param)
            call_log = json.loads(param_list[0])
            if call_log.get("unique_id"):
                call_record = call_db.search(
                    [('partner_id', '=', partner_id.id), ('unique_id', '=', call_log.get("unique_id"))])
                seller_record = None
                phone_record = None
                if call_record.seller_id:
                    seller_record = call_record.seller_id

                if call_record.phone_id:
                    phone_record = call_record.phone_id

                for call_key, call_value in call_log.items():
                    if call_key in call_map:
                        call_param[call_map[call_key]] = call_value

                    if call_key in log_map:
                        log_param[log_map[call_key]] = call_value

                if "talktime" in call_log:
                    call_param["duration"] = int(call_log['talktime'])
                    log_param["talktime"] = int(call_log['talktime'])
                    log_param["holdtime"] = int(call_log['holdtime'])

                if "incoming_number" in call_log:
                    seller_search = seller_db.search(
                        [('partner_id', '=', partner_id.id), ('callcenter', '=', call_log['incoming_number'])], limit=1)
                    if seller_search:
                        call_param["seller_id"] = seller_search.id
                        seller_record = seller_search

                if "customer_num" in call_log:
                    if call_log.get("scenario", "NotFound") == 'Outbound_call' and len(call_log['customer_num']) > 2:
                        if call_log['customer_num']:
                            seller_search = seller_db.search(
                                [('partner_id', '=', partner_id.id),
                                 ('callcenter_prefix', '=', call_log['customer_num'][0:2])],
                                limit=1)
                            customer_number = "0%s" % call_log['customer_num'][2:]

                            if not seller_search:
                                seller_search = seller_db.search(
                                    [('partner_id', '=', partner_id.id),
                                     ('callcenter_prefix', '=', call_log['customer_num'][0])],
                                    limit=1)
                                customer_number = "0%s" % call_log['customer_num'][1:]

                            if seller_search:
                                call_log['customer_num'] = customer_number
                                call_param['phone'] = customer_number
                                call_param['seller_id'] = seller_search.id
                                seller_record = seller_search

                    if len(call_log['customer_num']) > 2 and call_log['customer_num'][0:2] == '00':
                        call_log['customer_num'] = call_log['customer_num'][1:]

                    phone_search = phone_db.search(
                        [('partner_id', '=', partner_id.id), ('phone', 'ilike', call_log['customer_num'].lstrip("0"))],
                        limit=1)
                    if phone_search:
                        phone_record = phone_search
                        call_param["phone_id"] = phone_record.id
                        call_param["customer_id"] = phone_record.customer_id.id

                    if not phone_record:
                        phone_record = phone_db.create({
                            'partner_id': partner_id.id,
                            'phone': call_log['customer_num']
                        })
                        call_param["phone_id"] = phone_record.id

                if call_log.get("scenario", "NotFound") in ['InboundtoPBX', 'Inbound_call']:
                    call_param["type"] = 'inbound'

                if call_log.get("scenario", False) == 'Outbound_call':
                    call_param["type"] = 'outbound'

                if call_log.get("scenario", False) == 'Hangup':
                    call_param["call_end"] = True

                if 'talktime' in call_log and int(
                        call_log['talktime']) == 0 and call_record and call_record.type == 'inbound':
                    call_param['unanswered'] = True
                    call_param['unanswered_first'] = True
                    request.env['bus.bus'].sudo().sendone("unanswered", "change")

                if not call_record:
                    call_param["unique_id"] = call_log['unique_id']
                    call_param['start'] = datetime.now()
                    call_record = call_db.create(call_param)
                else:
                    call_update_value = {}
                    for c_key, c_value in call_param.items():
                        if not call_record[c_key] and 'internal_num' != c_key:
                            call_update_value[c_key] = c_value
                    if call_update_value:
                        call_record.write(call_update_value)

                log_param['call_id'] = call_record.id
                log_db.create(log_param)

                if "internal_num" in log_param and call_log.get("scenario", "NotFound") == 'Inbound_call':
                    user = user_db.search(
                        [('partner_id.parent_id', '=', partner_id.id), ('partner_id.phone', '=', log_param['internal_num'])],
                        limit=1)
                    if seller_record and user:
                        message = {
                            'seller': seller_record.name,
                            'seller_number': seller_record.callcenter,
                            'customer_number': phone_record.phone,
                            'customer_phone_id': phone_record.id,
                            'call_id': call_record.id,
                            'calls': [],
                        }

                        if phone_record.customer_id:
                            last_calls = []
                            last_call_record = request.env['crm_voip.crm.customer.call'].sudo().search(
                                [('customer_id', '=', phone_record.customer_id.id)], limit=3)
                            if last_call_record:
                                lang = request.env['res.lang'].sudo().search([('code', '=', user.lang)], limit=1)
                                for l in last_call_record:
                                    last_calls.append({
                                        'date': l.create_date.strftime("%s %s" % (lang.date_format, lang.time_format)),
                                        'seller': l.seller_id.name if l.seller_id else ''
                                    })
                            message.update({
                                'customer_exist': True,
                                'customer_name': phone_record.customer_id.full_name,
                                'customer_id': phone_record.customer_id.id,
                                'customer_note': phone_record.customer_id.note,
                                'customer_phone_description': phone_record.description,
                                'calls': last_calls,
                            })
                        else:
                            message.update({
                                'customer_exist': False
                            })
                        request.env['bus.bus'].sudo().sendone("pbx_%s" % user.partner_id.id, message)

        return "OK"

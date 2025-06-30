# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo import http
from odoo.http import request, Response
from datetime import datetime
import logging
import requests
import json
_logger = logging.getLogger(__name__)
from odoo.tools import date_utils
import base64

class notifierProfileReq(http.Controller):

    @http.route(['/notifier/<card_id>'], type="http", auth="public", methods=["GET"], cors='*', website=True, csrf=False)
    def notifier_profile_analyze(self,card_id):
        notifier = http.request.env['notifiers.profile'].sudo().search([["card_id","ilike",card_id]],limit=1)
        qr = http.request.env['qidgenerator.qidgenerator'].sudo().search([["card_id","=",card_id]],limit=1)
        if qr:  
            if notifier:
                return request.render("website.nfc-profile", {'contact': notifier.card_owner, 'notifier': notifier})
            else:
                return request.render("website.nfc-signup-form", {'card_id': card_id})
        else:
            return request.render("website.contactus_thanks_ea2f2e_70ad58_ef8852")
        
    @http.route('/netgsmcallback', type="json", auth="public", methods=["POST"], cors='*', csrf=False)
    def netgsm_Callback(self):
        data = json.loads(request.httprequest.data)
        _logger.info("Callback Came From Netgsm: " + str(data))
        create_ir_logging = request.env['ir.logging'].sudo().create({
                    'dbname': "Last Server",
                    'type': 'server',
                    'name': 'odoo.addons.base.models.ir_actions',
                    'level': 'info',
                    'path': 'action',
                    'line': '489',
                    'func': 'netgsm_Callback',
                    'message':  str(data)
                })
        create_notifier = request.env['notifier.profile'].sudo().create({
                    'name': str(data)
                })
        return "{'code': 200, 'message': 'Successfull'}"

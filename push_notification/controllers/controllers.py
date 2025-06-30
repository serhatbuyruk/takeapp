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

""" class notifierProfileReq(http.Controller):

    @http.route(['/notifier/<card_id>'], type="http", auth="public", methods=["GET"], cors='*', website=True, csrf=False)
    def notifier_profile_analyze(self,card_id):
        push_notification = http.request.env['push_notification.profile'].sudo().search([["card_id","ilike",card_id]],limit=1)
        qr = http.request.env['qidgenerator.qidgenerator'].sudo().search([["card_id","=",card_id]],limit=1)
        if qr:  
            if notifier:
                return request.render("website.nfc-profile", {'contact': push_notification.card_owner, 'notifier': push_notification})
            else:
                return request.render("website.nfc-signup-form", {'card_id': card_id})
        else:
            return request.render("website.contactus_thanks_ea2f2e_70ad58_ef8852") """
7
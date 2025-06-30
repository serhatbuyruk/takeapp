# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo import http
from odoo.http import request, route
from datetime import datetime
import logging
import requests
import json
_logger = logging.getLogger(__name__)
from odoo.tools import date_utils
import uuid
import base64
from odoo.addons.portal.controllers.portal import CustomerPortal
import os

class paramProfileController(CustomerPortal):
    @route(['/param/info'], type='http', auth='public', website=True, csrf=False)
    def get_text(self, redirect=None, **kw):   
        name = kw.get('name')
        card_owner = kw.get('card_owner')     
        contact =  http.request.env['res.partner'].sudo().create({
            'name': name,             
        })   

        param =  http.request.env['param.profile'].sudo().create({
            'name': contact.id,   
            'card_owner': card_owner,          
        })
        return request.redirect("/success-page") 

class parmProfileReq(http.Controller):
       
    @http.route(['/param/json'], type="json", auth="public", methods=["POST"], cors='*', csrf=False)
    def get_json(self):
        data = json.loads(request.httprequest.data)

        contact =  http.request.env['res.partner'].sudo().create({
            'name': data['params']['name'],             
        }) 

        val = {
            'name': contact.id,
            'card_owner': data['params']['card_owner'],
            
            }

        create = request.env['param.profile'].sudo().create(val)
        result = {"code": 200, "message": "Created Successfully"}
        return result
 

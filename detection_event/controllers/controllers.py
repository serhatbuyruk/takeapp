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


class DetectionEventAPI(http.Controller): 


    @http.route('/api/detection_event/create', type="json", auth="public", methods=["POST"], cors='*', csrf=False)
    def pagate_order_callback(self):
        data = json.loads(request.httprequest.data)
        data_str = json.dumps(data).replace("'", " ")
        data = json.loads(data_str)
        try:

            event = request.env['detection_event.profile'].sudo().create({
                'name': data.get('name'),               
            
        

                # Yeni alanlar
                'device_name': data.get('device_name'),
                'ademco_id': data.get('ademco_id'),
                'zone': data.get('zone'),
                'event_date': data.get('create_time'),

            
            })

            return {'success': True, 'id': event.id}
        except Exception as e:
            return {'error': str(e)}
        
        
        
        
        
    # Python code
    @http.route('/web/auto_reload', type='json', auth='user')
    def auto_reload(self, model, **kwargs):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }    
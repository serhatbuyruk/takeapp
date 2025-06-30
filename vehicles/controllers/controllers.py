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


# class vehiclesProfileReq(http.Controller):

#     @http.route('/musait-saatler-bugun', type='http', auth="user", methods=["GET"], cors='*', website=True)
#     def musait_saatler_bugun(self):
#         return request.redirect("/musait-saatler?filter_start_date=" + str(datetime.now()))


# -*- coding: utf-8 -*-
import base64
import io
import os

from werkzeug.utils import redirect
from odoo import api, fields, models, _, http
from odoo.tools.misc import str2bool, xlwt, file_open
import time
from odoo.http import request


class CrmController(http.Controller):

    @http.route('/crm/call/record/<string:call_id>.mp3', auth='user')
    def get_mp3(self, call_id):
        call_db = http.request.env['crm_voip.crm.customer.call']
        sound = call_db.browse([int(call_id)])
        g = open(sound.call_record, 'rb')
        # image_base64 = base64.b64decode(g)
        image_data = io.BytesIO(g.read())
        response = http.send_file(image_data, filename="%s.mp3" % call_id, mimetype="audio/mp3", mtime=sound.write_date)
        # return str(os.stat(image.call_record).st_size)
        return response

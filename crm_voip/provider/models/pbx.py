# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from tempfile import gettempdir
from pydub import AudioSegment
from shutil import rmtree
import requests
import os
import uuid
import traceback


class CRMVoipPBX(models.Model):
    _name = 'crm_voip.providers.pbx'
    _rec_name = 'name'
    _description = 'Pbx'

    def _default_token(self):
        return uuid.uuid4().hex

    partner_id = fields.Many2one(comodel_name='res.partner', string='Operator', domain=[('is_company', '=', True)],
                                 required=True)
    name = fields.Char("Name")
    type = fields.Selection(string="Type", selection=[('netsantral', 'Netsantral')], required=True,
                            default='netsantral')
    server = fields.Char("Server")
    port = fields.Integer("Socket Port")
    username = fields.Char("Username")
    password = fields.Char("Password")
    number = fields.Char("Number")
    api_port = fields.Char("API Port")
    token = fields.Char("Token", default=_default_token)
    call_hook = fields.Char("Call Hook URL", compute='_compute_call_hook')

    @api.model
    def default_get(self, fields):
        res = super(CRMVoipPBX, self).default_get(fields)
        if self.env.user.partner_id.parent_id:
            res['partner_id'] = self.env.user.partner_id.parent_id.id
        return res

    def _compute_call_hook(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            record.call_hook = "%s/crm/netsantral/calllog/%s" % (base_url, record.token)

    @api.model
    def fetch_cron(self):
        for s in self.search([]):
            s.fetch_call_detail()
        self.env["crm_voip.sms.log"].match_customer()

    def call_phone(self, hotel, customer_number, internal_num):
        if hotel.callcenter_prefix:
            customer_number = hotel.callcenter_prefix + customer_number

        params = (
            ('username', self.username),
            ('password', self.password),
            ('customer_num', customer_number),
            ('ring_timeout', '60'),
            ('crm_id', '1'),
            ('internal_num', internal_num),
            ('wait_response', '1'),
            ('originate_order', 'if'),
            ('trunk', hotel.callcenter),
        )
        api_url = 'http://%s:%s/%s/originate' % (self.server, self.api_port, self.number)
        try:
            response = requests.get(api_url, params=params)
            return response.json()
        except:
            return {
                'message': 'error'
            }

    def fetch_button(self):
        for record in self:
            record.fetch_call_detail()

    def fetch_call_detail(self, start_date=None, end_date=None):
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = datetime.now() + timedelta(hours=3)
        xml = """<?xml version='1.0'?>
        <mainbody>
        <header>
        <company>Netgsm</company>
        <usercode>%s</usercode>
        <password>%s</password>
        <startdate>%s</startdate>
        <stopdate>%s</stopdate>
        <version>4</version>
        </header>
        </mainbody>""" % (self.username, self.password,
                          start_date.strftime("%d%m%Y%H%M"), end_date.strftime("%d%m%Y%H%M"))
        headers = {'Content-Type': 'application/xml'}
        response = requests.post('https://api.netgsm.com.tr/netsantral/report/xml', verify=False, data=xml, headers=headers)
        calls = response.content.decode("utf-8").split("<br/>")
        call_rows = []
        call_map = {}

        tmp = os.path.join(gettempdir(), '.{}'.format(hash(os.times())))
        tmp_folder_create = False

        def output_file(unique_id):
            unix_call_time =  unique_id
            if '-' in unique_id:
                unix_call_time = unique_id.split("-")[1]
            file_date = datetime.fromtimestamp(float(unix_call_time))
            root_folder = "/var/call_record"
            if not os.path.exists(root_folder):
                os.mkdir(root_folder)

            year_folder = os.path.join(root_folder, str(file_date.year))
            if not os.path.exists(year_folder):
                os.mkdir(year_folder)

            month_folder = os.path.join(year_folder, str(file_date.month))
            if not os.path.exists(month_folder):
                os.mkdir(month_folder)
            file_name = os.path.join(month_folder, "%s.mp3" % unique_id.replace('.', '_'))
            if os.path.exists(file_name):
                os.remove(file_name)
            return file_name

        def download_file(url, local_filename):
            with requests.get(url, stream=True, verify=False) as r:
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            return local_filename

        def time_to_second(time_in):
            if ':' not in time_in:
                return int(time_in)
            time_part = time_in.split(":")
            return int(time_part[0]) * 3600 + int(time_part[1]) * 60 + int(time_part[2])

        for c in calls:
            row = c.strip().split("|")
            if len(row) == 7:
                call_id = row[0]
                if call_id not in call_map:
                    call_map[call_id] = {}
                second = time_to_second(row[4])
                if second:
                    call_map[call_id]['duration'] = second
                if 'http' in row[6]:
                    call_map[call_id]['link'] = row[6]

        for unique_id, value in call_map.items():
            if value:
                value['unique_id'] = unique_id
                call_rows.append(value)

        for c in call_rows:
            call_record = self.env['crm_voip.crm.customer.call'].search([('partner_id', '=', self.partner_id.id), ('unique_id', '=', c['unique_id'])], limit=1)
            if call_record:
                update_value = {
                    'call_end': True,
                }
                # if call_record.duration == 0 and c['duration'] > 0:
                #     update_value['duration'] = c['duration']
                #     update_value['unanswered'] = False

                if not call_record.unanswered_first and call_record.duration == 0 and call_record.type == 'inbound':
                    update_value['unanswered_first'] = True
                    update_value['unanswered'] = True
                    self.env['bus.bus'].sudo().sendone("unanswered", "change")

                if not call_record.call_record and c.get('link', False):
                    update_value['call_record_source'] = c['link']
                    if not tmp_folder_create:
                        os.makedirs(tmp)
                        tmp_folder_create = True
                    temp_file = os.path.join(tmp, "%s.waw" % c['unique_id'])
                    download_file(c['link'], temp_file)
                    if os.path.exists(temp_file):
                        mp3_file = output_file(c['unique_id'])
                        try:
                            AudioSegment.from_wav(temp_file).export(mp3_file, format="mp3", bitrate="16k")
                        except:
                            traceback.print_exc()
                        if os.path.exists(mp3_file):
                            update_value['call_record'] = mp3_file

                if update_value:
                    call_record.write(update_value)
        if tmp_folder_create:
            rmtree(tmp, ignore_errors=True)

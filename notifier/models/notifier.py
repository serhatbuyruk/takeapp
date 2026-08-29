from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
cookie = "notifier"
import logging
_logger = logging.getLogger(__name__)
HTTP_TIMEOUT = (3, 15)

class notifierProfile(models.Model):
    _name = "notifier.profile"

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    sequence = fields.Integer(string="Sequence", default=1)
    latitude = fields.Float(string='Latitude')
    longitude = fields.Float(string='Longitude')

    @api.model
    def _log_push_deliveries(
        self,
        player_ids,
        title,
        message,
        channel='push',
    ):
        """Persist successful push recipients for the courier inbox."""
        normalized_player_ids = list({
            str(player_id).strip()
            for player_id in (player_ids or [])
            if player_id and str(player_id).strip()
        })
        if not normalized_player_ids:
            return self.env['notifier.delivery.log']

        try:
            with self.env.cr.savepoint():
                partners = self.env['res.partner'].sudo().search([
                    ('player_id', 'in', normalized_player_ids),
                ])
                source_id = self.env.context.get('notifier_source_id')
                source = (
                    self.env['notifier.profile'].sudo().browse(source_id).exists()
                    if source_id
                    else self.env['notifier.profile']
                )
                values_list = [
                    {
                        'partner_id': partner.id,
                        'source_notification_id': source.id or False,
                        'title': str(title or _('Notification')),
                        'message': str(message or ''),
                        'channel': channel,
                        'player_id_snapshot': partner.player_id,
                    }
                    for partner in partners
                ]
                if not values_list:
                    return self.env['notifier.delivery.log']
                return self.env['notifier.delivery.log'].sudo().create(
                    values_list
                )
        except Exception:
            _logger.exception(
                "Successful push could not be written to delivery log."
            )
            return self.env['notifier.delivery.log']

    @api.model
    def _send_http_request(self, method, url, **kwargs):
        """Keep notification failures from blocking or aborting business jobs."""
        kwargs.setdefault('timeout', HTTP_TIMEOUT)
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as error:
            _logger.warning(
                "Notification HTTP request failed: method=%s url=%s error=%s",
                method,
                url,
                error,
            )
            return False

    @api.model
    def send_Sms(self,usercode,password,msgheader,gsmno,message):
        url = 'https://api.netgsm.com.tr/sms/send/get?usercode='+ usercode + '&password=' + password + '&msgheader=' + msgheader + '&gsmno=' + gsmno + '&message=' + message
        x = self._send_http_request('GET', url)
        if not x:
            return False
        notifer = self.env['notifier.profile'].sudo().create({
                    'name': "SMS: " + str(gsmno) + " => " + str(message)
                })
        _logger.info("\nSMS: " + str(x.text) + " - " + str(x.status_code) + "\n")
        return True
        #-------------------------------------------------------------------
    
    @api.model
    def send_Push_Notification_With_Playerid(self,auth_key,app_id,player_ids,message):
        _logger = logging.getLogger(__name__)
        header = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {auth_key}',
                'Connection': "keep-alive",
                  }
        payload = {
                    "app_id": app_id,
                    "include_subscription_ids": player_ids,
                    #"headings": {"en": "Notification Title"},
                    "contents": {
                        "en": message
                    }
                }
        payload_json = json.dumps(payload)
        req = self._send_http_request(
            'POST',
            "https://onesignal.com/api/v1/notifications",
            headers=header,
            data=payload_json,
        )
        if not req:
            return False
        self._log_push_deliveries(
            player_ids,
            _('Notification'),
            message,
            channel='push',
        )
        _logger.info("OneSignal notification sent: status=%s", req.status_code)
        return True
        #-------------------------------------------------------------------

    @api.model
    def send_Push_Notification_With_Playerid_V1(self,auth_key,app_id,player_ids,headings,message):
        _logger = logging.getLogger(__name__)
        header = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {auth_key}',
                'Connection': "keep-alive",
                  }
        payload = {
                    "app_id": app_id,
                    "include_subscription_ids": player_ids,
                    "headings": {"en": headings},
                    "contents": {
                        "en": message
                    }
                }
        payload_json = json.dumps(payload)
        req = self._send_http_request(
            'POST',
            "https://onesignal.com/api/v1/notifications",
            headers=header,
            data=payload_json,
        )
        if not req:
            return False
        self._log_push_deliveries(
            player_ids,
            headings,
            message,
            channel='push',
        )
        _logger.info("OneSignal notification sent: status=%s", req.status_code)
        return True
        #-------------------------------------------------------------------

    @api.model
    def send_Push_Notification_With_Playerid_Voice(self,auth_key,app_id,player_ids,android_channel_id,category,ios_sound,android_sound,headings,message):
        _logger = logging.getLogger(__name__)
        header = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {auth_key}',
                'Connection': "keep-alive",
                  }
        payload = {
            "app_id": app_id,
            "headings": {
                "en": headings
            },
            "contents": {
                "en": message
            },
            "include_subscription_ids": player_ids,
            "target_channel": "push",
            "android_channel_id": android_channel_id,
            "category" : category,
            "ios_sound" : ios_sound,
            "android_sound": android_sound,
            "isIos": True,
            "isAndroid": True
        }
        payload_json = json.dumps(payload)
        req = self._send_http_request(
            'POST',
            "https://onesignal.com/api/v1/notifications",
            headers=header,
            data=payload_json,
        )
        if not req:
            return False
        self._log_push_deliveries(
            player_ids,
            headings,
            message,
            channel='voice_push',
        )
        _logger.info("OneSignal voice notification sent: status=%s", req.status_code)
        return True
        #-------------------------------------------------------------------

    @api.model
    def send_basic_voice_call(self,usercode,password,startdate,starttime,stopdate,stoptime,url,key,appkey,text,no_1,no_2,no_3,no_4,no_5,keyinfo1,text1,keyinfo2,text2,keyinfo3,text3):
        xml = f"""<?xml version='1.0'?>
        <mainbody>
            <header>
                <usercode>{usercode}</usercode>
                <password>{password}</password>
                <startdate>{startdate}</startdate>
                <starttime>{starttime}</starttime>
                <stopdate>{stopdate}</stopdate>
                <stoptime>{stoptime}</stoptime>
                <url>{url}</url>
                <key>{key}</key>   
                <appkey>{appkey}</appkey>       
            </header>
            <body>
                <text>{text}</text>
                <no>{no_1}</no>
                <no>{no_2}</no>
                <no>{no_3}</no>
                <no>{no_4}</no>
                <no>{no_5}</no>
                <keys>
                    <keydetail>
                        <keyinfo>{keyinfo1}</keyinfo>
                        <text>{text1}</text>
                    </keydetail>
                    <keydetail>
                        <keyinfo>{keyinfo2}</keyinfo>
                        <text>{text2}</text>
                    </keydetail>
                    <keydetail>
                        <keyinfo>{keyinfo3}</keyinfo>
                        <text>{text3}</text>
                    </keydetail>
                </keys>
            </body>
        </mainbody>
        """
        headers = {'Content-Type': 'application/xml'}
        req = self._send_http_request(
            'POST',
            'https://api.netgsm.com.tr/voicesms/send',
            data=xml.encode('utf-8'),
            headers=headers,
        )
        if not req:
            return False
        _logger.info("Netgsm voice call sent: status=%s", req.status_code)
        return True
        #-------------------------------------------------------------------




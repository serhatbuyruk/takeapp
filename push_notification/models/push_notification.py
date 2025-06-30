from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
cookie = "push_notification"
import logging
_logger = logging.getLogger(__name__)

class pushNotification(models.Model):
    _name = "push_notification.profile"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1) 

    personalized_message_status = fields.Boolean(string="Kişisel Mesaj Gönder")
    mass_message_status = fields.Boolean(string="Toplu Mesaj Gönder")

    personalized_name = fields.Char(string="Name")
    personalized_message = fields.Char(string="Message")
    person = fields.Many2one('res.partner', string="People")
    personalized_sequence = fields.Integer(string="Sequence", default=1)
    personalized_start_date = fields.Date(string="Start Date")
    personalized_end_date = fields.Date(string="End Date")
    personalized_upload_date = fields.Date(string="Upload Date", default=lambda self: fields.Date.today())

    personalized_send_sms_status = fields.Boolean(string="Kişiye SMS Gönder")
    personalized_send_push_notification_status = fields.Boolean(string="Kişiye Push Notification Gönder")

    mass_sms_send_status = fields.Boolean(string="Toplu SMS Gönder")
    mass_push_notification_send_status = fields.Boolean(string="Toplu Push Notification Gönder")     

    mass_name = fields.Char(string="Name")
    mass_message = fields.Char(string="Message")
    mass_sequence = fields.Integer(string="Sequence", default=1)
    mass_start_date = fields.Date(string="Start Date")
    mass_end_date = fields.Date(string="End Date")
    mass_upload_date = fields.Date(string="Upload Date", default=lambda self: fields.Date.today())

   
    
    

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError("Start date cannot be after end date.")

    @api.model
    def send_Sms(self,usercode,password,msgheader,gsmno,message):
        url = 'https://api.netgsm.com.tr/sms/send/get?usercode='+ usercode + '&password=' + password + '&msgheader=' + msgheader + '&gsmno=' + gsmno + '&message=' + message
        x = requests.get(url)
        """ notifer = self.env['push_notification.profile'].sudo().create({
                    'name': "SMS: " + str(gsmno) + " => " + str(message)
                }) """
        #_logger.info("\nSMS: " + str(x.text) + " - " + str(x.status_code) + "\n")
        return str(x.status_code) + " " + str(x.text)
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
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=payload_json)
        print(req.status_code, req.reason)
        _logger.info("\n" + str(auth_key) + " " + str(app_id) + " " + str(player_ids) + " " + str(message) + str(req.text) + str(req.status_code) + str(req.reason) + "\n")
        return True
        #-------------------------------------------------------------------

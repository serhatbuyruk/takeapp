from odoo import fields, models, api,_
from odoo.exceptions import UserError
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from odoo import http
from odoo.http import request
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)
import json
import socket
cookie = "aa"

class reportsProfile(models.Model):
    _name = "reports.profile"

    name = fields.Char(string="Name")
    ademco_id = fields.Char(string="Code")
    device_id = fields.Many2one('devices.profile', string="Device")
    date = fields.Datetime("Date")
    zone = fields.Integer(string="Zone")
    battery_level = fields.Integer(string="Battery Level")
    electricity_status = fields.Boolean(string="Battery Level")
    status = fields.Text(string="Status")
    report_importance = fields.Char(string="Report Importance")
    reports_image = fields.Binary(string="Image")

    @api.model
    def arrange_ademco_id_parameters(self,id,ademco_id):
        report = self.env['reports.profile'].sudo().search([('id', '=', id)])
        data_string = ademco_id.replace("'", '"')
        data_json = json.loads(data_string)
        report["device_id"]["ocpp_transaction_id"] = data_json['transactionInfo']['transaction_id']
        # report["device_id"]["phase_1_amper"] = data_json['meterValue'][0]['sampled_value'][0]['value']
        # report["device_id"]["phase_1_voltage"] = data_json['meterValue'][0]['sampled_value'][1]['value']
        # report["device_id"]["car_percentage"] = data_json['meterValue'][0]['sampled_value'][3]['value']
        # report["device_id"]["total_kw"] = data_json['meterValue'][0]['sampled_value'][4]['value']
        for meter in data_json.get('meterValue', []):
            for sampled_value in meter.get('sampled_value', []):
                if sampled_value.get('measurand') == 'Voltage':
                    report["device_id"]["phase_1_voltage"] = sampled_value.get('value')
                if sampled_value.get('measurand') == 'Current.Import':
                    report["device_id"]["phase_1_amper"] = sampled_value.get('value')
                if sampled_value.get('measurand') == 'Energy.Active.Import.Register':
                    report["device_id"]["total_kw"] = sampled_value.get('value')
                if sampled_value.get('measurand') == 'Power.Active.Import':
                    report["device_id"]["phase_1_power"] = sampled_value.get('value')
                if sampled_value.get('measurand') == 'SoC':
                    report["device_id"]["car_percentage"] = sampled_value.get('value')
        return True

    @api.model
    def send_Push_Notification_With_Playerid(self,auth_key,app_id,player_id,message):
        header = {"Content-Type": "application/json; charset=utf-8",
                  "Authorization": auth_key
                  }

        payload = {"app_id": app_id,
                "include_player_ids": player_id,
                "contents": {"en": message}}
        
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))

        #company = self.env['res.company'].sudo().search([('id','=', 1)])
        #company['x_example_data'] = str(req.status_code) + " " + str(req.reason)
        
        print(req.status_code, req.reason)
        
        return True

    @api.model
    def send_Sms(self,usercode,password,msgheader,gsmno,message):
        url = 'https://api.netgsm.com.tr/sms/send/get?usercode='+ usercode + '&password=' + password + '&msgheader=' + msgheader + '&gsmno=' + gsmno + '&message=' + message
        x = requests.get(url)
        return True
        #-------------------------------------------------------------------

    @api.model
    def send_Ademco_Id_To_Desi_Ahm(self,host,port,first_four_digit,subscriber_id,transmission_type,event_qualifier,event_code,group_number,zone_number,code):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
            response_from_socket = "no response from socket"
            s.settimeout(10)        
            try:
                s.connect((host, port))
                s.settimeout(None)
                socket_data = first_four_digit + " " + subscriber_id + transmission_type + event_qualifier + event_code + group_number + zone_number + " " + code + "\n"
                socket_data_encoded = bytes(socket_data,'UTF-8')
                s.sendall(socket_data_encoded)
                response_from_socket = s.recv(1024)  
            except socket.error as e:
                print(e)
            finally:
                print(f"Received {response_from_socket!r}")
                s.close()
        return True  
    
    @api.model
    def send_Ademco_Id_To_Teknim_Ahm(self,host,port,first_seven_digit,subscriber_id,event_qualifier,event_code,group_number,zone_number):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
            response_from_socket = "no response from socket"
            s.settimeout(10)        
            try:
                s.connect((host, port))
                s.settimeout(None)
                socket_data = first_seven_digit + "\"" + "ADM-CID\"0001L1#" + subscriber_id + "[#" + subscriber_id + "|18" + event_qualifier + event_code + group_number + zone_number + "4]" + "\n"
                socket_data_encoded = bytes(socket_data,'UTF-8')
                s.sendall(socket_data_encoded)
                response_from_socket = s.recv(1024)  
            except socket.error as e:
                print(e)
            finally:
                print(f"Received {response_from_socket!r}")
                s.close()
        return True
                                    


class ResPartnersInherit(models.Model):
    _inherit = 'res.partner'

    player_id = fields.Char("Player Id")
    tax_center = fields.Char(string="Tax Center")

    #gender = fields.Selection([('male','Male'),('female', 'Female'),('other', 'Other'),],string="Gender")
    #type_of_person = fields.Selection([('adult','Adult'),('child', 'Child'),('baby', 'Baby'),('driver', 'Driver')],string="Person Type")
    
    # How to OverRide Create Method Of a Model
    # https://www.youtube.com/watch?v=AS08H3G9x1U&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=26
    
    #@api.model
    #def create(self, vals_list):
    #    res = super(ResPartners, self).create(vals_list)
    #    print("yes working")
    #    # do the custom coding here
    #    return res

    
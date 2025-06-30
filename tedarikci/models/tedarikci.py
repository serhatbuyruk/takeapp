from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
cookie = "tedarikci"
import logging
_logger = logging.getLogger(__name__)
 

 


class tedarikci(models.Model):
    _name = "tedarikci.profile"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1)
         
    phone = fields.Char(string="Telefon")
    email = fields.Char(string="Email")
    vergi_dairesi = fields.Char(string="Vergi Dairesi")
    vergi_numarasi = fields.Char(string="Vergi Numarası")
    bakiye = fields.Float(string="Bakiye") 
    website = fields.Char(string="Website") 
    adress = fields.Char(string="Adres")
    city = fields.Char(string="Şehir")      
    upload_date = fields.Date(string="Yüklendiği Tarih", default=lambda self: fields.Date.today())

    @api.model
    def ewelink_get_request(self,getLink):
        response = requests.get(getLink)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Failed to retrieve data: {response.status_code}"
      

        
     
   
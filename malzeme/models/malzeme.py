from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
cookie = "malzeme"
import logging
_logger = logging.getLogger(__name__)


class malzeme(models.Model): 

    _name = "malzeme.profile"
      
    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1)  
    #product_name = fields.Char(string="Ürün Adı")
    product_model = fields.Char(string="Ürün Modeli")
    #contact = fields.Many2one('tedarikci.profile', string="contact")
    upload_date = fields.Date(string="Upload Date", default=lambda self: fields.Date.today())
    

 
   
from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
cookie = "stoktakibi"
import logging
_logger = logging.getLogger(__name__)

class tedarikci(models.Model):

    _name = "stoktakibi.profile"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1)
    products = fields.Many2one('malzeme.profile', string="Ürün Adı")
    suppliers = fields.Many2one('tedarikci.profile', string="Tedarikçi")
    number = fields.Integer(string="Adet")
    price = fields.Float(string="Fiyat")
    total  = fields.Float(string="Genel Toplam")
     
     
   
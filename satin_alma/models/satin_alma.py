from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
cookie = "satin_alma"
import logging
_logger = logging.getLogger(__name__)

class satin_alma(models.Model):
    
    _name = "satin_alma.profile"
    
    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1) 
    
    #products = fields.Many2one('malzeme.profile', string="Ürün Adı")
    #suppliers = fields.Many2one('tedarikci.profile', string="Tedarikçi")
    #number = fields.Integer(string="Adet")
    #price = fields.Float(string="Fiyat")
    #kdv = fields.Float(string="Kdv")
    '''kdv = fields.Selection([('0.1','%10'),('0.2','%20'),('mola','Mola')],
                                    string="Scan Type ", default=""
                                    )'''
    #kdv = fields.Many2many('res.users',relation='x_personel_profile_res_users_rel', column1='personel_users_id',column2='res_users_id', string="Users Can Edit")                                
    #total  = fields.Float(string="Genel Toplam")
    
     
   
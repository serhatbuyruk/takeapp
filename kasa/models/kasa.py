from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
 

cookie = "kasa"
import logging
_logger = logging.getLogger(__name__)

class kasa(models.Model):
    _name = "kasa.profile"

    name = fields.Char(string="Name")
    description = fields.Char(string="Açıklama")
    sequence = fields.Integer(string="Sequence", default=1)
    #firma_kasa = fields.Many2one('res.partner', string="Firma Kasası")

    total_money = fields.Float(string="Kasadaki O anki Total Para",  readonly=True)  
    upload_date = fields.Date(string="Yüklenen Tarih", default=lambda self: fields.Date.today(),readonly=True) 



    gelen_giden= fields.Selection([('gelen','Gelen'),('giden','Giden')],
                                    string="Gelen Giden Para ", default=""
                                    )


    tahsil = fields.Many2one('res.partner', string="Tahsil Eden")
    
    # Gelen Para
    gelen_payment_type = fields.Selection([('cash','Nakit'),('transfer','Havale'),('kart','Kredi Kartı')],
                                    string="Ödeme Türü", default=""
                                    )   
    gelen_money = fields.Float(string="Kaç Para Geldi")   
    gelen_company_name = fields.Many2one('res.partner', string="Firma Adı")
    #gelen_user_name = fields.Many2one('res.partner', string="Tahsil Eden")
   


    
    # Giden Para
    giden_payment_type = fields.Selection([('cash','Nakit'),('transfer','Havale'),('kart','Kredi Kartı')],
                                    string="Ödeme Türü", default=""
                                    )   
    giden_money = fields.Float(string="Kaç Para Gitti")   
    giden_company_name = fields.Many2one('res.partner', string="Firma Adı")
    #giden_user_name = fields.Many2one('res.partner', string="Tahsil Eden")





    


from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode

import logging

_logger = logging.getLogger(__name__)  # Odoo Logger

cookie = "ewelink_modul"

class ewelink_modulProfile(models.Model):
    _name = "ewelink_modul.profile"
    _description = "Röle Modul Model"

    name = fields.Char(string="Name")
    ewelink_modul_id = fields.Char(string="Id")
    sequence = fields.Integer(string="Sequence", default=1)
    visibility = fields.Boolean(string="Visibility", default=True) 
    title = fields.Char(string="Title")
    description = fields.Text(string="Açıklama")
    start_date = fields.Date(string="Başlangıç Tarihi")
    end_date = fields.Date(string="Bitiş Tarihi")
    state = fields.Selection([
        ('draft', 'Taslak'),
        ('active', 'Aktif'),
        ('done', 'Tamamlandı')
    ], string="Durum", default="draft")
    
    ewelink_modul_image = fields.Binary(string="Image")
    #is_late = fields.Boolean(string="is late") 
    
 
    url = fields.Char(string="Url")
    
    @api.model
    def fetch_data(self):
        
        """Her kayıt için URL'yi kullanarak API isteği yapar."""
        if not self.url:
            return "Hata: URL alanı boş!"

        try:
            response = requests.get(self.url)  # Field'dan URL alınıyor
            if response.status_code == 200:
                data = response.json()
                _logger.info(f"API Response: {data}")  # Odoo log'a yazdır
                return str(data)  # String olarak döndür
            else:
                error_msg = f"İstek başarısız. Hata kodu: {response.status_code}"
                _logger.error(error_msg)
                return error_msg
        except requests.RequestException as e:
            _logger.error(f"Bağlantı hatası: {e}")
            return f"Hata: {str(e)}"
    
    
    
"""  
   
   @api.model
    def fetch_data(self):
        
        if not self.url:
            _logger.error("URL alanı boş, istek atılamadı.")
            return {"error": "URL alanı boş, istek atılamadı."}

        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                data = response.json()

                # Odoo sistem loguna yazma
                self.env['ir.logging'].create({
                    'name': "API Request",
                    'type': "server",
                    'dbname': self.env.cr.dbname,
                    'level': "info",
                    'message': f"API'den dönen veri: {json.dumps(data, indent=4)}",
                    'path': "ewelink_modul/profile",
                    'line': "fetch_data",
                    'func': "fetch_data"
                })

                return data
            else:
                _logger.error(f"İstek başarısız. Hata kodu: {response.status_code}")

                # Odoo sistem loguna hata yazma
                self.env['ir.logging'].create({
                    'name': "API Request Error",
                    'type': "server",
                    'dbname': self.env.cr.dbname,
                    'level': "error",
                    'message': f"İstek başarısız. Hata kodu: {response.status_code}",
                    'path': "ewelink_modul/profile",
                    'line': "fetch_data",
                    'func': "fetch_data"
                })

                return {"error": f"İstek başarısız. Hata kodu: {response.status_code}"}
        except Exception as e:
            _logger.error(f"İstek sırasında hata oluştu: {str(e)}")

            # Odoo sistem loguna hata yazma
            self.env['ir.logging'].create({
                'name': "API Request Exception",
                'type': "server",
                'dbname': self.env.cr.dbname,
                'level': "error",
                'message': f"İstek sırasında hata oluştu: {str(e)}",
                'path': "ewelink_modul/profile",
                'line': "fetch_data",
                'func': "fetch_data"
            })

            return {"error": f"İstek sırasında hata oluştu: {str(e)}"}
 

 
"""


    
    

class Survey(models.Model):
    _inherit = 'survey.survey'

    # survey_ewelink = fields.Char(string="Ewelink Id",tracking=True)  
    survey_ewelink_modul_id = fields.Many2one('ewelink_modul.profile', string="Ewelink",tracking=True)
    lokasyon = fields.Char(string="Lokasyon",tracking=True)
    

    @api.model
    def create(self, vals):
        """Yeni bir anket oluşturulduğunda statik soruları ekler"""
        survey = super(Survey, self).create(vals)
        survey._create_static_questions()
        return survey

    def _create_static_questions(self):
        """Statik sorular otomatik olarak eklenecek."""
        static_questions = [
            {'title': 'Ad Soyad', 'question_type': 'char_box'},            
            {'title': 'TC Kimlik No', 'question_type': 'char_box'},
            {'title': 'Telefon Numarası', 'question_type': 'char_box'},
            {'title': 'Doğum Tarihi', 'question_type': 'date'},
        ]

        for question_data in static_questions:
            existing_question = self.env['survey.question'].search([
                ('title', '=', question_data['title']),
                ('survey_id', '=', self.id)
            ], limit=1)

            if not existing_question:
                self.env['survey.question'].create({
                    'title': question_data['title'],
                    'question_type': question_data['question_type'],
                    'survey_id': self.id,
                    'is_page': False,  # Normal soru olarak ekle
                    'sequence': 0,  # Her zaman ilk sırada olsun
                    'constr_mandatory': True,
                    'constr_error_msg': 'Lütfen Boş geçmeyin',
                })



class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    first_name = fields.Char(string="Ad", required=True)
    last_name = fields.Char(string="Soyad", required=True)
    tc_number = fields.Char(string="TC Kimlik No", required=True)
    phone_number = fields.Char(string="Telefon Numarası")
    birth_date = fields.Date(string="Doğum Tarihi")
    
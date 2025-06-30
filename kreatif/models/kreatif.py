from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
cookie = "kreatif"

class kreatifProfile(models.Model):
    _name = "kreatif.profile"
    _description = "API Integration Example"

    name = fields.Char(string="Name")
    data = fields.Text(string="Response Data", readonly=True)


    price = fields.Float(string="Price")
    image_url = fields.Char(string="Image URL")

    sequence = fields.Integer(string="Sequence", default=1)
    visibility = fields.Boolean(string="Visibility", default=True)
    image_type = fields.Selection([('kreatif','kreatif'),('service','Service'),('notification','Notification')],
                                    string="Image Type ", default="kreatif"
                                    )
    title = fields.Char(string="Title")
    description = fields.Char(string="Description")
    kreatif_image = fields.Binary(string="Image")  
   
    company_id = fields.Many2one('res.company', string="Company")

    # Muhammet tarafından eklenen fields
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
   
    paid = fields.Boolean(string="Paid")
    upload_date = fields.Date(string="Upload Date", default=lambda self: fields.Date.today())
    company_name = fields.Char(string="Company Name")
    topic = fields.Char(string="Topic")
    
    
    @api.model
    def call_api(self):
        # API URL
        url = "http://www.birikimpromosyon.com/api/json/"

        # API payload
        payload = {
            "ebayi_eposta": "info@kreatifcozumler.com",
            "hash": "892cfb16ebbdbdd8abb3630810a0792f",
            "tip": "tum_kategoriler"
        }

        # Headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "kreatifcozumler.com",
        }

        try:
            # API request
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()  # Check for HTTP errors
            response_data = response.json()

            # İşlenen veriyi kaydetmek için
            self.env["kreatif.profile"].create({
                "name": "API Call Result",
                "data": json.dumps(response_data, indent=4),
            })
            return response_data
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


    @api.model
    def get_api(self):
        # API URL'si
        url = "http://www.birikimpromosyon.com/api/json/"

        # E-Bayi verileri
        hash_code = "892cfb16ebbdbdd8abb3630810a0792f"
        ebayi_email = "info@kreatifcozumler.com"
        website_url = "kreatifcozumler.com"  # www olmadan

        # Sorgu parametreleri
        query_type = "tum_kategoriler"
        sort_type = "kategori_id"
        sort_order = "DESC"

        # POST verisi
        payload = {
            "ebayi_eposta": ebayi_email,
            "hash": hash_code,
            "tip": query_type,
            "siralama_tipi": sort_type,
            "siralama": sort_order,
        }

        # Header bilgisi
        headers = {
            "Content-Type": "application/json",
            "User-Agent": website_url,
        }

        # HTTP POST isteği
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
            response.raise_for_status()  # HTTP hataları için kontrol
            print(response.json())  # Gelen JSON veriyi yazdır
        except requests.exceptions.RequestException as e:
            print(f"API isteğinde hata oluştu: {e}")
     

     

    
    

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError("Start date cannot be after end date.")

        
 


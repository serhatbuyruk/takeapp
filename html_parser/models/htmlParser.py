from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode

from html.parser import HTMLParser
from bs4 import BeautifulSoup

cookie = "html_parser"
import logging
_logger = logging.getLogger(__name__)

class htmlParser(models.Model):
    _name = "html_parser.profile"
    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    sequence = fields.Integer(string="Sequence", default=1)



    @api.model
    def get_html_code(self,html_code, tag_name, attribute_name=None, attribute_value=None):
        
        """
        Example: 1 
        <body>
            <img src="https://example.com/image.jpg" alt="Örnek Resim">
        </body>

        Metod çağırırken
        HTML içeriğinden belirli bir nitelik değerine sahip etiketi al
        img_src = get_html_code(html_content, 'img', 'src', 'https://example.com/image.jpg')


        Example: 2
        <body>
            <h1>Bu bir başlık</h1>
            <p>Bu bir paragraf.</p>
            <a href="http://www.example.com">Bu bir link</a>
        </body>

        HTML içeriğinden belirli bir değeri al        
        h1_content = get_html_code(html_content, 'h1')
        print("H1 İçeriği:", h1_content)

        link_href = get_html_code(html_content, 'a', 'href')
        print("Link HREF Değeri:", link_href)

        """
        
        soup = BeautifulSoup(html_code, 'html.parser')

        if attribute_name and attribute_value:
                       
            tag = soup.find(tag_name, {attribute_name: attribute_value})
        else:
            tag = soup.find(tag_name)

        if not tag:
            return None  

        if attribute_name:
            return tag.get(attribute_name)
        else:
            return tag.get_text(strip=True)      

    @api.model
    def get_abone_info(self,html_code):

        # HTML içeriğini BeautifulSoup ile analiz et
        soup = BeautifulSoup(html_code, 'html.parser')
        
        # Tüm tablo satırlarını al
        rows = soup.find_all('tr')

        # Abone bilgileri için boş bir sözlük oluştur
        abone_bilgileri = {}
        
        # Her bir satırı işle
        for row in rows:
            # Satırdaki hücreleri al
            cells = row.find_all('td')
          
            # Hücrelerin içeriğini alarak abone kodu ve abone ünvanını bul            
            for cell in cells:
                cell_content = cell.get_text(strip=True)
                
                if 'Abone Kodu' in cell_content:
                    #abone_bilgileri['abone_kodu'] = cells[2].get_text(strip=True)
                    full_code = cells[2].get_text(strip=True)
                    abone_kodu = full_code.split('-')[0]  # "-" karakterine göre böl ve ilk kısmı al
                    abone_bilgileri['abone_kodu'] = abone_kodu

                elif 'Abone Ünvanı' in cell_content:
                    abone_bilgileri['abone_unvani'] = cells[2].get_text(strip=True)

                elif 'Operatör Notu' in cell_content:    
                    abone_bilgileri['operator_notu'] = cells[-1].get_text(strip=True)
                    
                elif 'Operatör' in cell_content:
                    abone_bilgileri['operator'] = cells[-1].get_text(strip=True)    

        return abone_bilgileri




    


 


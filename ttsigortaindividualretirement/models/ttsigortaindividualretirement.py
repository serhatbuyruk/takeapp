from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode

 
from bs4 import BeautifulSoup

cookie = "ttsigortaindividualretirement"
import logging
_logger = logging.getLogger(__name__)

class ttsigortaindividualretirement(models.Model):
    _name = "ttsigortaindividualretirement.profile"
    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    sequence = fields.Integer(string="Sequence", default=1)






    


 


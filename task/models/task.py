from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode

from html.parser import HTMLParser
from bs4 import BeautifulSoup

cookie = "task"
import logging
_logger = logging.getLogger(__name__)

class task(models.Model):
    _name = "task.profile"
    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    sequence = fields.Integer(string="Sequence", default=1)

    @api.model
    def create_project_task(self, servis_notu, contacts_id, user_id):
        task = self.env['project.task'].create({
            'project_id': 8,
            'name': servis_notu,
            'x_customer': contacts_id,
            'user_ids': [(4, user_id)],
        })
        
        # Log yazdırma
        tools.logger.info('New project task created: %s by user: %s', task.name, user_id)
        
        return task






    


 


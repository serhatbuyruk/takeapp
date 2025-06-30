from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime,timedelta
from base64 import b64encode
cookie = "personalize"
import math
import time
import random
import string

class personalizeProfile(models.Model):
    _name = 'personalize.profile'
    _description = 'Personalize Record'

    name = fields.Char("Name", translate=True)
    description = fields.Text("Description", translate=True)
    line_sequence = fields.Integer(string="Sequence")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")


class personalizeProfileLines(models.Model):
    _name = 'personalize.profile.lines'
    _description = 'Vehicle Lines Record'

    name = fields.Char("Name", translate=True)
    options = fields.Many2many('personalize.profile',relation='x_personalize_profile_lines_rel', column1='personalize_lines_users_id',column2='personalize_lines_users_id_2', string="Options")
    accepted = fields.Boolean(string='Accepted', default=False)
    active = fields.Boolean(string='Active', default=True)
    line_sequence = fields.Integer(string="Sequence")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")
    
    
class cordersProfileInherit(models.Model):
    _inherit = 'corders.profile'

    personalize_profile_lines = fields.One2many('personalize.profile.lines', 'sequence', string='Personalization Lines',tracking=True, copy=False)
    
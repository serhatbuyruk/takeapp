from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime,timedelta
from base64 import b64encode
cookie = "zones"
import math
import time
import random
import string

class zonesProfile(models.Model):
    _name = 'zones.profile'
    _description = 'Zones Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char("Name", translate=True)
    description = fields.Text("Description", translate=True)
    country_id = fields.Many2one('res.country', string="Country", default=lambda self: self.env.ref('base.us'))  # ABD varsayılan
    state_id = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=', country_id)]")
    county = fields.Char("County")  # ABD'de genelde Many2one değil, çünkü Odoo’da default county modeli yok
    city = fields.Char("City")
    zip_code = fields.Char("ZIP Code")
    polygons_char = fields.Char(string="Polygons Coordinates")
    polygons_json = fields.Json(string="Polygons Coordinates (Json)")
    sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=2, tracking=True)
    base_price = fields.Float("Base Price ($)", currency_field='sale_price_currency_id', tracking=True)
    per_mile_price = fields.Float("Per Mile Price ($)", currency_field='sale_price_currency_id', tracking=True)
    active_status = fields.Boolean(string="Active Status", default=True)
    out_of_area = fields.Boolean(string="Out of Area", default=False)
    line_sequence = fields.Integer(string="Sequence")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")


    

    base_fare = fields.Float("Base Fare ($)", required=True)
    per_mile_rate = fields.Float("Per Mile Rate ($)", required=True)
    is_active = fields.Boolean(default=True)
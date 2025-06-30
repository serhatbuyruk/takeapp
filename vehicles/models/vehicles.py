from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime,timedelta
from base64 import b64encode
cookie = "vehicles"
import math
import time
import random
import string

class vehiclesProfile(models.Model):
    _name = "vehicles.profile"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name" ,tracking=True)
    plate = fields.Char(string="Plate")
    code = fields.Char(string="Code")
    color = fields.Integer(string="Color")
    sequence = fields.Integer(string="Sequence", default=1)
    vehicle_sequence = fields.Integer(string="Vehicle Sequence", default=1)
    active_status = fields.Boolean(string="Active Status", default=True, tracking=True)
    type = fields.Many2one('type.profile', string="Type",tracking=True)


    # product_id = fields.Many2one('product.product', string="Product/Service",tracking=True)
    # product_status = fields.Selection([('available','Available'),('busy','Busy')],
    #                                 string="Product Status", default="available"
    #                                 )
    #delivery_details = fields.Char(string="Rezervasyon Notları", tracking=True)
    

    #turkey_entrance_datetime = fields.Datetime(string="Turkey Entrance",tracking=True)
    # saleperson = fields.Many2one('res.partner', string="Saleperson",tracking=True)
    # gemici = fields.Many2one('res.partner', string="Gemici",tracking=True)
    # dealer = fields.Many2one('res.partner', string="Dealer",tracking=True)
    # driver_status = fields.Boolean(string="Driver Status", tracking=True)
    # driver = fields.Many2one('res.partner', string="Driver",tracking=True)
    # car_petrol_status = fields.Selection([('1','1/4'),('2','2/4'),('3','3/4'),('4','4/4')],
    #                                 string="Car Petrol Status", default="4", tracking=True
    #                                 )
    #contracts_attachment_ids = fields.Many2many('ir.attachment','attachment_rel_contracts_vehicles','pro_id_contracts_vehicles','attach_id_contracts_vehicles', string='Contracts',) 
    
    # repeat_count = fields.Integer(string="Repeat Count", tracking=True)
    # repeat_status = fields.Boolean(string="Repeat Status", tracking=True)
    # repeat_type = fields.Selection([('once','Once'),('day','Day'),('week','Week'),('Month','Month'),('year','Year')],
    #                                 string="Repeat Type", default="once", tracking=True
    #                                 )
    # sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=32, tracking=True)
    # sale_price = fields.Monetary(string="Sale Price", currency_field='sale_price_currency_id', tracking=True)
    # deposit_price_currency_id = fields.Many2one('res.currency', string='Deposit Currency',default=32, tracking=True)
    # deposit_price = fields.Monetary(string="Deposit Price", currency_field='deposit_price_currency_id', tracking=True)
    # sale_description = fields.Char(string="Sale Description", tracking=True)
    # received_amount_currency_id = fields.Many2one('res.currency', string='Received Amount Currency',default=32, tracking=True)
    # received_amount = fields.Monetary(string="Received Amount", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_1 = fields.Monetary(string="Received Amount-1", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_2 = fields.Monetary(string="Received Amount-2", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_3 = fields.Monetary(string="Received Amount-3", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_4 = fields.Monetary(string="Received Amount-4", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_5 = fields.Monetary(string="Received Amount-5", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_6 = fields.Monetary(string="Received Amount-6", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_7 = fields.Monetary(string="Received Amount-7", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_8 = fields.Monetary(string="Received Amount-8", currency_field='received_amount_currency_id', tracking=True)
    # received_amount_total = fields.Monetary(string="Received Amount Total", currency_field='received_amount_currency_id', tracking=True)
    # remaining_amount_currency_id = fields.Many2one('res.currency', string='Remaining Amount Currency',default=32, tracking=True)
    # remaining_amount = fields.Monetary(string="Remaining Amount", currency_field='remaining_amount_currency_id', tracking=True)
    # commission_rate = fields.Float(string="Commission Rate", tracking=True)
    # commission_amount_currency_id = fields.Many2one('res.currency', string='Commission Currency %',default=32, tracking=True)
    # commission_amount = fields.Monetary(string="Commission Amount", currency_field='commission_amount_currency_id', tracking=True)
    # customer_payment_status = fields.Selection([('not_paid','Not Paid'),('in_payment','In Payment'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
    #                                 string="Customer Payment Status ", default="not_paid", tracking=True
    #                                 )
    # invoice_status = fields.Selection([('draft','Draft'),('posted','Posted'),('canceled','Canceled')],
    #                                 string="Customer Invoice Status ", default="draft", tracking=True
    #                                 )
    # sale_payment_receiver = fields.Many2one('res.partner', string="Payment Receiver",tracking=True)
    # sale_payment_type = fields.Selection([('bank','Bank'),('cash','Cash')],
    #                                 string="Payment Type", default="cash", tracking=True
    #                                 )
    # attachment_ids = fields.Many2many('ir.attachment','attachment_rel_1_vehicles','pro_id_1_vehicles','attach_id_1_vehicles', string='Attachments',) 
    

    # scan_date = fields.Datetime(string="Scan Date")
    # entry_date = fields.Datetime(string="Entry Date")
    # exit_date = fields.Datetime(string="Exit Date")
    
    # email = fields.Char(string="Email")
    # tc = fields.Char(string="TC")
    # mobile = fields.Char(string="Mobile")
    # company_id = fields.Many2one('res.company', string="Company")
    # parent_id = fields.Many2one('res.partner', string="Related Company")
    # scan_type = fields.Selection([('entry','Entry'),('exit','Exit'),('mola','Mola')],
    #                                 string="Scan Type ", default=""
    #                                 )
    # lat = fields.Float(string="Latitude", digits=(12, 6))
    # lng = fields.Float(string="Longitude", digits=(12, 6))
    # working_hours = fields.Float(string="Working Hours")
    # working_minutes = fields.Integer(string="Working Minutes")
    # distance = fields.Integer(string="Distance")
    # suspect_level = fields.Integer(string="Suspect Level")
    # suspect_level_entry = fields.Integer(string="Suspect Level Entry")
    # suspect_level_exit = fields.Integer(string="Suspect Level Exit")

    # contact_name = fields.Char(string="Contact Name")
    # company_name = fields.Char(string="Company Name")
    # street = fields.Char(string="Street")
    # city = fields.Char(string="City")
    # state = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=', country_id)]")
    # country_id = fields.Many2one('res.country', string="Country")
    
    # acenta = fields.Char(string="Acenta")

    # product_type = fields.Selection([('araba','Araba'),('yat','Yat'),('bungolov','Bungalov')],
    #                                 string="Ürün Tipi", default="", tracking=True) 

    
    def from_profile(self):
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'vehicles.profile',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]'
        }


class vehiclesProfileLines(models.Model):
    _name = 'vehicles.profile.lines'
    _description = 'Vehicle Lines Record'

    name = fields.Char("Name")
    type = fields.Many2one('type.profile', string="Type",tracking=True)
    vehicle = fields.Many2one('vehicles.profile', string="Vehicle",tracking=True)
    partner_id = fields.Many2one('res.partner', string='Driver')

    model_year = fields.Integer(string='Model Year')
    vehicle_color = fields.Char(string='Color')
    license_plate = fields.Char(string='License Plate')
    vehicle_photo = fields.Image(string='Vehicle Photo')

    vin_number = fields.Char(string='VIN Number')
    registration_document = fields.Binary(string='Registration Document')
    insurance_document = fields.Binary(string='Insurance Document')
    inspection_document = fields.Binary(string='Inspection Report')

    seat_count = fields.Integer(string='Number of Seats')
    fuel_type = fields.Selection([
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ], string='Fuel Type')

    is_owner = fields.Boolean(string='Owner')
    owner_name = fields.Char(string='Owner Name', help='If different from driver')

    active = fields.Boolean(string='Active', default=True)
    line_sequence = fields.Integer(string="Sequence")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")
    current_vehicle = fields.Boolean(string='Current Vehicle', default=False)
    accepted = fields.Boolean(string='Accepted', default=False)
    
    
class resPartnerProfileInherit(models.Model):
    _inherit = 'res.partner'

    vehicles_profile_lines = fields.One2many('vehicles.profile.lines', 'partner_id', string='Vehicle Lines',tracking=True, copy=False)
    
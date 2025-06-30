# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime


# Creating Model/Table to Store Doctor Details
# https://www.youtube.com/watch?v=L6MxDR71_1k&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=2
class typeProfile(models.Model):
    _name = 'type.profile'
    _description = 'Type Record'

    name = fields.Char("Name" ,tracking=True)
    description = fields.Text("Description")
    sequence = fields.Integer(string="Sequence")
    type_sequence = fields.Integer(string="Type Sequence")
    color = fields.Integer(string="Color")
    image = fields.Image(string="Image")
    max_passenger = fields.Integer(string="Max Passenger" ,tracking=True)
    active_status = fields.Boolean(string="Active Status", default=True)


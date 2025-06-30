# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Creating Model/Table to Store Doctor Details
# https://www.youtube.com/watch?v=L6MxDR71_1k&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=2
class stageApp(models.Model):
    _name = 'stage.app'
    _description = 'Box Record'

    name = fields.Char("Name")
    description = fields.Text("Description")
    image_1 = fields.Binary(string="Image 1")
    sequence = fields.Integer(string="Sequence")
    color = fields.Char(string="Color")
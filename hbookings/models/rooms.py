# -*- coding: utf-8 -*-

from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime


# Creating Model/Table to Store Doctor Details
# https://www.youtube.com/watch?v=L6MxDR71_1k&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=2
class roomsTracker(models.Model):
    _name = 'rooms.tracker'
    _description = 'Tracker Record'
    _order = "order_sequence"

    name = fields.Char("Name")
    is_active = fields.Boolean(string='Is Active', default=True)
    order_sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")
    
class roomsTrackerLines(models.Model):
    _name = 'rooms.tracker.lines'
    _description = 'Tracker Lines Record'
    _order = "order_sequence"

    name = fields.Many2one('rooms.tracker', string='Name')
    currency_id = fields.Many2one('res.currency', string='Currency Id')
    price = fields.Monetary(string="Amount", currency_field='currency_id')
    description = fields.Text("Description")
    rooms_tracker_status = fields.Selection([('not_received','Not Received'),('received','Received')],
                                    string="Documents Status ", default="not_received"
                                    )
    rooms_status = fields.Boolean(string='Status')
    rooms_attachment_ids = fields.Many2many('ir.attachment','attachment_rel_rooms_lines','pro_id_rooms_lines','attach_id_rooms_lines', string='Documents',)
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    order_sequence = fields.Integer(string="Sequence")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")

    def from_profile(self):
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'hbookings.profile',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]'
        }
    
    
class hbookingsProfileInherit(models.Model):
    _inherit = 'hbookings.profile'

    room = fields.Many2one('rooms.tracker', string='Room')

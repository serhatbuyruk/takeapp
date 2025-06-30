# -*- coding: utf-8 -*-

from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime


# Creating Model/Table to Store Doctor Details
# https://www.youtube.com/watch?v=L6MxDR71_1k&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=2
class documentsTracker(models.Model):
    _name = 'documents.tracker'
    _description = 'Tracker Record'
    _order = "order_sequence"

    name = fields.Char("Name")
    is_active = fields.Boolean(string='Is Active', default=True)
    order_sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")
    
class documentsTrackerLines(models.Model):
    _name = 'documents.tracker.lines'
    _description = 'Tracker Lines Record'
    _order = "order_sequence"

    name = fields.Many2one('documents.tracker', string='Name')
    currency_id = fields.Many2one('res.currency', string='Currency Id')
    price = fields.Monetary(string="Amount", currency_field='currency_id')
    description = fields.Text("Description")
    documents_tracker_status = fields.Selection([('not_received','Not Received'),('received','Received')],
                                    string="Documents Status ", default="not_received"
                                    )
    documents_status = fields.Boolean(string='Status')
    documents_attachment_ids = fields.Many2many('ir.attachment','attachment_rel_doc_lines','pro_id_doc_lines','attach_id_doc_lines', string='Documents',)
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
            'res_model': 'alphaashleybookings.profile',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]'
        }
    
    
class alphaashleybookingsProfileInherit(models.Model):
    _inherit = 'alphaashleybookings.profile'

    documents_tracker_lines = fields.One2many('documents.tracker.lines', 'sequence', string='Documents Tracker',tracking=True)

    @api.model
    def default_get(self, fields_list):
        res = super(alphaashleybookingsProfileInherit, self).default_get(fields_list)
        # Varsayılan order_line ekleyelim
        documents_ids = self.env['documents.tracker'].search([('is_active', '=', True)]).mapped('id')

        documents = [(0, 0, {
            'name': documents_id
        }) for documents_id in documents_ids]

        res.update({'documents_tracker_lines': documents})
        return res
    
    @api.onchange('documents_tracker_lines')
    def documents_tracker_lines_changed(self):
        document_status = "not_received"
        all_true = all(line["documents_status"] for line in self.documents_tracker_lines)
        all_false = all(not line["documents_status"] for line in self.documents_tracker_lines)
        if all_true:
            document_status = "received"
            self["document_status"] = document_status
        elif all_false:
            document_status = "not_received"
            self["document_status"] = document_status
        else:
            document_status = "partial_received"
            self["document_status"] = document_status
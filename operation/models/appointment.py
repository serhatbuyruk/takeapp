# -*- coding: utf-8 -*-

from odoo import models, fields, api


# Creating Model/Table to Store Doctor Details
# https://www.youtube.com/watch?v=L6MxDR71_1k&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=2
class appointmentApp(models.Model):
    _name = 'appointment.app'
    _description = 'Appointment Record'

    name = fields.Char("Name")
    description = fields.Text("Description")
    image_1 = fields.Binary(string="Image 1")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")
    appointment_lines = fields.One2many('appointment.app.lines', 'id', string='Appointments')
    
class appointmentAppLines(models.Model):
    _name = 'appointment.app.lines'
    _description = 'App Lines Record'

    appointment_start_time = fields.Datetime(string="Appointment Start Date And Time")
    appointment_finish_time = fields.Datetime(string="Appointment Finish Date And Time")
    patient_coming_status = fields.Boolean("Coming Status")
    doctor = fields.Many2one('res.partner', string="Doctor")
    box = fields.Char("Box")
    description = fields.Text("Description")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")

class projectTaskInherit(models.Model):
    _inherit = 'project.task'

    appointment_lines = fields.One2many('appointment.app.lines', 'sequence', string='Appointments')
from odoo import fields, models


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'model.signature']

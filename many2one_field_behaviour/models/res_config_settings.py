from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    many2one_field_behaviour = fields.Selection([
        ('0', 'Odoo Default'),
        ('1', 'New Tab'),
        ('2', 'Show Popup'),
    ], 'Many2one Field Behaviour Action',
        config_parameter='many2one_field_behaviour.many2one_field_behaviour',
        help="""0: Use Odoo Default Action.
                1: Open New Browser Tab.
                2: Show Popup In Current Tab.""",
        default='0')


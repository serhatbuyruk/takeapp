# wizard/confirmation_wizard.py
from odoo import models, fields, api

class ConfirmationWizard(models.TransientModel):
    _name = 'detection.event.confirmation.wizard'
    _description = 'Olay Onay Sihirbazı'

    comment = fields.Text(string="Yorum")
    severity = fields.Selection([
        ('info', 'Bilgi'),
        ('warning', 'Uyarı'),
        ('critical', 'Kritik')],
        string="Öncelik", default='info'
    )

    def action_confirm(self):
        active_id = self.env.context.get('active_id')
        event = self.env['detection_event.profile'].browse(active_id)
        event.write({
            'acknowledged': True,
            'ack_date': fields.Datetime.now(),
            'ack_user_id': self.env.user.id,
            'ack_comment': self.comment,
            'severity': self.severity
        })
        return {'type': 'ir.actions.act_window_close'}

    
    '''
    comment = fields.Text(string="Yorum")
    
    def action_confirm(self):
        active_id = self.env.context.get('active_id')
        event = self.env['detection_event.profile'].browse(active_id)
        event.write({
            'acknowledged': True,
            'ack_date': fields.Datetime.now(),
            'ack_user_id': self.env.user.id,
            'ack_comment': self.comment
        })
        return {'type': 'ir.actions.act_window_close'}
    '''    
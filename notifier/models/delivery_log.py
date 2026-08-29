from odoo import fields, models


class NotifierDeliveryLog(models.Model):
    _name = 'notifier.delivery.log'
    _description = 'Notifier Delivery Log'
    _order = 'sent_at desc, id desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Recipient',
        required=True,
        index=True,
        ondelete='cascade',
    )
    source_notification_id = fields.Many2one(
        'notifier.profile',
        string='Source Notification',
        index=True,
        ondelete='set null',
    )
    title = fields.Char(string='Title', required=True)
    message = fields.Text(string='Message', required=True)
    channel = fields.Selection(
        [
            ('push', 'Push'),
            ('voice_push', 'Voice Push'),
        ],
        string='Channel',
        required=True,
        default='push',
    )
    player_id_snapshot = fields.Char(
        string='Player ID Snapshot',
        readonly=True,
    )
    sent_at = fields.Datetime(
        string='Sent At',
        required=True,
        default=fields.Datetime.now,
        index=True,
    )


from odoo import api, fields, models


class MailRtcSession(models.Model):
    _inherit = 'mail.channel.rtc.session'

    @api.model_create_multi
    def create(self, vals_list):
        sessions = super().create(vals_list)
        calls = self.env['partner.courier.call'].sudo().search([
            ('channel_id', 'in', sessions.channel_id.ids),
            ('state', 'in', ['waiting', 'ringing']),
        ])
        now = fields.Datetime.now()
        for call in calls:
            session_count = len(call.channel_id.sudo().rtc_session_ids)
            if session_count >= 2:
                call.write({
                    'state': 'active',
                    'answered_at': call.answered_at or now,
                    'ringing_at': call.ringing_at or now,
                })
            elif session_count == 1:
                call.write({
                    'state': 'ringing',
                    'ringing_at': call.ringing_at or now,
                })
        return sessions

    def unlink(self):
        calls = self.env['partner.courier.call'].sudo().search([
            ('channel_id', 'in', self.channel_id.ids),
            ('state', '=', 'active'),
        ])
        result = super().unlink()
        now = fields.Datetime.now()
        for call in calls:
            if len(call.channel_id.sudo().rtc_session_ids) < 2:
                call.write({
                    'state': 'ended',
                    'ended_at': now,
                })
        return result

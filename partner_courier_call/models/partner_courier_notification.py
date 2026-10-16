from odoo import models


class PartnerCourierNotification(models.Model):
    _inherit = 'partner.courier.notification'

    def _prepare_onesignal_payload(self, app_id, subscription_ids):
        payload = super()._prepare_onesignal_payload(app_id, subscription_ids)
        data = payload.get('data') or {}
        actions = data.get('notification_actions')
        if not isinstance(actions, list):
            return payload

        mobile_buttons = []
        web_buttons = []
        for action in actions[:2]:
            if not isinstance(action, dict):
                continue
            action_id = action.get('id')
            text = action.get('text')
            url = action.get('url')
            if not action_id or not text:
                continue
            mobile_buttons.append({'id': action_id, 'text': text})
            if url:
                web_buttons.append({'id': action_id, 'text': text, 'url': url})

        mobile_actions_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'partner_courier_call.mobile_notification_actions_enabled',
            'True',
        ) == 'True'
        if mobile_buttons and mobile_actions_enabled:
            payload['buttons'] = mobile_buttons
        if web_buttons:
            payload['web_buttons'] = web_buttons
        return payload

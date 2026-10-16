import base64
import json

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    partner_courier_notification_provider = fields.Selection(
        [('onesignal', 'OneSignal'), ('firebase', 'Firebase Cloud Messaging')],
        string='Varsayılan Bildirim Servisi', default='onesignal',
        config_parameter='partner_courier_notification.provider',
    )

    partner_courier_onesignal_app_id = fields.Char(
        string='OneSignal App ID',
        config_parameter='partner_courier_notification.onesignal_app_id',
    )
    partner_courier_onesignal_api_key = fields.Char(
        string='OneSignal API Key',
        config_parameter='partner_courier_notification.onesignal_api_key',
    )
    partner_courier_firebase_project_id = fields.Char(
        string='Firebase Proje ID',
        config_parameter='partner_courier_notification.firebase_project_id',
    )
    partner_courier_firebase_service_account = fields.Binary(
        string='Firebase Servis Hesabı JSON',
        help='Firebase Console üzerinden indirilen servis hesabı JSON dosyası.',
    )
    partner_courier_firebase_service_account_filename = fields.Char(
        string='Dosya Adı',
    )

    def get_values(self):
        values = super().get_values()
        attachment_id = self.env['ir.config_parameter'].sudo().get_param(
            'partner_courier_notification.firebase_service_account_attachment_id'
        )
        attachment = self.env['ir.attachment'].sudo().browse(int(attachment_id or 0)).exists()
        if attachment:
            values.update({
                'partner_courier_firebase_service_account': attachment.datas,
                'partner_courier_firebase_service_account_filename': attachment.name,
            })
        return values

    def set_values(self):
        super().set_values()
        self.ensure_one()
        if not self.partner_courier_firebase_service_account:
            return
        try:
            raw_data = base64.b64decode(self.partner_courier_firebase_service_account)
            payload = json.loads(raw_data.decode('utf-8'))
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValidationError(_('Lütfen geçerli bir Firebase servis hesabı JSON dosyası yükleyin.')) from exc
        if not isinstance(payload, dict) or not payload.get('client_email') or not payload.get('private_key'):
            raise ValidationError(_('Yüklenen dosya Firebase servis hesabı JSON dosyası değil.'))

        params = self.env['ir.config_parameter'].sudo()
        attachment_model = self.env['ir.attachment'].sudo()
        attachment = attachment_model.browse(int(params.get_param(
            'partner_courier_notification.firebase_service_account_attachment_id', '0'
        ) or 0)).exists()
        values = {
            'name': self.partner_courier_firebase_service_account_filename or 'firebase-service-account.json',
            'datas': self.partner_courier_firebase_service_account,
            'mimetype': 'application/json',
            'res_model': 'ir.config_parameter',
            'res_id': 0,
            'public': False,
        }
        if attachment:
            attachment.write(values)
        else:
            attachment = attachment_model.create(values)
            params.set_param('partner_courier_notification.firebase_service_account_attachment_id', attachment.id)

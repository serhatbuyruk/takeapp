from odoo import _, fields, models
from odoo.exceptions import UserError


class PartnerCourierIbanUpdateWizard(models.TransientModel):
    _name = 'partner.courier.iban.update.wizard'
    _description = 'Toplu Kurye Ödeme Bilgileri Güncelleme Sihirbazı'

    payment_person = fields.Char(string='Para Yatacak Kişi Adı Soyadı')
    payment_person_tc = fields.Char(string='Para Yatacak Kişi T.C. No')
    iban = fields.Char(string='IBAN Bilgisi')
    bank_branch = fields.Char(string='Şube Kodu')
    bank_account_no = fields.Char(string='Hesap No')
    bank_name = fields.Char(string='Banka Adı')

    def action_update_iban(self):
        self.ensure_one()
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids') or []
        if active_model != 'res.partner' or not active_ids:
            raise UserError(_('Lütfen güncellenecek contact kayıtlarını seçin.'))

        fields_to_update = [
            'payment_person',
            'payment_person_tc',
            'iban',
            'bank_branch',
            'bank_account_no',
            'bank_name',
        ]
        vals = {
            field_name: (self[field_name] or '').strip()
            for field_name in fields_to_update
            if (self[field_name] or '').strip()
        }
        if not vals:
            raise UserError(_('Lütfen güncellenecek en az bir ödeme bilgisi alanı doldurun.'))

        partners = self.env['res.partner'].browse(active_ids).exists()
        if not partners:
            raise UserError(_('Güncellenecek contact kaydı bulunamadı.'))

        partners.write(vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Toplu Ödeme Bilgileri Güncelleme'),
                'message': _('%s contact kaydının ödeme bilgileri güncellendi.') % len(partners),
                'type': 'success',
                'sticky': False,
            },
        }

from odoo import fields, models


class PartnerCourierApplication(models.Model):
    _name = 'partner.courier.application'
    _description = 'Kurye Başvurusu'
    _order = 'create_date desc, id desc'

    name = fields.Char(string='Ad Soyad', required=True, index=True)
    email = fields.Char(string='E-posta', required=True, index=True)
    state = fields.Selection([
        ('pending', 'Değerlendirmede'),
        ('contacted', 'İletişime Geçildi'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Uygun Bulunmadı'),
    ], string='Durum', required=True, default='pending', index=True)

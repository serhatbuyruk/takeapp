from odoo import api, fields, models


class PartnerCourierRequest(models.Model):
    _name = 'partner.courier.request'
    _description = 'Kurye Talebi'
    _order = 'create_date desc, id desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Kurye',
        required=True,
        ondelete='cascade',
        index=True,
    )
    type = fields.Selection([
        ('advance', 'Avans Talebi'),
        ('equipment', 'Ekipman Talebi'),
        ('shift', 'Vardiya / Bölge Değişikliği'),
        ('holiday', 'İzin Talebi'),
        ('accounting', 'Hakediş İtirazı / Muhasebe'),
        ('other', 'Diğer'),
    ], string='Talep Tipi', required=True, default='advance')

    description = fields.Text(string='Talep Açıklaması', required=True)
    response = fields.Text(string='Yönetici Açıklaması / Cevap')
    state = fields.Selection([
        ('new', 'Yeni'),
        ('progress', 'İşleme Alındı'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ], string='Durum', default='new', required=True)

    def name_get(self):
        result = []
        for record in self:
            type_label = dict(self._fields['type'].selection).get(record.type, '')
            name = f"{record.partner_id.name or ''} - {type_label} (#{record.id})"
            result.append((record.id, name))
        return result

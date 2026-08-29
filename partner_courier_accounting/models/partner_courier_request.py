from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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
    courier_id = fields.Char(
        string='Kurye ID',
        related='partner_id.courier_id',
        store=True,
        readonly=True,
    )
    courier_tc = fields.Char(
        string='Kurye T.C. No',
        related='partner_id.courier_tc',
        store=True,
        readonly=True,
    )
    type = fields.Selection([
        ('advance', 'Avans Talebi'),
        ('equipment', 'Ekipman Talebi'),
        ('shift', 'Vardiya / Bölge Değişikliği'),
        ('holiday', 'İzin Talebi'),
        ('accounting', 'Hakediş İtirazı / Muhasebe'),
        ('other', 'Diğer'),
    ], string='Talep Tipi', required=True, default='advance')

    requested_amount = fields.Float(string='Talep Edilen Tutar')
    description = fields.Text(string='Talep Açıklaması', required=True)
    response = fields.Text(string='Yönetici Açıklaması / Cevap')
    state = fields.Selection([
        ('new', 'Yeni'),
        ('progress', 'İşleme Alındı'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ], string='Durum', default='new', required=True)

    @api.constrains('type', 'requested_amount')
    def _check_requested_amount(self):
        for record in self:
            if record.type == 'advance' and record.requested_amount <= 0:
                raise ValidationError(_('Avans taleplerinde talep edilen tutar 0 değerinden büyük olmalıdır.'))

    def name_get(self):
        result = []
        for record in self:
            type_label = dict(self._fields['type'].selection).get(record.type, '')
            name = f"{record.partner_id.name or ''} - {type_label} (#{record.id})"
            result.append((record.id, name))
        return result

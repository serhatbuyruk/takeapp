from odoo import fields, models


class PartnerCourierStartNotification(models.Model):
    _name = 'partner.courier.start.notification'
    _description = 'Kurye İş Başı Bildirimi'
    _order = 'submitted_at desc, id desc'

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
    start_date = fields.Date(string='İşe Başlama Tarihi', required=True, index=True)
    submitted_at = fields.Datetime(
        string='Bildirim Tarihi',
        required=True,
        default=fields.Datetime.now,
        readonly=True,
    )
    state = fields.Selection([
        ('new', 'Yeni'),
        ('progress', 'İşleme Alındı'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    ], string='Durum', required=True, default='new', index=True)
    handled_by = fields.Many2one('res.users', string='İşlemi Yapan', readonly=True, copy=False)
    team_note = fields.Text(string='Ekip Notu')

    def name_get(self):
        result = []
        for record in self:
            label = '%s - %s' % (
                record.partner_id.name or '',
                fields.Date.to_string(record.start_date) if record.start_date else '',
            )
            result.append((record.id, label))
        return result

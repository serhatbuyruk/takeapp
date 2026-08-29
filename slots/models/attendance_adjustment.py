from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ShiftAttendanceAdjustment(models.Model):
    _name = 'slots.puantaj.duzeltme'
    _description = 'Vardiya Puantaj Eki'
    _order = 'attendance_date desc, id desc'

    line_id = fields.Many2one(
        'skurye.profile.lines', string='Kurye Vardiyası', required=True,
        ondelete='cascade', index=True,
    )
    slot_id = fields.Many2one(
        'slots.profile', string='Vardiya', required=True,
        ondelete='cascade', index=True,
    )
    restaurant_id = fields.Many2one(
        'res.partner', string='Restoran', required=True,
        ondelete='restrict', index=True,
    )
    courier_id = fields.Many2one(
        related='line_id.partner_id', string='Kurye', store=True, index=True,
    )
    attendance_date = fields.Date(
        string='Puantaj Tarihi', required=True, index=True,
    )
    extra_hours = fields.Float(string='Ek Çalışma Saati', default=0.0)
    extra_packages = fields.Integer(string='Ek Paket Sayısı', default=0)
    note = fields.Text(string='Açıklama')
    created_by_id = fields.Many2one(
        'res.users', string='Ekleyen', required=True,
        default=lambda self: self.env.user, readonly=True,
    )

    @api.constrains('extra_hours', 'extra_packages')
    def _check_values(self):
        for record in self:
            if record.extra_hours < 0 or record.extra_packages < 0:
                raise ValidationError(_('Ek saat ve paket negatif olamaz.'))
            if not record.extra_hours and not record.extra_packages:
                raise ValidationError(
                    _('En az bir ek çalışma saati veya paket sayısı girin.')
                )

    def _refresh_earnings(self, lines=None):
        target_lines = lines or self.mapped('line_id')
        submitted = target_lines.filtered('kurye_paket_beyani_yapildi')
        if submitted:
            submitted._refresh_package_reconciliation_earnings()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._refresh_earnings()
        return records

    def write(self, vals):
        old_lines = self.mapped('line_id')
        result = super().write(vals)
        self._refresh_earnings(old_lines | self.mapped('line_id'))
        return result

    def unlink(self):
        lines = self.mapped('line_id')
        result = super().unlink()
        submitted = lines.filtered('kurye_paket_beyani_yapildi')
        if submitted:
            submitted._refresh_package_reconciliation_earnings()
        return result


class SkuryeProfileLines(models.Model):
    _inherit = 'skurye.profile.lines'

    puantaj_duzeltme_ids = fields.One2many(
        'slots.puantaj.duzeltme', 'line_id', string='Puantaj Ekleri', copy=False,
    )
    puantaj_ek_saat = fields.Float(
        string='Toplam Ek Saat', compute='_compute_puantaj_totals', store=True,
    )
    puantaj_ek_paket_sayisi = fields.Integer(
        string='Toplam Ek Paket', compute='_compute_puantaj_totals', store=True,
    )

    @api.depends(
        'puantaj_duzeltme_ids.extra_hours',
        'puantaj_duzeltme_ids.extra_packages',
    )
    def _compute_puantaj_totals(self):
        for line in self:
            line.puantaj_ek_saat = sum(
                line.puantaj_duzeltme_ids.mapped('extra_hours')
            )
            line.puantaj_ek_paket_sayisi = sum(
                line.puantaj_duzeltme_ids.mapped('extra_packages')
            )

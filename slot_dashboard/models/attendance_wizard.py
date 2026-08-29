from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SlotDashboardAttendanceWizard(models.TransientModel):
    _name = 'slot.dashboard.attendance.wizard'
    _description = 'Vardiya Puantaj Ekleme Sihirbazı'

    attendance_date = fields.Date(
        string='Puantaj Tarihi', required=True,
        default=fields.Date.context_today,
    )
    courier_id = fields.Many2one(
        'res.partner', string='Kurye', required=True,
        domain=[('user_role', '=', 'kurye')],
    )
    available_line_ids = fields.Many2many(
        'skurye.profile.lines', compute='_compute_available_lines',
    )
    shift_line_id = fields.Many2one(
        'skurye.profile.lines', string='Kurye Vardiyası', required=True,
        domain="[('id', 'in', available_line_ids)]",
    )
    restaurant_id = fields.Many2one(
        'res.partner', string='Restoran', compute='_compute_restaurant',
        readonly=True,
    )
    extra_hours = fields.Float(string='Ek Çalışma Saati', default=0.0)
    extra_packages = fields.Integer(string='Ek Paket Sayısı', default=0)
    note = fields.Text(string='Açıklama')

    def _available_lines(self):
        self.ensure_one()
        if not self.attendance_date or not self.courier_id:
            return self.env['skurye.profile.lines']
        _date, timezone, utc_start, utc_end = (
            self.env['slots.profile']._operation_dashboard_day_bounds(
                self.attendance_date
            )
        )
        restaurants = self.env['res.partner'].sudo().search([
            ('user_role', '=', 'magaza'),
            ('operation_dashboard_enabled', '=', True),
        ])
        slots = self.env['slots.profile'].sudo().search([
            ('start_date', '<', utc_end),
            ('end_date', '>=', utc_start),
            '|',
            ('magazalar', 'in', restaurants.ids),
            ('partner_id', 'in', restaurants.ids),
        ])
        lines = self.env['skurye.profile.lines'].sudo().search([
            ('sequence', 'in', slots.ids),
            ('partner_id', '=', self.courier_id.id),
        ], order='kurye_start_date, id')
        return lines.filtered(lambda line: (
            line._courier_planned_period()[1]
            and self.env['slots.profile']._operation_dashboard_localize(
                line._courier_planned_period()[1], timezone
            ).date() == self.attendance_date
        ))

    @api.depends('attendance_date', 'courier_id')
    def _compute_available_lines(self):
        for wizard in self:
            wizard.available_line_ids = wizard._available_lines()

    @api.depends('shift_line_id')
    def _compute_restaurant(self):
        for wizard in self:
            slot = self.env['slots.profile'].browse(
                wizard.shift_line_id.sequence
            ).exists()
            wizard.restaurant_id = (
                (slot.magazalar | slot.partner_id).filtered(
                    'operation_dashboard_enabled'
                )[:1]
                if slot else False
            )

    @api.onchange('attendance_date', 'courier_id')
    def _onchange_shift_scope(self):
        self.shift_line_id = False
        lines = self._available_lines()
        if len(lines) == 1:
            self.shift_line_id = lines

    def action_apply(self):
        self.ensure_one()
        self.env['slots.profile']._operation_dashboard_check_access()
        available_lines = self._available_lines()
        if self.shift_line_id not in available_lines:
            raise ValidationError(
                _('Seçilen kurye vardiyası tarih/restoran kapsamıyla uyuşmuyor.')
            )
        if self.extra_hours < 0 or self.extra_packages < 0:
            raise ValidationError(_('Ek saat ve paket negatif olamaz.'))
        if not self.extra_hours and not self.extra_packages:
            raise ValidationError(
                _('En az bir ek çalışma saati veya paket sayısı girin.')
            )
        slot = self.env['slots.profile'].browse(
            self.shift_line_id.sequence
        ).exists()
        if not slot or not self.restaurant_id:
            raise ValidationError(_('Vardiyanın dashboard restoranı bulunamadı.'))
        self.env['slots.puantaj.duzeltme'].create({
            'line_id': self.shift_line_id.id,
            'slot_id': slot.id,
            'restaurant_id': self.restaurant_id.id,
            'attendance_date': self.attendance_date,
            'extra_hours': self.extra_hours,
            'extra_packages': self.extra_packages,
            'note': self.note,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Puantaj eklendi'),
                'message': _('%s için ek saat ve paket hakedişe yansıtıldı.')
                % self.shift_line_id.partner_id.name,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

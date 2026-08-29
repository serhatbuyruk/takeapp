from datetime import datetime, time, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SlotDashboardManualShiftWizard(models.TransientModel):
    _name = 'slot.dashboard.manual.shift.wizard'
    _description = 'Manuel Vardiya Ekleme'

    shift_date = fields.Date(
        string='Vardiya Tarihi',
        required=True,
        default=fields.Date.context_today,
    )
    restaurant_id = fields.Many2one(
        'res.partner',
        string='Restoran',
        required=True,
        domain="[('user_role', '=', 'magaza'), ('active', '=', True)]",
    )
    courier_id = fields.Many2one(
        'res.partner',
        string='Kurye',
        required=True,
        domain="[('user_role', '=', 'kurye'), ('active', '=', True)]",
    )
    start_hour = fields.Float(
        string='Vardiya Giriş',
        required=True,
        default=9.0,
    )
    end_hour = fields.Float(
        string='Vardiya Çıkış',
        required=True,
        default=18.0,
    )
    region = fields.Char(string='Bölge')
    branch = fields.Char(string='Şube')

    def _check_access(self):
        self.env['slots.profile']._operation_dashboard_check_access()

    @staticmethod
    def _float_to_time(value, label):
        if value is None or value < 0 or value >= 24:
            raise ValidationError(
                _('%s 00:00 ile 23:59 arasında olmalıdır.') % label
            )
        total_minutes = int(round(value * 60))
        if total_minutes >= 24 * 60:
            raise ValidationError(
                _('%s 00:00 ile 23:59 arasında olmalıdır.') % label
            )
        hour, minute = divmod(total_minutes, 60)
        return time(hour=hour, minute=minute)

    def _planned_period(self):
        self.ensure_one()
        timezone_name = self.env.user.tz or 'Europe/Istanbul'
        try:
            timezone = pytz.timezone(timezone_name)
        except pytz.UnknownTimeZoneError:
            timezone = pytz.timezone('Europe/Istanbul')

        start_time = self._float_to_time(
            self.start_hour,
            _('Vardiya giriş saati'),
        )
        end_time = self._float_to_time(
            self.end_hour,
            _('Vardiya çıkış saati'),
        )
        local_start_value = datetime.combine(self.shift_date, start_time)
        if start_time == time.min:
            local_start_value += timedelta(seconds=1)
        local_start = timezone.localize(local_start_value)

        if end_time == time.min:
            local_end = timezone.localize(datetime.combine(
                self.shift_date,
                time.max.replace(microsecond=0),
            ))
        else:
            local_end = timezone.localize(datetime.combine(
                self.shift_date,
                end_time,
            ))
            if local_end <= local_start:
                local_end += timedelta(days=1)

        return (
            local_start.astimezone(pytz.UTC).replace(tzinfo=None),
            local_end.astimezone(pytz.UTC).replace(tzinfo=None),
        )

    @staticmethod
    def _overlaps(start_a, end_a, start_b, end_b):
        return start_a < end_b and end_a > start_b

    @staticmethod
    def _restaurant_address(restaurant):
        parts = [
            restaurant.street,
            restaurant.street2,
            restaurant.city,
            restaurant.state_id.name,
            restaurant.country_id.name,
        ]
        return ' '.join(part for part in parts if part) or restaurant.name

    @staticmethod
    def _weekday_key(plan_date):
        return (
            'pazartesi',
            'sali',
            'carsamba',
            'persembe',
            'cuma',
            'cumartesi',
            'pazar',
        )[plan_date.weekday()]

    def _has_package_activity(self, line, slot):
        if (
            line.slot_paket_sayisi > 0
            or line.kurye_paket_beyani_yapildi
            or line.paket_mutabakat_durumu not in (False, 'not_submitted')
        ):
            return True
        restaurants = slot.magazalar | slot.partner_id
        if not restaurants:
            return False
        return bool(self.env['corders.profile'].sudo().search_count([
            ('kurye', '=', line.partner_id.id),
            ('magaza', 'in', restaurants.ids),
            ('siparis_tarihi', '>=', slot.start_date),
            ('siparis_tarihi', '<=', slot.end_date),
            ('siparis_durumu', '!=', 'iptal_edildi'),
        ]))

    def _find_target_slot(self, day_start, day_end):
        slots = self.env['slots.profile'].sudo().search([
            ('slot_tipi', '=', 'sabit'),
            ('start_date', '<', day_end),
            ('end_date', '>', day_start),
            '|',
            ('magazalar', 'in', self.restaurant_id.ids),
            ('partner_id', '=', self.restaurant_id.id),
        ], order='id')
        if len(slots) > 1:
            raise ValidationError(
                _(
                    '%(restaurant)s için bu tarihte birden fazla ana vardiya '
                    'bulundu (%(slots)s). Yanlış kayda ekleme yapmamak için '
                    'önce çakışan vardiyaları düzeltin.'
                ) % {
                    'restaurant': self.restaurant_id.name,
                    'slots': ', '.join('#%s' % slot.id for slot in slots),
                }
            )
        return slots[:1]

    def _check_courier_overlap(
        self,
        planned_start,
        planned_end,
        target_slot,
        existing_line,
    ):
        slot_model = self.env['slots.profile'].sudo()
        candidate_slots = slot_model.search([
            ('start_date', '<', planned_end),
            ('end_date', '>', planned_start),
        ])
        lines = self.env['skurye.profile.lines'].sudo().search([
            ('sequence', 'in', candidate_slots.ids),
            ('partner_id', '=', self.courier_id.id),
        ])
        slots_by_id = {slot.id: slot for slot in candidate_slots}
        for line in lines:
            if existing_line and line == existing_line:
                continue
            slot = slots_by_id.get(line.sequence)
            if not slot:
                continue
            line_start = line.kurye_start_date or slot.start_date
            line_end = line.kurye_end_date or slot.end_date
            if (
                line_start
                and line_end
                and self._overlaps(
                    planned_start,
                    planned_end,
                    line_start,
                    line_end,
                )
            ):
                raise ValidationError(
                    _(
                        '%(courier)s, “%(slot)s” (#%(slot_id)s) vardiyasıyla '
                        'aynı saatlerde çalışıyor. Çakışan manuel vardiya '
                        'eklenemez.'
                    ) % {
                        'courier': self.courier_id.name,
                        'slot': slot.name,
                        'slot_id': slot.id,
                    }
                )

    def action_save_shift(self):
        self.ensure_one()
        self._check_access()
        if not self.shift_date:
            raise ValidationError(_('Vardiya tarihini seçin.'))
        if not self.restaurant_id.lat or not self.restaurant_id.lng:
            raise ValidationError(
                _(
                    '%s restoranının başlangıç koordinatları eksik. Önce '
                    'restoran kartındaki konumu tamamlayın.'
                ) % self.restaurant_id.name
            )
        active_user = self.env['res.users'].sudo().search([
            ('partner_id', '=', self.courier_id.id),
            ('active', '=', True),
        ], limit=1)
        if not active_user:
            raise ValidationError(
                _(
                    '%s için aktif bir Odoo kullanıcı hesabı bulunamadı. '
                    'Kurye frontendden vardiyaya giriş yapamaz.'
                ) % self.courier_id.name
            )

        self.env.cr.execute(
            "SELECT pg_advisory_xact_lock(hashtext(%s))",
            ['slot_dashboard.shift_import'],
        )
        planned_start, planned_end = self._planned_period()
        _target_date, _timezone, day_start, day_end = (
            self.env['slots.profile']._operation_dashboard_day_bounds(
                self.shift_date
            )
        )
        target_slot = self._find_target_slot(day_start, day_end)
        existing_lines = (
            target_slot.skurye_profile_lines.filtered(
                lambda line: line.partner_id == self.courier_id
            ).sorted('id')
            if target_slot
            else self.env['skurye.profile.lines']
        )
        # Aynı kurye aynı gün içinde birden fazla, çakışmayan vardiyada
        # çalışabilir. Yalnız aynı saat aralığındaki satır güncellenir.
        matching_lines = existing_lines.filtered(lambda line: (
            (line.kurye_start_date or target_slot.start_date) == planned_start
            and (line.kurye_end_date or target_slot.end_date) == planned_end
        )) if target_slot else existing_lines
        if len(matching_lines) > 1:
            raise ValidationError(
                _(
                    '%s aynı saat aralığında birden fazla kez kayıtlı. Manuel '
                    'güncellemeden önce bu mükerrer satırları düzeltin.'
                ) % self.courier_id.name
            )
        existing_line = matching_lines[:1]
        if (
            existing_line
            and self._has_package_activity(existing_line, target_slot)
            and (
                existing_line.kurye_start_date != planned_start
                or existing_line.kurye_end_date != planned_end
            )
        ):
            raise ValidationError(
                _(
                    '%s bu vardiyada paket taşımaya başladığı için planlanan '
                    'giriş/çıkış saatleri değiştirilemez.'
                ) % self.courier_id.name
            )

        self._check_courier_overlap(
            planned_start,
            planned_end,
            target_slot,
            existing_line,
        )

        batch = self.env['slot.dashboard.shift.import.batch'].sudo().create({
            'name': _('%s - Manuel Vardiya') % fields.Datetime.now(),
            'filename': _('Manuel Dashboard Kaydı'),
        })
        restaurant = self.restaurant_id.sudo()
        restaurant_values = {}
        if restaurant.slot_tipi != 'sabit':
            restaurant_values['slot_tipi'] = 'sabit'
        if not restaurant.operation_dashboard_enabled:
            restaurant_values['operation_dashboard_enabled'] = True
        if restaurant_values:
            restaurant.write(restaurant_values)

        line_values = {
            'partner_id': self.courier_id.id,
            'kurye_start_date': planned_start,
            'kurye_end_date': planned_end,
            'shift_import_batch_id': batch.id,
            'shift_plan_date': self.shift_date,
            'shift_plan_region': self.region or restaurant.state_id.name,
            'shift_plan_project': restaurant.name,
            'shift_plan_branch': self.branch or restaurant.city,
            'active': True,
        }
        slot_values = {
            'name': _('%s Vardiyası') % restaurant.name,
            'slot_tipi': 'sabit',
            'magazalar': [(6, 0, restaurant.ids)],
            'start_date': day_start,
            'end_date': day_end - timedelta(seconds=1),
            'lat': restaurant.lat,
            'lng': restaurant.lng,
            'slot_acik_adresi': self._restaurant_address(restaurant),
            'calisma_gunu': self._weekday_key(self.shift_date),
            'active_status': day_end > fields.Datetime.now(),
        }
        created_slot = False
        precreated_line = self.env['skurye.profile.lines']
        if target_slot:
            # Boş parent vardiyayı yazmak automation_20'nin boş kurye
            # kontrolüne takılır. İlk satırı önce ekle; devamındaki herhangi
            # bir hata aynı transaction içinde bu kaydı da geri alır.
            if not target_slot.skurye_profile_lines:
                precreated_line = self.env['skurye.profile.lines'].sudo().create({
                    **line_values,
                    'sequence': target_slot.id,
                })
                target_slot.invalidate_recordset(['skurye_profile_lines'])
            if not target_slot.shift_import_batch_id:
                slot_values['shift_import_batch_id'] = batch.id
            target_slot.write(slot_values)
        else:
            slot_values['shift_import_batch_id'] = batch.id
            # The slot validation automation requires at least one courier
            # at create time.  Create the parent and its first courier line
            # atomically, as the Excel import path does.
            slot_values['skurye_profile_lines'] = [(0, 0, line_values)]
            target_slot = self.env['slots.profile'].sudo().create(slot_values)
            created_slot = True

        if existing_line:
            if not existing_line.start_date:
                line_values.update({
                    'kurye_active': planned_end > fields.Datetime.now(),
                    'end_date': False,
                })
            else:
                # Never reactivate a courier line which has already started
                # or completed; only its safe plan metadata is updated.
                line_values.pop('active')
            existing_line.sudo().write(line_values)
        elif not created_slot and not precreated_line:
            self.env['skurye.profile.lines'].sudo().create({
                **line_values,
                'sequence': target_slot.id,
            })

        batch.write({
            'slot_count': 1 if created_slot else 0,
            'updated_slot_count': 0 if created_slot else 1,
            'shift_count': 1,
            'skipped_count': 0,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Vardiya kaydedildi'),
                'message': _(
                    '%(courier)s, %(restaurant)s vardiyasına eklendi veya '
                    'mevcut planı güncellendi.'
                ) % {
                    'courier': self.courier_id.name,
                    'restaurant': restaurant.name,
                },
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

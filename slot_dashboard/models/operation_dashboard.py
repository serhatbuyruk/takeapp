from datetime import datetime, time, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class RestaurantOperationDashboard(models.Model):
    _inherit = 'res.partner'

    operation_dashboard_enabled = fields.Boolean(
        string='Operasyon Dashboardu',
        default=False,
        help=(
            'Operasyon dashboardu yalnız bu alanı açık restoranların '
            'vardiyalarını ve kuryelerini gösterir.'
        ),
    )


class SlotOperationDashboard(models.Model):
    _inherit = 'slots.profile'

    @staticmethod
    def _operation_dashboard_courier_status(statuses):
        if statuses == {'upcoming'}:
            return 'upcoming'
        if 'missing' in statuses:
            return 'missing'
        if 'late' in statuses:
            return 'late'
        return 'on_time'

    @staticmethod
    def _operation_dashboard_group_rows(rows, group_key=None):
        """Return mutually exclusive, courier-based operational totals."""
        grouped = {}
        for row in rows:
            group_name = row[group_key] if group_key else '__all__'
            courier_statuses = grouped.setdefault(group_name, {}).setdefault(
                row['courier_id'],
                set(),
            )
            courier_statuses.add(row['status'])

        summaries = []
        for group_name, couriers in grouped.items():
            summary = {
                'name': group_name,
                'planned': len(couriers),
                'due': 0,
                'arrived': 0,
                'on_time': 0,
                'late': 0,
                'missing': 0,
                'upcoming': 0,
                'entry_rate': 0,
            }
            for statuses in couriers.values():
                courier_status = (
                    SlotOperationDashboard
                    ._operation_dashboard_courier_status(statuses)
                )
                summary[courier_status] += 1

            summary['due'] = summary['planned'] - summary['upcoming']
            summary['arrived'] = summary['on_time'] + summary['late']
            if summary['due']:
                summary['entry_rate'] = round(
                    summary['arrived'] * 100 / summary['due']
                )
            summaries.append(summary)

        return sorted(
            summaries,
            key=lambda item: (
                -item['missing'],
                -item['late'],
                item['name'],
            ),
        )

    @api.model
    def _operation_dashboard_is_admin(self):
        user = self.env.user
        return (
            user.has_group('base.group_system')
            or user.has_group('slots.slots_group_admin')
            or user.has_group('slots.slots_group_fullaccess')
            or user.has_group('corders.corders_group_admin')
            or user.has_group('corders.corders_group_fullaccess')
        )

    @api.model
    def _operation_dashboard_check_access(self):
        if not self._operation_dashboard_is_admin():
            raise AccessError(
                _('Operasyon dashboardunu yalnızca yöneticiler görüntüleyebilir.')
            )

    @api.model
    def get_attendance_adjustment_action(self, selected_date=False):
        """Open attendance additions for the selected dashboard day."""
        self._operation_dashboard_check_access()
        try:
            target_date = (
                fields.Date.to_date(selected_date)
                if selected_date else fields.Date.context_today(self)
            )
        except (TypeError, ValueError):
            raise ValidationError(_('Geçerli bir puantaj tarihi seçin.'))
        action = self.env.ref(
            'slot_dashboard.action_attendance_adjustment_list'
        ).sudo().read()[0]
        action['domain'] = [
            ('attendance_date', '=', fields.Date.to_string(target_date)),
            ('restaurant_id.operation_dashboard_enabled', '=', True),
        ]
        action['name'] = _('%s Puantaj Kayıtları') % target_date.strftime(
            '%d.%m.%Y'
        )
        return action

    @api.model
    def get_operation_shift_line_action(self, line_id):
        """Open only the selected courier shift line, never its parent slot."""
        self._operation_dashboard_check_access()
        try:
            line_id = int(line_id)
        except (TypeError, ValueError):
            raise ValidationError(_('Geçerli bir kurye vardiyası seçin.'))

        line = self.env['skurye.profile.lines'].browse(line_id).exists()
        if not line:
            raise ValidationError(_('Kurye vardiyası bulunamadı.'))
        slot = self.browse(line.sequence).exists()
        if not slot:
            raise ValidationError(
                _('Kurye satırının bağlı olduğu ana vardiya bulunamadı.')
            )
        scoped_restaurants = (slot.magazalar | slot.partner_id).filtered(
            'operation_dashboard_enabled'
        )
        if not scoped_restaurants:
            raise AccessError(
                _('Bu vardiya operasyon dashboardu kapsamına dahil değil.')
            )

        form_view = self.env.ref(
            'slot_dashboard.view_operation_shift_line_form'
        )
        return {
            'type': 'ir.actions.act_window',
            'name': _('%s - Kurye Vardiyası') % line.partner_id.name,
            'res_model': 'skurye.profile.lines',
            'res_id': line.id,
            'view_mode': 'form',
            'views': [(form_view.id, 'form')],
            'target': 'current',
            'context': {'create': False},
        }

    @api.model
    def _operation_dashboard_day_bounds(self, selected_date=None):
        if selected_date:
            try:
                target_date = fields.Date.to_date(selected_date)
            except (TypeError, ValueError):
                raise ValidationError(_('Geçerli bir rapor tarihi seçin.'))
        else:
            target_date = fields.Date.context_today(self)
        if not target_date:
            raise ValidationError(_('Geçerli bir rapor tarihi seçin.'))

        timezone = pytz.timezone(self.env.user.tz or 'UTC')
        local_start = timezone.localize(datetime.combine(target_date, time.min))
        local_end = local_start + timedelta(days=1)
        utc_start = local_start.astimezone(pytz.UTC).replace(tzinfo=None)
        utc_end = local_end.astimezone(pytz.UTC).replace(tzinfo=None)
        return target_date, timezone, utc_start, utc_end

    @staticmethod
    def _operation_dashboard_localize(value, timezone):
        if not value:
            return False
        return pytz.UTC.localize(value).astimezone(timezone)

    @api.model
    def action_operation_dashboard_toggle_shift(self, line_id):
        """Stop or resume a started courier shift from the admin dashboard."""
        self._operation_dashboard_check_access()
        try:
            line_id = int(line_id)
        except (TypeError, ValueError):
            raise ValidationError(_('Geçerli bir kurye vardiyası seçin.'))

        self.env.cr.execute(
            'SELECT id FROM skurye_profile_lines WHERE id = %s FOR UPDATE',
            [line_id],
        )
        if not self.env.cr.fetchone():
            raise ValidationError(_('Kurye vardiyası bulunamadı.'))

        line = self.env['skurye.profile.lines'].sudo().browse(line_id)
        line.invalidate_cache()
        slot = self.sudo().browse(line.sequence).exists()
        if not slot or line not in slot.skurye_profile_lines:
            raise ValidationError(_('Kurye vardiyasının bağlı olduğu kayıt bulunamadı.'))

        scoped_restaurants = (slot.magazalar | slot.partner_id).filtered(
            'operation_dashboard_enabled'
        )
        if not scoped_restaurants:
            raise AccessError(
                _('Bu vardiya operasyon dashboardu kapsamına dahil değil.')
            )

        now = fields.Datetime.now()
        _slot, planned_start, planned_end = line._courier_planned_period()
        if not planned_start or not planned_end:
            raise ValidationError(_('Vardiyanın başlangıç ve bitiş saati eksik.'))
        if not line.start_date:
            raise ValidationError(
                _('Henüz başlamamış bir vardiya sonlandırılamaz.')
            )

        if line.operasyon_admin_durdurdu:
            if line.kurye_paket_beyani_yapildi:
                raise ValidationError(
                    _('Paket beyanı verilmiş bir vardiya yeniden başlatılamaz.')
                )
            if now >= planned_end:
                raise ValidationError(
                    _('Planlanan bitiş saati geçen vardiya yeniden başlatılamaz.')
                )
            if not slot.active_status:
                raise ValidationError(_('Kapanmış bir vardiya yeniden başlatılamaz.'))

            paused_at = line.operasyon_duraklatma_zamani or line.end_date
            pause_seconds = 0
            if paused_at and now > paused_at:
                pause_seconds = int((now - paused_at).total_seconds())
            line.write({
                'end_date': False,
                'kurye_active': True,
                'active': True,
                'kurye_calisma_saati': 0.0,
                'sale_price': 0.0,
                'operasyon_admin_durdurdu': False,
                'operasyon_duraklatma_zamani': False,
                'operasyon_toplam_duraklatma_saniyesi': (
                    line.operasyon_toplam_duraklatma_saniyesi
                    + max(pause_seconds, 0)
                ),
            })
            if (
                not line.partner_id.kurye_mola_durumu
                and line.partner_id.kurye_durumu == 'mesgul'
            ):
                line.partner_id.write({'kurye_durumu': 'musait'})
            return {
                'state': 'resumed',
                'message': _('%s vardiyasına devam ediyor.') % line.partner_id.name,
            }

        if line.end_date or not line.kurye_active:
            raise ValidationError(_('Bu vardiya zaten sonlandırılmış.'))
        if now >= planned_end:
            raise ValidationError(
                _('Bu vardiyanın planlanan bitiş saati zaten geçmiş.')
            )

        worked_hours = line.calculate_worked_hours_until(now)
        restaurant = slot.magazalar[:1] or slot.partner_id
        hourly_rate = (
            restaurant.saatlik_ucret
            if slot.slot_tipi == 'sabit' and restaurant
            else slot.saatlik_ucret
        )
        line.write({
            'end_date': now,
            'kurye_active': False,
            'kurye_calisma_saati': worked_hours,
            'sale_price': worked_hours * hourly_rate if hourly_rate > 0 else 0.0,
            'operasyon_admin_durdurdu': True,
            'operasyon_duraklatma_zamani': now,
        })

        other_lines = self.env['skurye.profile.lines'].sudo().search([
            ('id', '!=', line.id),
            ('partner_id', '=', line.partner_id.id),
            ('active', '=', True),
            ('kurye_active', '=', True),
            ('start_date', '!=', False),
            ('end_date', '=', False),
        ])
        has_other_active_shift = any(
            other_start
            and other_end
            and other_start <= now < other_end
            for _other_slot, other_start, other_end in (
                other_line._courier_planned_period()
                for other_line in other_lines
            )
        )
        if not has_other_active_shift:
            line.partner_id.write({
                'kurye_durumu': (
                    'molada' if line.partner_id.kurye_mola_durumu else 'mesgul'
                ),
            })
        return {
            'state': 'stopped',
            'worked_hours': round(worked_hours, 2),
            'message': _(
                '%(courier)s vardiyası sonlandırıldı (%(hours).2f saat).'
            ) % {
                'courier': line.partner_id.name,
                'hours': worked_hours,
            },
        }

    @api.model
    def get_operation_dashboard_data(self, selected_date=None):
        self._operation_dashboard_check_access()
        target_date, timezone, utc_start, utc_end = (
            self._operation_dashboard_day_bounds(selected_date)
        )
        now_utc = fields.Datetime.now()
        today = fields.Date.context_today(self)

        dashboard_restaurants = self.env['res.partner'].sudo().search([
            ('user_role', '=', 'magaza'),
            ('operation_dashboard_enabled', '=', True),
        ])
        dashboard_scope_active = True
        slot_domain = [
            ('start_date', '<', utc_end),
            ('end_date', '>=', utc_start),
            '|',
            ('magazalar', 'in', dashboard_restaurants.ids),
            ('partner_id', 'in', dashboard_restaurants.ids),
        ]
        slots = self.sudo().search(
            slot_domain,
            order='start_date asc, id asc',
        )
        lines = self.env['skurye.profile.lines'].sudo().search([
            ('sequence', 'in', slots.ids),
            ('partner_id', '!=', False),
            ('partner_id.user_role', '=', 'kurye'),
            # The legacy fixed-slot generator inserts this technical placeholder
            # when a restaurant has no courier plan. It is not a real shift.
            ('partner_id.name', '!=', 'Boş'),
        ], order='sequence asc, kurye_start_date asc, id asc')
        slot_by_id = {slot.id: slot for slot in slots}

        metrics = {
            'planned_slots': len(slots),
            'unassigned_slots': 0,
            'planned_shifts': 0,
            'planned_couriers': 0,
            'due_shifts': 0,
            'arrived': 0,
            'arrived_couriers': 0,
            'on_time': 0,
            'late': 0,
            'missing': 0,
            'upcoming': 0,
            'working_now': 0,
            'completed': 0,
            'fixed_slots': len(slots.filtered(lambda slot: slot.slot_tipi == 'sabit')),
            'region_slots': len(slots.filtered(lambda slot: slot.slot_tipi == 'bolge')),
            'restaurants': len(slots.mapped('magazalar')),
        }
        rows = []
        planned_courier_ids = set()
        arrived_courier_ids = set()
        staffed_slot_ids = set()

        for line in lines:
            slot = slot_by_id.get(line.sequence)
            if not slot:
                continue
            use_courier_times = bool(
                line.kurye_start_date and line.kurye_end_date
            )
            planned_start = (
                line.kurye_start_date if use_courier_times else slot.start_date
            )
            planned_end = (
                line.kurye_end_date if use_courier_times else slot.end_date
            )
            if (
                not planned_start
                or not planned_end
                or planned_start >= utc_end
                or planned_end < utc_start
            ):
                continue

            metrics['planned_shifts'] += 1
            planned_courier_ids.add(line.partner_id.id)
            staffed_slot_ids.add(slot.id)
            is_due = (
                target_date < today
                or (target_date == today and planned_start <= now_utc)
            )
            arrived = bool(line.start_date)
            if is_due:
                metrics['due_shifts'] += 1
            if arrived:
                metrics['arrived'] += 1
                arrived_courier_ids.add(line.partner_id.id)

            calculated_late_minutes = 0
            if arrived and line.start_date > planned_start:
                calculated_late_minutes = max(
                    int((line.start_date - planned_start).total_seconds() // 60),
                    0,
                )
            late_minutes = max(
                line.gecikme_dakikasi or 0,
                calculated_late_minutes,
            )
            is_late = bool(
                arrived
                and (line.gecikme_durumu or late_minutes > 10)
            )
            is_working = bool(
                arrived
                and not line.end_date
                and line.kurye_active
                and target_date == today
                and planned_end > now_utc
            )
            is_completed = bool(
                arrived
                and (
                    line.end_date
                    or target_date < today
                    or planned_end <= now_utc
                )
            )

            if arrived and is_late:
                metrics['late'] += 1
                status = 'late'
                status_label = _('Geç Giriş')
            elif arrived:
                metrics['on_time'] += 1
                if is_working:
                    status = 'working'
                    status_label = _('Çalışıyor')
                elif is_completed:
                    status = 'completed'
                    status_label = _('Tamamlandı')
                else:
                    status = 'on_time'
                    status_label = _('Zamanında')
            elif is_due:
                metrics['missing'] += 1
                status = 'missing'
                status_label = _('Giriş Yapmadı')
            else:
                metrics['upcoming'] += 1
                status = 'upcoming'
                status_label = _('Yaklaşan')

            if is_working:
                metrics['working_now'] += 1
            if is_completed:
                metrics['completed'] += 1

            slot_restaurants = slot.magazalar.filtered(
                'operation_dashboard_enabled'
            )
            restaurant_names = slot_restaurants.mapped('name')
            if (
                not restaurant_names
                and slot.partner_id
                and (
                    slot.partner_id.operation_dashboard_enabled
                )
            ):
                restaurant_names = [slot.partner_id.name]
            restaurant_name = ', '.join(restaurant_names) or _('Bölge Operasyonu')

            local_planned_start = self._operation_dashboard_localize(
                planned_start,
                timezone,
            )
            local_planned_end = self._operation_dashboard_localize(
                planned_end,
                timezone,
            )
            local_actual_start = self._operation_dashboard_localize(
                line.start_date,
                timezone,
            )

            rows.append({
                'line_id': line.id,
                'slot_id': slot.id,
                'courier_id': line.partner_id.id,
                'courier_name': line.partner_id.name or '-',
                'slot_name': slot.name or '-',
                'slot_type': slot.slot_tipi,
                'slot_type_label': (
                    _('Sabit') if slot.slot_tipi == 'sabit' else _('Bölge')
                ),
                'restaurant_name': restaurant_name,
                'planned_start': local_planned_start.strftime('%H:%M'),
                'planned_end': local_planned_end.strftime('%H:%M'),
                'actual_start': (
                    local_actual_start.strftime('%H:%M')
                    if local_actual_start
                    else '-'
                ),
                'late_minutes': late_minutes if is_late else 0,
                'late_duration_label': (
                    '%02d:%02d saat' % divmod(late_minutes, 60)
                    if is_late
                    else False
                ),
                'status': status,
                'status_label': status_label,
                'can_stop_shift': bool(is_working),
                'can_resume_shift': bool(
                    target_date == today
                    and line.operasyon_admin_durdurdu
                    and not line.kurye_paket_beyani_yapildi
                    and planned_end > now_utc
                    and slot.active_status
                ),
            })

        metrics['planned_couriers'] = len(planned_courier_ids)
        metrics['arrived_couriers'] = len(arrived_courier_ids)
        metrics['unassigned_slots'] = len(slots) - len(staffed_slot_ids)
        due_count = metrics['due_shifts']
        if not due_count and not metrics['unassigned_slots']:
            health = 'neutral'
            health_title = _('Plan hazır, vardiya saatleri bekleniyor')
            health_message = _(
                'Henüz giriş zamanı gelen kurye yok. Yaklaşan vardiyaları takip edin.'
            )
        elif metrics['missing'] or metrics['unassigned_slots']:
            health = 'danger'
            intervention_count = (
                metrics['missing'] + metrics['unassigned_slots']
            )
            health_title = _('%s plan için müdahale gerekiyor') % intervention_count
            health_message = _(
                'Giriş yapmayan kuryeler veya henüz kurye atanmamış vardiyalar var.'
            )
        elif metrics['late']:
            health = 'warning'
            health_title = _('Operasyon çalışıyor, gecikmeler takip edilmeli')
            health_message = _(
                'Tüm kuryeler giriş yaptı ancak geciken vardiyalar bulunuyor.'
            )
        else:
            health = 'success'
            health_title = _('Operasyon planlandığı gibi ilerliyor')
            health_message = _(
                'Zamanı gelen tüm kuryeler vardiyalarına giriş yaptı.'
            )

        status_priority = {
            'missing': 0,
            'late': 1,
            'working': 2,
            'upcoming': 3,
            'on_time': 4,
            'completed': 5,
        }
        rows.sort(key=lambda row: (
            status_priority.get(row['status'], 9),
            row['planned_start'],
            row['courier_name'],
        ))
        courier_statuses = {}
        for row in rows:
            courier_statuses.setdefault(row['courier_id'], set()).add(
                row['status']
            )
        courier_status_by_id = {
            courier_id: self._operation_dashboard_courier_status(statuses)
            for courier_id, statuses in courier_statuses.items()
        }
        for row in rows:
            row['courier_status'] = courier_status_by_id[row['courier_id']]

        courier_summary = self._operation_dashboard_group_rows(rows)
        courier_summary = courier_summary[0] if courier_summary else {
            'planned': 0,
            'due': 0,
            'arrived': 0,
            'on_time': 0,
            'late': 0,
            'missing': 0,
            'upcoming': 0,
            'entry_rate': 0,
        }
        metrics.update({
            'courier_planned': courier_summary['planned'],
            'courier_due': courier_summary['due'],
            'courier_arrived': courier_summary['arrived'],
            'courier_on_time': courier_summary['on_time'],
            'courier_late': courier_summary['late'],
            'courier_missing': courier_summary['missing'],
            'courier_upcoming': courier_summary['upcoming'],
            'courier_compliance_rate': courier_summary['entry_rate'],
        })
        restaurant_summaries = self._operation_dashboard_group_rows(
            rows,
            group_key='restaurant_name',
        )
        local_now = self._operation_dashboard_localize(now_utc, timezone)
        return {
            'selected_date': fields.Date.to_string(target_date),
            'selected_date_label': target_date.strftime('%d.%m.%Y'),
            'is_today': target_date == today,
            'last_updated': local_now.strftime('%H:%M:%S'),
            'metrics': metrics,
            'dashboard_scope_active': dashboard_scope_active,
            'dashboard_restaurant_count': len(dashboard_restaurants),
            'health': {
                'status': health,
                'title': health_title,
                'message': health_message,
            },
            'rows': rows,
            'attention_rows': [
                row for row in rows if row['status'] in ('missing', 'late')
            ][:8],
            'restaurants': restaurant_summaries,
        }

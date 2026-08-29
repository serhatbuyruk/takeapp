import base64
import re
import unicodedata
import xml.etree.ElementTree as ElementTree
from collections import defaultdict
from datetime import datetime, timedelta

import pytz
import xlrd

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


REQUIRED_HEADERS = (
    'TARİH',
    'BÖLGE',
    'PROJE',
    'ŞUBE',
    'KURYE',
    'VARDİYA GİRİŞ',
    'VARDİYA ÇIKIŞ',
)
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_SHIFT_ROWS = 5000


def _normalized_text(value):
    value = unicodedata.normalize('NFKD', str(value or '').strip().casefold())
    value = value.replace('ı', 'i')
    value = ''.join(char for char in value if not unicodedata.combining(char))
    return ' '.join(re.findall(r'[a-z0-9]+', value))


class SlotDashboardShiftImportBatch(models.Model):
    _name = 'slot.dashboard.shift.import.batch'
    _description = 'Vardiya Planı İçe Aktarım Kaydı'
    _order = 'create_date desc, id desc'

    name = fields.Char(required=True, readonly=True)
    filename = fields.Char(readonly=True)
    slot_count = fields.Integer(string='Açılan Vardiya', readonly=True)
    updated_slot_count = fields.Integer(
        string='Güncellenen Vardiya',
        readonly=True,
    )
    shift_count = fields.Integer(string='Açılan Vardiya', readonly=True)
    skipped_count = fields.Integer(string='Atlanan Mevcut Vardiya', readonly=True)
    slot_ids = fields.One2many(
        'slots.profile',
        'shift_import_batch_id',
        string='Oluşturulan Vardiyalar',
        readonly=True,
    )
    line_ids = fields.One2many(
        'skurye.profile.lines',
        'shift_import_batch_id',
        string='Oluşturulan Vardiyalar',
        readonly=True,
    )


class SlotsProfile(models.Model):
    _inherit = 'slots.profile'

    shift_import_batch_id = fields.Many2one(
        'slot.dashboard.shift.import.batch',
        string='Vardiya İçe Aktarımı',
        copy=False,
        index=True,
        ondelete='set null',
    )

    @api.model
    def get_shift_management_action(self, selected_date=None, mode='shifts'):
        self._operation_dashboard_check_access()
        if mode not in ('shifts', 'packages'):
            raise ValidationError(_('Geçersiz vardiya görünümü.'))

        target_date, _timezone, utc_start, utc_end = (
            self._operation_dashboard_day_bounds(selected_date)
        )
        dashboard_restaurants = self.env['res.partner'].sudo().search([
            ('user_role', '=', 'magaza'),
            ('operation_dashboard_enabled', '=', True),
        ])
        slots = self.sudo().search([
            ('start_date', '<', utc_end),
            ('end_date', '>', utc_start),
            ('slot_tipi', '=', 'sabit'),
            '|',
            ('magazalar', 'in', dashboard_restaurants.ids),
            ('partner_id', 'in', dashboard_restaurants.ids),
        ])
        if mode == 'shifts':
            domain = [
                ('sequence', 'in', slots.ids),
                ('partner_id', '!=', False),
                ('partner_id.name', '!=', 'Boş'),
                ('shift_import_batch_id', '!=', False),
                ('shift_plan_date', '=', target_date),
            ]
            view = self.env.ref(
                'slot_dashboard.view_imported_shift_line_tree'
            )
            return {
                'type': 'ir.actions.act_window',
                'name': _('Yüklenen Vardiya Planı - %s') % (
                    target_date.strftime('%d.%m.%Y')
                ),
                'res_model': 'skurye.profile.lines',
                'view_mode': 'tree,form',
                'views': [(view.id, 'tree'), (False, 'form')],
                'domain': domain,
                'context': {
                    'create': False,
                    'delete': False,
                },
                'target': 'current',
            }
        else:
            view = self.env.ref(
                'slot_dashboard.view_shift_package_status_tree'
            )
            domain = [
                ('sequence', 'in', slots.ids),
                ('partner_id', '!=', False),
                ('partner_id.name', '!=', 'Boş'),
                ('shift_import_batch_id', '!=', False),
                ('shift_plan_date', '=', target_date),
            ]
            return {
                'type': 'ir.actions.act_window',
                'name': _('Personel Paket Beyanları - %s') % (
                    target_date.strftime('%d.%m.%Y')
                ),
                'res_model': 'skurye.profile.lines',
                'view_mode': 'tree,form',
                'views': [(view.id, 'tree'), (False, 'form')],
                'domain': domain,
                'context': {
                    'create': False,
                    'delete': False,
                },
                'target': 'current',
            }


class SkuryeProfileLines(models.Model):
    _inherit = 'skurye.profile.lines'

    shift_import_batch_id = fields.Many2one(
        'slot.dashboard.shift.import.batch',
        string='Vardiya İçe Aktarımı',
        copy=False,
        index=True,
        ondelete='set null',
    )
    shift_plan_date = fields.Date(
        string='Tarih',
        copy=False,
        index=True,
    )
    shift_plan_region = fields.Char(string='Bölge', copy=False)
    shift_plan_project = fields.Char(string='Proje', copy=False)
    shift_plan_branch = fields.Char(string='Şube', copy=False)
    dashboard_planned_start = fields.Datetime(
        string='Vardiya Giriş',
        compute='_compute_dashboard_shift_status',
    )
    dashboard_planned_end = fields.Datetime(
        string='Vardiya Çıkış',
        compute='_compute_dashboard_shift_status',
    )
    dashboard_package_state = fields.Selection(
        [
            ('upcoming', 'Zamanı Gelmedi'),
            ('missing', 'Paket Beyanı Eksik'),
            ('submitted', 'Paket Beyanı Girildi'),
        ],
        string='Paket Beyan Durumu',
        compute='_compute_dashboard_shift_status',
    )

    @api.depends(
        'sequence',
        'kurye_start_date',
        'kurye_end_date',
        'kurye_paket_beyani_yapildi',
        'paket_mutabakat_slot_id',
        'paket_mutabakat_slot_id.start_date',
        'paket_mutabakat_slot_id.end_date',
    )
    def _compute_dashboard_shift_status(self):
        now = fields.Datetime.now()
        for line in self:
            slot = (
                line.paket_mutabakat_slot_id
                or self.env['slots.profile'].browse(line.sequence).exists()
            )
            use_line_times = bool(
                line.kurye_start_date and line.kurye_end_date
            )
            planned_start = (
                line.kurye_start_date
                if use_line_times
                else slot.start_date
            )
            planned_end = (
                line.kurye_end_date
                if use_line_times
                else slot.end_date
            )
            line.dashboard_planned_start = planned_start
            line.dashboard_planned_end = planned_end
            if line.kurye_paket_beyani_yapildi:
                line.dashboard_package_state = 'submitted'
            elif planned_end and planned_end <= now:
                line.dashboard_package_state = 'missing'
            else:
                line.dashboard_package_state = 'upcoming'


class SlotDashboardShiftImportWizard(models.TransientModel):
    _name = 'slot.dashboard.shift.import.wizard'
    _description = 'Excel Vardiya Planı Yükleme'

    upload_file = fields.Binary(
        string='Excel Dosyası',
        required=True,
        attachment=False,
    )
    filename = fields.Char(string='Dosya Adı')
    state = fields.Selection(
        [
            ('upload', 'Dosya Yükleme'),
            ('review', 'Kontrol Sonucu'),
            ('done', 'Tamamlandı'),
        ],
        default='upload',
        required=True,
    )
    preview_message = fields.Text(string='Kontrol Raporu', readonly=True)
    valid_row_count = fields.Integer(string='Aktarılabilir Satır', readonly=True)
    error_count = fields.Integer(string='Atlanacak Satır/Hata', readonly=True)
    result_message = fields.Text(string='İçe Aktarma Sonucu', readonly=True)

    def _check_access(self):
        self.env['slots.profile']._operation_dashboard_check_access()

    @staticmethod
    def _cell_text(sheet, row_index, column_index):
        return str(sheet.cell_value(row_index, column_index) or '').strip()

    @staticmethod
    def _is_blank_cell_value(value):
        return value is None or (
            isinstance(value, str) and not value.strip()
        )

    @staticmethod
    def _parse_excel_date(cell, datemode):
        if cell.ctype == xlrd.XL_CELL_DATE:
            return xlrd.xldate_as_datetime(cell.value, datemode).date()
        if cell.ctype == xlrd.XL_CELL_NUMBER:
            return xlrd.xldate_as_datetime(cell.value, datemode).date()
        value = str(cell.value or '').strip()
        for date_format in ('%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(value, date_format).date()
            except ValueError:
                continue
        raise ValidationError(_('geçerli bir tarih değil'))

    @staticmethod
    def _parse_excel_time(cell, datemode):
        if cell.ctype in (xlrd.XL_CELL_DATE, xlrd.XL_CELL_NUMBER):
            return xlrd.xldate_as_datetime(cell.value, datemode).time().replace(
                microsecond=0
            )
        value = str(cell.value or '').strip()
        for time_format in ('%H:%M', '%H:%M:%S'):
            try:
                return datetime.strptime(value, time_format).time()
            except ValueError:
                continue
        raise ValidationError(_('geçerli bir saat değil'))

    def _read_rows(self):
        self.ensure_one()
        if not self.upload_file:
            raise ValidationError(_('Lütfen bir Excel dosyası seçin.'))
        if self.filename and not self.filename.lower().endswith('.xlsx'):
            raise ValidationError(_('Yalnızca .xlsx vardiya dosyası yükleyebilirsiniz.'))
        try:
            content = base64.b64decode(self.upload_file, validate=True)
        except (ValueError, TypeError):
            raise ValidationError(_('Yüklenen dosya okunamadı.'))
        if len(content) > MAX_FILE_SIZE:
            raise ValidationError(_('Excel dosyası 5 MB sınırını aşamaz.'))

        # xlrd 1.2 uses the removed getiterator alias on modern Python.
        if not hasattr(ElementTree.ElementTree, 'getiterator'):
            ElementTree.ElementTree.getiterator = ElementTree.ElementTree.iter
        try:
            workbook = xlrd.open_workbook(file_contents=content)
        except (xlrd.XLRDError, OSError, ValueError) as error:
            raise ValidationError(
                _('Excel dosyası açılamadı: %s') % str(error)
            )
        if not workbook.nsheets:
            raise ValidationError(_('Excel dosyasında çalışma sayfası yok.'))
        sheet = workbook.sheet_by_index(0)
        if sheet.nrows < 2:
            raise ValidationError(_('Excel dosyasında vardiya satırı bulunamadı.'))
        if sheet.nrows - 1 > MAX_SHIFT_ROWS:
            raise ValidationError(
                _('Tek dosyada en fazla %s vardiya yüklenebilir.') % MAX_SHIFT_ROWS
            )

        actual_headers = [
            _normalized_text(sheet.cell_value(0, column))
            for column in range(min(sheet.ncols, len(REQUIRED_HEADERS)))
        ]
        expected_headers = [_normalized_text(header) for header in REQUIRED_HEADERS]
        if actual_headers != expected_headers:
            raise ValidationError(
                _(
                    'Excel başlıkları değiştirilmemelidir. Beklenen sıra:\n%s'
                ) % ' | '.join(REQUIRED_HEADERS)
            )

        timezone = pytz.timezone(self.env.user.tz or 'Europe/Istanbul')
        rows = []
        errors = []
        for row_index in range(1, sheet.nrows):
            values = [
                sheet.cell_value(row_index, column)
                for column in range(len(REQUIRED_HEADERS))
            ]
            if all(self._is_blank_cell_value(value) for value in values):
                continue
            excel_row = row_index + 1
            if any(self._is_blank_cell_value(value) for value in values):
                errors.append(
                    _('Satır %(row)s: zorunlu hücrelerden biri boş.') % {
                        'row': excel_row,
                    }
                )
                continue
            try:
                plan_date = self._parse_excel_date(
                    sheet.cell(row_index, 0),
                    workbook.datemode,
                )
                start_time = self._parse_excel_time(
                    sheet.cell(row_index, 5),
                    workbook.datemode,
                )
                end_time = self._parse_excel_time(
                    sheet.cell(row_index, 6),
                    workbook.datemode,
                )
            except ValidationError as error:
                errors.append(
                    _('Satır %(row)s: %(error)s.') % {
                        'row': excel_row,
                        'error': error.args[0],
                    }
                )
                continue
            local_start_value = datetime.combine(plan_date, start_time)
            if start_time == datetime.min.time():
                local_start_value += timedelta(seconds=1)
            local_start = timezone.localize(local_start_value)
            if end_time == datetime.min.time():
                local_end = timezone.localize(datetime.combine(
                    plan_date,
                    datetime.max.time().replace(microsecond=0),
                ))
            else:
                local_end = timezone.localize(
                    datetime.combine(plan_date, end_time)
                )
            if local_end <= local_start:
                local_end += timedelta(days=1)
            start = local_start.astimezone(pytz.UTC).replace(tzinfo=None)
            end = local_end.astimezone(pytz.UTC).replace(tzinfo=None)
            rows.append({
                'excel_row': excel_row,
                'plan_date': plan_date,
                'region': self._cell_text(sheet, row_index, 1),
                'project': self._cell_text(sheet, row_index, 2),
                'branch': self._cell_text(sheet, row_index, 3),
                'courier_name': self._cell_text(sheet, row_index, 4),
                'start': start,
                'end': end,
            })
        if not rows and not errors:
            raise ValidationError(_('Excel dosyasında geçerli vardiya satırı yok.'))
        return rows, errors

    @staticmethod
    def _partner_name_map(partners):
        result = defaultdict(list)
        for partner in partners:
            result[_normalized_text(partner.name)].append(partner)
        return result

    def _match_restaurant(self, row, restaurants, exact_name_map):
        project = _normalized_text(row['project'])
        branch = _normalized_text(row['branch'])
        combined = _normalized_text('%s %s' % (row['project'], row['branch']))

        candidates = exact_name_map.get(combined, [])
        if not candidates:
            candidates = exact_name_map.get(project, [])
        if not candidates:
            project_tokens = set(project.split())
            branch_tokens = set(branch.split())
            candidates = [
                restaurant
                for restaurant in restaurants
                if project_tokens.issubset(
                    set(_normalized_text(restaurant.name).split())
                )
                and branch_tokens.issubset(
                    set(_normalized_text(restaurant.name).split())
                )
            ]
        return candidates

    def _match_partners(self, rows):
        partners = self.env['res.partner'].sudo()
        couriers = partners.search([
            ('user_role', '=', 'kurye'),
            ('active', '=', True),
        ])
        restaurants = partners.search([
            ('user_role', '=', 'magaza'),
            ('active', '=', True),
        ])
        courier_map = self._partner_name_map(couriers)
        restaurant_map = self._partner_name_map(restaurants)
        errors = []
        matched_rows = []
        for row in rows:
            row_errors = []
            courier_matches = courier_map.get(
                _normalized_text(row['courier_name']),
                [],
            )
            if len(courier_matches) != 1:
                detail = (
                    _('bulunamadı')
                    if not courier_matches
                    else _('birden fazla kayıtla eşleşti: %s') % ', '.join(
                        '%s (#%s)' % (item.name, item.id)
                        for item in courier_matches
                    )
                )
                row_errors.append(
                    _('Satır %(row)s: kurye "%(name)s" %(detail)s.') % {
                        'row': row['excel_row'],
                        'name': row['courier_name'],
                        'detail': detail,
                    }
                )
            else:
                row['courier'] = courier_matches[0]

            restaurant_matches = self._match_restaurant(
                row,
                restaurants,
                restaurant_map,
            )
            if len(restaurant_matches) != 1:
                detail = (
                    _('bulunamadı')
                    if not restaurant_matches
                    else _('birden fazla kayıtla eşleşti: %s') % ', '.join(
                        '%s (#%s)' % (item.name, item.id)
                        for item in restaurant_matches
                    )
                )
                row_errors.append(
                    _(
                        'Satır %(row)s: restoran "%(project)s / %(branch)s" '
                        '%(detail)s.'
                    ) % {
                        'row': row['excel_row'],
                        'project': row['project'],
                        'branch': row['branch'],
                        'detail': detail,
                    }
                )
            else:
                row['restaurant'] = restaurant_matches[0]
            if row_errors:
                errors.extend(row_errors)
            else:
                matched_rows.append(row)
        return matched_rows, errors

    @staticmethod
    def _overlaps(start_a, end_a, start_b, end_b):
        return start_a < end_b and end_a > start_b

    def _deduplicate_and_validate_input(self, rows):
        latest_rows = {}
        duplicate_count = 0
        warnings = []
        for row in rows:
            signature = (
                row['restaurant'].id,
                row['plan_date'],
                row['courier'].id,
            )
            previous = latest_rows.get(signature)
            if previous:
                duplicate_count += 1
                warnings.append(
                    _(
                        'Satır %(old)s: %(courier)s aynı restoran ve gün için '
                        'tekrarlandı; son satır %(new)s esas alınacak.'
                    ) % {
                        'old': previous['excel_row'],
                        'new': row['excel_row'],
                        'courier': row['courier'].name,
                    }
                )
            latest_rows[signature] = row

        unique_rows = []
        by_courier = defaultdict(list)
        errors = []
        for row in sorted(
            latest_rows.values(), key=lambda item: item['excel_row']
        ):
            conflict = False
            for other in by_courier[row['courier'].id]:
                if self._overlaps(
                    row['start'],
                    row['end'],
                    other['start'],
                    other['end'],
                ):
                    errors.append(
                        _(
                            'Satır %(row)s ile %(other)s: %(courier)s için '
                            'dosya içinde çakışan vardiya.'
                        ) % {
                            'row': row['excel_row'],
                            'other': other['excel_row'],
                            'courier': row['courier'].name,
                        }
                    )
                    conflict = True
                    break
            if conflict:
                continue
            by_courier[row['courier'].id].append(row)
            unique_rows.append(row)
        return unique_rows, duplicate_count, warnings + errors

    @staticmethod
    def _line_times(line, slot):
        if line.kurye_start_date and line.kurye_end_date:
            return line.kurye_start_date, line.kurye_end_date
        return slot.start_date, slot.end_date

    def _plan_day_bounds(self, plan_date):
        """Return the selected local calendar day without crossing midnight."""
        timezone = pytz.timezone(self.env.user.tz or 'Europe/Istanbul')
        local_start = timezone.localize(datetime.combine(
            plan_date,
            datetime.min.time(),
        ))
        local_end = timezone.localize(datetime.combine(
            plan_date,
            datetime.max.time().replace(microsecond=0),
        ))
        return (
            local_start.astimezone(pytz.UTC).replace(tzinfo=None),
            local_end.astimezone(pytz.UTC).replace(tzinfo=None),
        )

    def _prepare_groups(self, rows):
        groups = defaultdict(list)
        for row in rows:
            groups[(row['restaurant'].id, row['plan_date'])].append(row)
        groups_by_restaurant = defaultdict(list)
        for key, group_rows in groups.items():
            groups_by_restaurant[key[0]].append({
                'key': key,
                'rows': group_rows,
                'start': min(row['start'] for row in group_rows),
                'end': max(row['end'] for row in group_rows),
            })
        errors = []
        rejected_keys = set()
        for restaurant_groups in groups_by_restaurant.values():
            restaurant_groups.sort(key=lambda item: item['start'])
            for previous, current in zip(
                restaurant_groups,
                restaurant_groups[1:],
            ):
                if self._overlaps(
                    previous['start'],
                    previous['end'],
                    current['start'],
                    current['end'],
                ):
                    errors.append(
                        _(
                            '%(restaurant)s: %(first)s ve %(second)s tarihli '
                            'restoran vardiyaları dosya içinde çakışıyor.'
                        ) % {
                            'restaurant': current['rows'][0]['restaurant'].name,
                            'first': fields.Date.to_string(previous['key'][1]),
                            'second': fields.Date.to_string(current['key'][1]),
                        }
                    )
                    rejected_keys.add(current['key'])
        return {
            key: group_rows
            for key, group_rows in groups.items()
            if key not in rejected_keys
        }, errors

    def _slot_package_couriers(self, slot):
        lines = slot.skurye_profile_lines.filtered(
            lambda line: (
                line.partner_id
                and line.partner_id.name != 'Boş'
                and (
                    line.slot_paket_sayisi > 0
                    or line.kurye_paket_beyani_yapildi
                    or line.paket_mutabakat_durumu
                    not in (False, 'not_submitted')
                )
            )
        )
        courier_ids = set(lines.partner_id.ids)
        slot_couriers = slot.skurye_profile_lines.partner_id.filtered(
            lambda courier: courier and courier.name != 'Boş'
        )
        if slot_couriers and slot.magazalar:
            orders = self.env['corders.profile'].sudo().search([
                ('kurye', 'in', slot_couriers.ids),
                ('magaza', 'in', slot.magazalar.ids),
                ('siparis_tarihi', '>=', slot.start_date),
                ('siparis_tarihi', '<=', slot.end_date),
                ('siparis_durumu', '!=', 'iptal_edildi'),
            ])
            courier_ids.update(orders.kurye.ids)
        return self.env['res.partner'].sudo().browse(list(courier_ids))

    def _validate_existing_plan(self, groups):
        errors = []
        valid_groups = {}
        update_slots = {}
        slot_model = self.env['slots.profile'].sudo()

        for key, group_rows in groups.items():
            restaurant = group_rows[0]['restaurant']
            group_start, group_end = self._plan_day_bounds(key[1])
            existing_slots = slot_model.search([
                ('slot_tipi', '=', 'sabit'),
                ('magazalar', 'in', restaurant.id),
                ('start_date', '<', group_end),
                ('end_date', '>', group_start),
            ])
            imported_slots = existing_slots.filtered(
                lambda slot: bool(slot.shift_import_batch_id)
            )
            target_slot = False
            if len(existing_slots) == 1 and imported_slots == existing_slots:
                target_slot = imported_slots
                update_slots[key] = target_slot
            elif existing_slots:
                for row in group_rows:
                    errors.append(
                        _(
                            'Satır %(row)s: %(restaurant)s / %(date)s için '
                            'mevcut %(slots)s numaralı elle açılmış veya çoklu '
                            'vardiyayla çakışıyor; satır aktarılmayacak.'
                        ) % {
                            'row': row['excel_row'],
                            'restaurant': restaurant.name,
                            'date': fields.Date.to_string(key[1]),
                            'slots': ', '.join(
                                str(slot.id) for slot in existing_slots
                            ),
                        }
                    )
                continue

            package_courier_ids = set(
                self._slot_package_couriers(target_slot).ids
            ) if target_slot else set()
            valid_rows = []
            for row in group_rows:
                existing_line = (
                    target_slot.skurye_profile_lines.filtered(
                        lambda line: line.partner_id == row['courier']
                    )[:1]
                    if target_slot else self.env['skurye.profile.lines']
                )
                if existing_line and row['courier'].id in package_courier_ids:
                    current_start, current_end = self._line_times(
                        existing_line, target_slot
                    )
                    if (
                        current_start != row['start']
                        or current_end != row['end']
                    ):
                        errors.append(
                            _(
                                'Satır %(row)s: %(courier)s paket taşımaya '
                                'başladığı için mevcut saatleri değiştirilemez; '
                                'satır aktarılmayacak.'
                            ) % {
                                'row': row['excel_row'],
                                'courier': row['courier'].name,
                            }
                        )
                        continue
                valid_rows.append(row)
            if valid_rows:
                valid_groups[key] = valid_rows

        active_rows = [row for rows in valid_groups.values() for row in rows]
        if active_rows:
            min_start = min(row['start'] for row in active_rows)
            max_end = max(row['end'] for row in active_rows)
            courier_ids = {row['courier'].id for row in active_rows}
            candidate_slots = slot_model.search([
                ('start_date', '<', max_end),
                ('end_date', '>', min_start),
            ])
            existing_lines = self.env['skurye.profile.lines'].sudo().search([
                ('sequence', 'in', candidate_slots.ids),
                ('partner_id', 'in', list(courier_ids)),
            ])
            slots_by_id = {slot.id: slot for slot in candidate_slots}
            for row in active_rows:
                for line in existing_lines.filtered(
                    lambda item: item.partner_id == row['courier']
                ):
                    target_slot = update_slots.get(
                        (row['restaurant'].id, row['plan_date'])
                    )
                    if target_slot and line.sequence == target_slot.id:
                        continue
                    slot = slots_by_id.get(line.sequence)
                    if not slot:
                        continue
                    line_start, line_end = self._line_times(line, slot)
                    if self._overlaps(
                        row['start'],
                        row['end'],
                        line_start,
                        line_end,
                    ):
                        errors.append(
                            _(
                                'Satır %(row)s: %(courier)s, mevcut "%(slot)s" '
                                '(#%(id)s) vardiyasıyla çakışıyor; satır '
                                'aktarılmayacak.'
                            ) % {
                                'row': row['excel_row'],
                                'courier': row['courier'].name,
                                'slot': slot.name,
                                'id': slot.id,
                            }
                        )
                        group_key = (
                            row['restaurant'].id,
                            row['plan_date'],
                        )
                        if row in valid_groups.get(group_key, []):
                            valid_groups[group_key].remove(row)
                        break
        valid_groups = {
            key: rows for key, rows in valid_groups.items() if rows
        }
        update_slots = {
            key: slot
            for key, slot in update_slots.items()
            if key in valid_groups
        }
        return valid_groups, update_slots, errors

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

    @staticmethod
    def _line_values(row, batch, slot=None):
        values = {
            'partner_id': row['courier'].id,
            'kurye_start_date': row['start'],
            'kurye_end_date': row['end'],
            'shift_import_batch_id': batch.id,
            'shift_plan_date': row['plan_date'],
            'shift_plan_region': row['region'],
            'shift_plan_project': row['project'],
            'shift_plan_branch': row['branch'],
        }
        if slot:
            values['sequence'] = slot.id
        return values

    def _merge_imported_shift_lines(self, slot, group_rows, batch):
        """Add new couriers and update repeated ones without deleting others."""
        line_model = self.env['skurye.profile.lines'].sudo()
        for row in sorted(group_rows, key=lambda item: item['excel_row']):
            existing_line = slot.skurye_profile_lines.filtered(
                lambda line: line.partner_id == row['courier']
            ).sorted('id')[:1]
            values = self._line_values(row, batch, slot=slot)
            if existing_line:
                values.pop('sequence', None)
                existing_line.write(values)
            else:
                line_model.create(values)

    def _create_plan(
        self,
        groups,
        update_slots,
        skipped_count,
    ):
        filename = self.filename or _('Vardiya Planı.xlsx')
        batch = self.env['slot.dashboard.shift.import.batch'].create({
            'name': _('%(date)s - %(filename)s') % {
                'date': fields.Datetime.now(),
                'filename': filename,
            },
            'filename': filename,
        })
        created_slots = self.env['slots.profile']
        updated_slot_count = 0
        created_shift_count = 0

        for key, group_rows in groups.items():
            restaurant = group_rows[0]['restaurant']
            if restaurant.slot_tipi != 'sabit':
                restaurant.write({'slot_tipi': 'sabit'})
            group_start, group_end = self._plan_day_bounds(key[1])
            line_commands = [
                (0, 0, self._line_values(row, batch))
                for row in sorted(
                    group_rows,
                    key=lambda item: (item['start'], item['courier'].name),
                )
            ]
            slot_values = {
                'name': _('%s Vardiyası') % restaurant.name,
                'slot_tipi': 'sabit',
                'magazalar': [(6, 0, restaurant.ids)],
                'start_date': group_start,
                'end_date': group_end,
                'lat': restaurant.lat,
                'lng': restaurant.lng,
                'slot_acik_adresi': self._restaurant_address(restaurant),
                'calisma_gunu': self._weekday_key(
                    group_rows[0]['plan_date']
                ),
                'shift_import_batch_id': batch.id,
            }
            if key in update_slots:
                slot = update_slots[key]
                slot.write(slot_values)
                self._merge_imported_shift_lines(
                    slot,
                    group_rows,
                    batch,
                )
                updated_slot_count += 1
                created_shift_count += len(group_rows)
                continue

            slot_values['skurye_profile_lines'] = line_commands
            slot = self.env['slots.profile'].create({
                **slot_values,
            })
            created_slots |= slot
            created_shift_count += len(group_rows)

        batch.write({
            'slot_count': len(created_slots),
            'updated_slot_count': updated_slot_count,
            'shift_count': created_shift_count,
            'skipped_count': skipped_count,
        })
        return batch

    def _prepare_import(self):
        rows, errors = self._read_rows()
        rows, match_errors = self._match_partners(rows)
        errors.extend(match_errors)
        rows, duplicate_count, row_errors = (
            self._deduplicate_and_validate_input(rows)
        )
        errors.extend(row_errors)
        groups, group_errors = self._prepare_groups(rows)
        errors.extend(group_errors)
        groups, update_slots, existing_errors = (
            self._validate_existing_plan(groups)
        )
        errors.extend(existing_errors)
        valid_count = sum(len(group_rows) for group_rows in groups.values())
        return groups, update_slots, duplicate_count, errors, valid_count

    @staticmethod
    def _format_issue_report(errors):
        if not errors:
            return _('Hata veya çakışma bulunamadı.')
        visible_errors = errors[:200]
        report = '\n'.join('• %s' % error for error in visible_errors)
        if len(errors) > len(visible_errors):
            report += _('\n• ... ve %s ek hata') % (
                len(errors) - len(visible_errors)
            )
        return report

    def _reopen_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vardiya Planı Yükle'),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'views': [
                (
                    self.env.ref(
                        'slot_dashboard.view_shift_import_wizard_form'
                    ).id,
                    'form',
                ),
            ],
            'target': 'new',
        }

    def action_preview(self):
        self.ensure_one()
        self._check_access()
        _groups, _update_slots, _duplicate_count, errors, valid_count = (
            self._prepare_import()
        )
        self.write({
            'state': 'review',
            'valid_row_count': valid_count,
            'error_count': len(errors),
            'preview_message': self._format_issue_report(errors),
            'result_message': False,
        })
        return self._reopen_wizard()

    def action_import(self):
        """Backward-compatible entry point; UI uses the preview explicitly."""
        return self.action_preview()

    def action_import_valid_rows(self):
        self.ensure_one()
        self._check_access()
        # Serializes imports so two simultaneous uploads cannot pass the same
        # duplicate check and create duplicate slots.
        self.env.cr.execute(
            "SELECT pg_advisory_xact_lock(hashtext(%s))",
            ['slot_dashboard.shift_import'],
        )
        groups, update_slots, _duplicate_count, errors, valid_count = (
            self._prepare_import()
        )
        if not valid_count:
            raise ValidationError(
                _('İçe aktarılabilecek geçerli vardiya satırı bulunamadı.')
            )
        batch = self._create_plan(
            groups,
            update_slots,
            len(errors),
        )
        issue_report = self._format_issue_report(errors)
        self.write({
            'state': 'done',
            'valid_row_count': valid_count,
            'error_count': len(errors),
            'preview_message': issue_report,
            'result_message': _(
                '%(slots)s vardiya açıldı, %(updated)s vardiya güncellendi ve '
                '%(shifts)s geçerli personel satırı uygulandı.\n'
                '%(skipped)s hatalı/çakışan/tekrarlı satır aktarılmadı.'
            ) % {
                'slots': batch.slot_count,
                'updated': batch.updated_slot_count,
                'shifts': batch.shift_count,
                'skipped': batch.skipped_count,
            },
        })
        return self._reopen_wizard()

    def action_reset(self):
        self.ensure_one()
        self.write({
            'state': 'upload',
            'preview_message': False,
            'result_message': False,
            'valid_row_count': 0,
            'error_count': 0,
        })
        return self._reopen_wizard()

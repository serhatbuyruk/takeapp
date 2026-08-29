import base64
import io
from collections import defaultdict

import xlsxwriter

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


RECONCILIATION_STATUS_LABELS = {
    'not_submitted': 'Kurye Beyanı Bekleniyor',
    'pending': 'Restoran Onayı Bekleniyor',
    'approved': 'Restoran Onayladı',
    'rejected': 'Restoran Reddetti',
    'auto_approved': 'Otomatik Onaylandı',
    'mixed': 'Birden Fazla Onay Durumu',
}


class SlotDashboardEarningWizard(models.TransientModel):
    _name = 'slot.dashboard.earning.wizard'
    _description = 'Kurye ve Restoran Hakediş Raporu'

    report_type = fields.Selection(
        [
            ('courier', 'Kurye Hakedişleri'),
            ('restaurant', 'Restoran Borçları'),
        ],
        string='Rapor Türü',
        required=True,
        default='courier',
    )
    grouping_type = fields.Selection(
        [
            ('combined', 'Birleşik Toplam'),
            ('daily', 'Gün Gün'),
        ],
        string='Rapor Görünümü',
        required=True,
        default='combined',
        help=(
            'Birleşik Toplam seçilen dönemi kurye/restoran başına tek satırda; '
            'Gün Gün ise her tarihi ayrı satırda gösterir.'
        ),
    )

    date_start = fields.Date(
        string='Başlangıç Tarihi',
        required=True,
        default=fields.Date.context_today,
    )
    date_end = fields.Date(
        string='Bitiş Tarihi',
        required=True,
        default=fields.Date.context_today,
    )
    courier_scope = fields.Selection(
        [
            ('all', 'Tüm Kuryeler'),
            ('selected', 'Belirli Kuryeler'),
            ('dedicated', 'Dedike Kuryeler'),
        ],
        string='Kurye Filtresi',
        required=True,
        default='all',
    )
    courier_ids = fields.Many2many(
        'res.partner',
        'slot_dashboard_earning_wizard_courier_rel',
        'wizard_id',
        'courier_id',
        string='Kuryeler',
        domain=[('user_role', '=', 'kurye')],
    )
    restaurant_scope = fields.Selection(
        [
            ('all', 'Tüm Restoranlar'),
            ('selected', 'Belirli Restoranlar'),
            ('dashboard', 'Dashboard Restoranları'),
        ],
        string='Restoran Filtresi',
        required=True,
        default='all',
    )
    restaurant_ids = fields.Many2many(
        'res.partner',
        'slot_dashboard_earning_wizard_restaurant_rel',
        'wizard_id',
        'restaurant_id',
        string='Restoranlar',
        domain=[('user_role', '=', 'magaza')],
    )
    line_ids = fields.One2many(
        'slot.dashboard.earning.line',
        'wizard_id',
        string='Hakedişler',
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Para Birimi',
        default=lambda self: self.env.company.currency_id,
        readonly=True,
    )
    total_amount = fields.Monetary(
        string='Genel Toplam',
        currency_field='currency_id',
        compute='_compute_totals',
    )
    total_hours = fields.Float(
        string='Toplam Çalışma Saati',
        compute='_compute_totals',
    )
    total_packages = fields.Integer(
        string='Toplam Paket',
        compute='_compute_totals',
    )
    export_file = fields.Binary(
        string='Excel Dosyası',
        readonly=True,
        attachment=False,
    )
    export_filename = fields.Char(string='Excel Dosya Adı', readonly=True)

    @api.depends(
        'line_ids.total_earning',
        'line_ids.working_hours',
        'line_ids.package_count',
    )
    def _compute_totals(self):
        for wizard in self:
            wizard.total_amount = sum(wizard.line_ids.mapped('total_earning'))
            wizard.total_hours = sum(wizard.line_ids.mapped('working_hours'))
            wizard.total_packages = sum(wizard.line_ids.mapped('package_count'))

    def _check_access(self):
        self.env['slots.profile']._operation_dashboard_check_access()

    def _validate_filters(self):
        self.ensure_one()
        if self.date_start > self.date_end:
            raise ValidationError(
                _('Başlangıç tarihi bitiş tarihinden sonra olamaz.')
            )
        if (
            self.report_type == 'courier'
            and self.courier_scope == 'selected'
            and not self.courier_ids
        ):
            raise ValidationError(_('En az bir kurye seçin.'))
        if (
            self.report_type == 'restaurant'
            and self.restaurant_scope == 'selected'
            and not self.restaurant_ids
        ):
            raise ValidationError(_('En az bir restoran seçin.'))

    @staticmethod
    def _line_earnings(line, slot, restaurant):
        """Calculate current courier earnings independent of approval state."""
        orders = line._package_reconciliation_orders(slot, restaurant)
        package_count = line._billable_package_count(
            restaurant, tariff='courier'
        )
        working_hours = line._package_reconciliation_working_hours(slot)
        package_earning = (
            package_count * restaurant.paket_basi_ucret
            if restaurant.paket_basi_ucret > 0 else 0.0
        )
        hourly_earning = (
            working_hours * restaurant.saatlik_ucret
            if restaurant.saatlik_ucret > 0 else 0.0
        )
        distance_earning = sum(
            max(
                restaurant.get_distance_fee(
                    order.restoran_paket_mesafesi or order.mesafe
                ),
                0.0,
            )
            for order in orders
        )
        promotion_earning = (
            package_count * slot.slot_promosyon_ucret
            if slot.slot_promosyon_ucret > 0 else 0.0
        )
        percentage_earning = (
            sum(
                restaurant.yuzdelik_kar_orani / 100.0
                * order.toplam_siparis_tutari
                for order in orders
            )
            if restaurant.yuzdelik_kar_orani > 0 else 0.0
        )
        total = (
            package_earning + hourly_earning + distance_earning
            + promotion_earning + percentage_earning
        )
        return {
            'hours': working_hours,
            'packages': package_count,
            'reported_packages': (
                line.kurye_beyan_paket_sayisi
                if line.kurye_paket_beyani_yapildi
                else max((line.slot_paket_sayisi or 0), 0)
            ),
            'extra_hours': line.puantaj_ek_saat or 0.0,
            'extra_packages': line.puantaj_ek_paket_sayisi or 0,
            'package': package_earning,
            'hourly': hourly_earning,
            'distance': distance_earning,
            'promotion': promotion_earning,
            'percentage': percentage_earning,
            'total': total,
        }

    @staticmethod
    def _restaurant_debt(line, slot, restaurant):
        """Calculate the restaurant's net platform debt for one shift line."""
        orders = line._package_reconciliation_orders(slot, restaurant)
        package_count = line._billable_package_count(
            restaurant, tariff='restaurant'
        )
        working_hours = line._package_reconciliation_working_hours(slot)

        package_charge = (
            package_count * restaurant.restoran_paket_basi_ucret
            if restaurant.restoran_paket_basi_ucret > 0 else 0.0
        )
        hourly_charge = (
            working_hours * restaurant.restoran_saatlik_ucret
            if restaurant.restoran_saatlik_ucret > 0 else 0.0
        )
        distance_charge = sum(
            fee
            for fee in (
                restaurant.get_platform_distance_fee(
                    order.restoran_paket_mesafesi or order.mesafe
                )
                for order in orders
            )
            if fee > 0
        )
        percentage_charge = (
            sum(
                restaurant.restoran_yuzdelik_kar_orani
                / 100.0
                * order.toplam_siparis_tutari
                for order in orders
            )
            if restaurant.restoran_yuzdelik_kar_orani > 0 else 0.0
        )
        cash_collected = sum(
            orders.mapped('kuryenin_musteriden_aldigi_odeme')
        )
        gross_amount = (
            package_charge
            + hourly_charge
            + distance_charge
            + percentage_charge
        )
        return {
            'hours': working_hours,
            'packages': package_count,
            'reported_packages': (
                line.kurye_beyan_paket_sayisi
                if line.kurye_paket_beyani_yapildi
                else max((line.slot_paket_sayisi or 0), 0)
            ),
            'extra_hours': line.puantaj_ek_saat or 0.0,
            'extra_packages': line.puantaj_ek_paket_sayisi or 0,
            'package': package_charge,
            'hourly': hourly_charge,
            'distance': distance_charge,
            'promotion': 0.0,
            'percentage': percentage_charge,
            'cash_collected': cash_collected,
            'gross_amount': gross_amount,
            'total': gross_amount - cash_collected,
        }

    def _prepare_lines(self):
        self.ensure_one()
        self._check_access()
        self._validate_filters()

        _start_date, timezone, utc_start, _utc_end = (
            self.env['slots.profile']._operation_dashboard_day_bounds(
                self.date_start
            )
        )
        _end_date, _timezone, _end_start, utc_end = (
            self.env['slots.profile']._operation_dashboard_day_bounds(
                self.date_end
            )
        )
        slot_domain = [
            ('start_date', '<', utc_end),
            ('end_date', '>=', utc_start),
        ]
        dashboard_filter = (
            self.report_type == 'courier'
            and self.courier_scope == 'dedicated'
        ) or (
            self.report_type == 'restaurant'
            and self.restaurant_scope == 'dashboard'
        )
        if dashboard_filter:
            dashboard_restaurants = self.env['res.partner'].sudo().search([
                ('user_role', '=', 'magaza'),
                ('operation_dashboard_enabled', '=', True),
            ])
            slot_domain.extend([
                '|',
                ('magazalar', 'in', dashboard_restaurants.ids),
                ('partner_id', 'in', dashboard_restaurants.ids),
            ])
        slots = self.env['slots.profile'].sudo().search(slot_domain)
        domain = [
            ('sequence', 'in', slots.ids),
            ('partner_id', '!=', False),
            ('partner_id.user_role', '=', 'kurye'),
            ('partner_id.name', '!=', 'Boş'),
            ('start_date', '!=', False),
        ]
        if self.report_type == 'courier' and self.courier_scope == 'selected':
            domain.append(('partner_id', 'in', self.courier_ids.ids))
        lines = self.env['skurye.profile.lines'].sudo().search(
            domain,
            order='kurye_start_date asc, id asc',
        )
        slots_by_id = {slot.id: slot for slot in slots}
        grouped = defaultdict(lambda: {
            'slot_names': set(),
            'restaurant_ids': set(),
            'restaurant_names': set(),
            'courier_ids': set(),
            'courier_names': set(),
            'statuses': set(),
            'working_hours': 0.0,
            'extra_hours': 0.0,
            'reported_package_count': 0,
            'extra_package_count': 0,
            'package_count': 0,
            'package_earning': 0.0,
            'hourly_earning': 0.0,
            'distance_earning': 0.0,
            'promotion_earning': 0.0,
            'percentage_earning': 0.0,
            'cash_collected': 0.0,
            'gross_amount': 0.0,
            'total_earning': 0.0,
        })

        for line in lines:
            slot = slots_by_id.get(line.sequence)
            if not slot:
                continue
            planned_start = line.kurye_start_date or slot.start_date
            if not planned_start:
                continue
            local_date = (
                self.env['slots.profile']
                ._operation_dashboard_localize(planned_start, timezone)
                .date()
            )
            if not self.date_start <= local_date <= self.date_end:
                continue

            restaurants = (
                line.paket_mutabakat_restoran_id
                | slot.magazalar
                | slot.partner_id
            ).filtered(lambda partner: partner.user_role == 'magaza')
            if dashboard_filter:
                restaurants = restaurants.filtered(
                    'operation_dashboard_enabled'
                )
            if self.report_type == 'restaurant' and self.restaurant_scope == 'selected':
                restaurants &= self.restaurant_ids
            restaurant = restaurants[:1]
            if not restaurant:
                continue

            entity_id = (
                line.partner_id.id
                if self.report_type == 'courier'
                else restaurant.id
            )
            group_key = (
                entity_id,
                local_date if self.grouping_type == 'daily' else False,
            )
            values = grouped[group_key]
            earnings = (
                self._line_earnings(line, slot, restaurant)
                if self.report_type == 'courier'
                else self._restaurant_debt(line, slot, restaurant)
            )
            values['slot_names'].add(slot.name or '-')
            values['restaurant_ids'].add(restaurant.id)
            values['restaurant_names'].add(restaurant.name or '-')
            values['courier_ids'].add(line.partner_id.id)
            values['courier_names'].add(line.partner_id.name or '-')
            values['statuses'].add(
                line.paket_mutabakat_durumu or 'not_submitted'
            )
            values['working_hours'] += earnings['hours']
            values['extra_hours'] += earnings['extra_hours']
            values['reported_package_count'] += earnings['reported_packages']
            values['extra_package_count'] += earnings['extra_packages']
            values['package_count'] += earnings['packages']
            values['package_earning'] += earnings['package']
            values['hourly_earning'] += earnings['hourly']
            values['distance_earning'] += earnings['distance']
            values['promotion_earning'] += earnings['promotion']
            values['percentage_earning'] += earnings['percentage']
            values['cash_collected'] += earnings.get('cash_collected', 0.0)
            values['gross_amount'] += earnings.get(
                'gross_amount', earnings['total']
            )
            values['total_earning'] += earnings['total']

        result = []
        period_label = '%s – %s' % (
            self.date_start.strftime('%d.%m.%Y'),
            self.date_end.strftime('%d.%m.%Y'),
        )
        for (group_id, group_date), values in sorted(grouped.items()):
            statuses = values.pop('statuses')
            restaurant_ids = values.pop('restaurant_ids')
            courier_ids = values.pop('courier_ids')
            earning_date = group_date or self.date_start
            current_period_label = (
                group_date.strftime('%d.%m.%Y')
                if group_date else period_label
            )
            result.append({
                'wizard_id': self.id,
                'earning_date': earning_date,
                'period_label': current_period_label,
                'courier_id': (
                    group_id if self.report_type == 'courier' else False
                ),
                'courier_names': ', '.join(
                    sorted(values.pop('courier_names'))
                ),
                'restaurant_id': (
                    group_id
                    if self.report_type == 'restaurant'
                    else min(restaurant_ids)
                ),
                'restaurant_names': ', '.join(
                    sorted(values.pop('restaurant_names'))
                ),
                'slot_names': ', '.join(sorted(values.pop('slot_names'))),
                'approval_status': (
                    next(iter(statuses)) if len(statuses) == 1 else 'mixed'
                ),
                'approval_status_detail': ' + '.join(
                    RECONCILIATION_STATUS_LABELS.get(status, status)
                    for status in sorted(statuses)
                ),
                'currency_id': self.currency_id.id,
                **values,
            })
        return result

    def action_generate(self):
        self.ensure_one()
        values_list = self._prepare_lines()
        self.line_ids.unlink()
        if values_list:
            self.env['slot.dashboard.earning.line'].create(values_list)
        self.export_file = False
        self.export_filename = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Kurye / Restoran Hakedişleri'),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref(
                'slot_dashboard.view_courier_earning_wizard_form'
            ).id,
            'target': 'new',
        }

    def action_export_xlsx(self):
        self.ensure_one()
        self._check_access()
        values_list = self._prepare_lines()
        self.line_ids.unlink()
        if values_list:
            self.env['slot.dashboard.earning.line'].create(values_list)
        if not self.line_ids:
            raise ValidationError(
                _('Seçilen filtrelerde indirilecek hakediş bulunamadı.')
            )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        is_restaurant = self.report_type == 'restaurant'
        sheet = workbook.add_worksheet(
            'Restoran Borçları' if is_restaurant else 'Kurye Hakedişleri'
        )
        title_format = workbook.add_format({
            'bold': True,
            'font_color': '#FFFFFF',
            'bg_color': '#123F70',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })
        number_format = workbook.add_format({'num_format': '#,##0.00'})
        money_format = workbook.add_format({'num_format': '#,##0.00 "₺"'})
        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#E9F6EF',
            'num_format': '#,##0.00 "₺"',
            'top': 1,
        })
        if is_restaurant:
            headers = [
                'Tarih' if self.grouping_type == 'daily' else 'Dönem',
                'Restoran', 'Kuryeler', 'Vardiyalar',
                'Onay Durumu', 'Çalışma Saati', 'Ek Saat',
                'Kurye Beyanı / Mevcut Paket', 'Ek Paket',
                'Ücretlendirilen Paket', 'Paket Bedeli',
                'Saatlik Bedel', 'KM Bedeli', 'Yüzdelik Bedel',
                'Brüt Hizmet Bedeli', 'Kuryenin Tahsil Ettiği',
                'Restoran Net Borcu',
            ]
        else:
            headers = [
                'Tarih' if self.grouping_type == 'daily' else 'Dönem',
                'Kurye', 'Restoranlar', 'Vardiyalar',
                'Onay Durumu', 'Çalışma Saati', 'Ek Saat',
                'Kurye Beyanı / Mevcut Paket', 'Ek Paket',
                'Ücretlendirilen Paket', 'Paket Kazancı',
                'Saatlik Kazanç', 'KM Kazancı', 'Promosyon',
                'Yüzdelik Kazanç', 'Toplam Hakediş',
            ]
        for column, header in enumerate(headers):
            sheet.write(0, column, header, title_format)
        sheet.freeze_panes(1, 0)
        sheet.autofilter(0, 0, len(self.line_ids), len(headers) - 1)
        sheet.set_column(0, 0, 12)
        sheet.set_column(1, 4, 24)
        sheet.set_column(5, 9, 16)
        sheet.set_column(10, len(headers) - 1, 17)

        for row_index, line in enumerate(self.line_ids, start=1):
            sheet.write(row_index, 0, line.period_label or '')
            sheet.write(
                row_index,
                1,
                line.restaurant_id.name if is_restaurant else line.courier_id.name,
            )
            sheet.write(
                row_index,
                2,
                line.courier_names if is_restaurant else line.restaurant_names,
            )
            sheet.write(row_index, 3, line.slot_names or '')
            sheet.write(
                row_index,
                4,
                line.approval_status_detail
                or RECONCILIATION_STATUS_LABELS.get(
                    line.approval_status, line.approval_status or ''
                ),
            )
            sheet.write_number(row_index, 5, line.working_hours, number_format)
            sheet.write_number(row_index, 6, line.extra_hours, number_format)
            sheet.write_number(row_index, 7, line.reported_package_count)
            sheet.write_number(row_index, 8, line.extra_package_count)
            sheet.write_number(row_index, 9, line.package_count)
            amounts = (
                [
                    line.package_earning,
                    line.hourly_earning,
                    line.distance_earning,
                    line.percentage_earning,
                    line.gross_amount,
                    line.cash_collected,
                    line.total_earning,
                ]
                if is_restaurant
                else [
                    line.package_earning,
                    line.hourly_earning,
                    line.distance_earning,
                    line.promotion_earning,
                    line.percentage_earning,
                    line.total_earning,
                ]
            )
            for column, amount in enumerate(amounts, start=10):
                sheet.write_number(row_index, column, amount, money_format)

        total_row = len(self.line_ids) + 1
        total_column = len(headers) - 1
        sheet.write(total_row, total_column - 1, 'GENEL TOPLAM', total_format)
        sheet.write_number(
            total_row, total_column, self.total_amount, total_format
        )
        workbook.close()
        self.write({
            'export_file': base64.b64encode(output.getvalue()),
            'export_filename': '%s_%s_%s.xlsx' % (
                '%s_%s' % (
                    'restoran_borclari'
                    if is_restaurant else 'kurye_hakedisleri',
                    'gun_gun'
                    if self.grouping_type == 'daily' else 'birlesik',
                ),
                self.date_start,
                self.date_end,
            ),
        })
        return {
            'type': 'ir.actions.act_url',
            'url': (
                '/web/content?model=slot.dashboard.earning.wizard'
                '&id=%s&field=export_file&filename_field=export_filename'
                '&download=true'
            ) % self.id,
            'target': 'self',
        }


class SlotDashboardEarningLine(models.TransientModel):
    _name = 'slot.dashboard.earning.line'
    _description = 'Kurye ve Restoran Hakediş Rapor Satırı'
    _order = 'restaurant_id, courier_id'

    wizard_id = fields.Many2one(
        'slot.dashboard.earning.wizard',
        required=True,
        ondelete='cascade',
        index=True,
    )
    earning_date = fields.Date(string='Tarih', required=True, index=True)
    period_label = fields.Char(string='Tarih', required=True, readonly=True)
    report_type = fields.Selection(
        related='wizard_id.report_type',
        string='Rapor Türü',
        readonly=True,
    )
    courier_id = fields.Many2one(
        'res.partner',
        string='Kurye',
        readonly=True,
    )
    restaurant_id = fields.Many2one(
        'res.partner',
        string='Restoran',
        required=True,
        readonly=True,
    )
    restaurant_names = fields.Char(string='Restoranlar', readonly=True)
    courier_names = fields.Char(string='Kuryeler', readonly=True)
    slot_names = fields.Char(string='Vardiyalar', readonly=True)
    approval_status = fields.Selection(
        [
            ('not_submitted', 'Kurye Beyanı Bekleniyor'),
            ('pending', 'Restoran Onayı Bekleniyor'),
            ('approved', 'Restoran Onayladı'),
            ('rejected', 'Restoran Reddetti'),
            ('auto_approved', 'Otomatik Onaylandı'),
            ('mixed', 'Birden Fazla Onay Durumu'),
        ],
        string='Restoran Onayı',
        readonly=True,
    )
    approval_status_detail = fields.Char(
        string='Restoran Onay Detayı',
        readonly=True,
    )
    working_hours = fields.Float(string='Çalışma Saati', readonly=True)
    extra_hours = fields.Float(string='Ek Saat', readonly=True)
    reported_package_count = fields.Integer(
        string='Kurye Beyanı / Mevcut Paket', readonly=True,
    )
    extra_package_count = fields.Integer(string='Ek Paket', readonly=True)
    package_count = fields.Integer(string='Paket', readonly=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Para Birimi',
        required=True,
        readonly=True,
    )
    package_earning = fields.Monetary(
        string='Paket Kazancı',
        currency_field='currency_id',
        readonly=True,
    )
    hourly_earning = fields.Monetary(
        string='Saatlik Kazanç',
        currency_field='currency_id',
        readonly=True,
    )
    distance_earning = fields.Monetary(
        string='KM Kazancı',
        currency_field='currency_id',
        readonly=True,
    )
    promotion_earning = fields.Monetary(
        string='Promosyon',
        currency_field='currency_id',
        readonly=True,
    )
    percentage_earning = fields.Monetary(
        string='Yüzdelik Kazanç',
        currency_field='currency_id',
        readonly=True,
    )
    gross_amount = fields.Monetary(
        string='Brüt Hizmet Bedeli',
        currency_field='currency_id',
        readonly=True,
    )
    cash_collected = fields.Monetary(
        string='Kuryenin Tahsil Ettiği',
        currency_field='currency_id',
        readonly=True,
    )
    total_earning = fields.Monetary(
        string='Toplam Hakediş',
        currency_field='currency_id',
        readonly=True,
    )

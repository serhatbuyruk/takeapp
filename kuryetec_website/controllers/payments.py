from datetime import datetime, time, timedelta

import pytz
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request


class KuryetecPaymentsController(http.Controller):

    @staticmethod
    def _parse_range(value):
        try:
            period, raw_offset = (value or 'week:0').split(':', 1)
            offset = int(raw_offset)
        except (TypeError, ValueError):
            return 'week', 0
        if period not in ('week', 'month'):
            return 'week', 0
        return period, max(min(offset, 12), -120)

    @staticmethod
    def _local_period(period, offset, timezone):
        now_local = datetime.now(timezone)
        if period == 'month':
            month_index = (
                now_local.year * 12 + now_local.month - 1 + offset
            )
            year, zero_based_month = divmod(month_index, 12)
            start_date = datetime(
                year,
                zero_based_month + 1,
                1,
            ).date()
            next_month_index = month_index + 1
            next_year, next_zero_based_month = divmod(next_month_index, 12)
            end_exclusive_date = datetime(
                next_year,
                next_zero_based_month + 1,
                1,
            ).date()
        else:
            current_monday = now_local.date() - timedelta(
                days=now_local.weekday()
            )
            start_date = current_monday + timedelta(weeks=offset)
            end_exclusive_date = start_date + timedelta(days=7)

        start_local = timezone.localize(
            datetime.combine(start_date, time.min)
        )
        end_local = timezone.localize(
            datetime.combine(end_exclusive_date, time.min)
        )
        start_utc = start_local.astimezone(pytz.UTC).replace(tzinfo=None)
        end_utc = end_local.astimezone(pytz.UTC).replace(tzinfo=None)
        return start_date, end_exclusive_date, start_utc, end_utc

    @http.route(
        '/odemeler',
        type='http',
        auth='user',
        website=True,
        methods=['GET'],
        sitemap=False,
    )
    def courier_payments(self, **params):
        payments_page = request.env.ref(
            'kuryetec_website.website_page_100',
            raise_if_not_found=False,
        )
        if not payments_page or not payments_page.sudo().is_published:
            raise NotFound()

        courier = request.env.user.partner_id
        period, offset = self._parse_range(params.get('range'))
        approval_status = params.get('approval_status', 'all')
        if approval_status not in ('all', 'pending', 'approved', 'rejected'):
            approval_status = 'all'

        timezone_name = (
            request.env.user.tz
            or request.env.context.get('tz')
            or 'Europe/Istanbul'
        )
        try:
            timezone = pytz.timezone(timezone_name)
        except pytz.UnknownTimeZoneError:
            timezone = pytz.timezone('Europe/Istanbul')

        start_date, end_exclusive_date, start_utc, end_utc = (
            self._local_period(period, offset, timezone)
        )
        order_model = request.env['corders.profile'].sudo()
        order_base_domain = [
            ('kurye', '=', courier.id),
            ('siparis_durumu', '=', 'teslim_edildi'),
        ]
        completed_orders = order_model.search(order_base_domain + [
            ('paket_bitis_tarihi', '>=', start_utc),
            ('paket_bitis_tarihi', '<', end_utc),
        ])
        # Eski teslim edilmiş kayıtlarda bitiş zamanı boşsa durum zamanını kullan.
        legacy_completed_orders = order_model.search(order_base_domain + [
            ('paket_bitis_tarihi', '=', False),
            ('siparis_durumu_zamani', '>=', start_utc),
            ('siparis_durumu_zamani', '<', end_utc),
        ])
        completed_orders |= legacy_completed_orders
        completed_orders = completed_orders.sorted(
            key=lambda order: (
                order.paket_bitis_tarihi
                or order.siparis_durumu_zamani
                or order.siparis_tarihi
                or datetime.min
            ),
            reverse=True,
        )

        line_model = request.env['skurye.profile.lines'].sudo()
        reconciliation_domain = [
            ('partner_id', '=', courier.id),
            ('paket_mutabakat_gerekli', '=', True),
            ('kurye_paket_beyani_yapildi', '=', True),
            ('paket_mutabakat_slot_id.end_date', '>=', start_utc),
            ('paket_mutabakat_slot_id.end_date', '<', end_utc),
        ]
        coverage_lines = line_model.search(reconciliation_domain)
        if approval_status == 'pending':
            reconciliation_domain.append(
                ('paket_mutabakat_durumu', '=', 'pending')
            )
        elif approval_status == 'approved':
            reconciliation_domain.append(
                ('paket_mutabakat_durumu', 'in', ('approved', 'auto_approved'))
            )
        elif approval_status == 'rejected':
            reconciliation_domain.append(
                ('paket_mutabakat_durumu', '=', 'rejected')
            )
        reconciliation_lines = line_model.search(
            reconciliation_domain,
            order='paket_mutabakat_slot_id desc, id desc',
        )

        # Sabit slot mutabakatına giren siparişleri tekrar bağımsız paket
        # kazancı olarak toplamayarak aynı ödemenin iki kez görünmesini önle.
        covered_order_ids = set()
        for line in coverage_lines:
            covered_order_ids.update(
                line._package_reconciliation_orders().ids
            )
        standalone_orders = completed_orders.filtered(
            lambda order: order.id not in covered_order_ids
        )
        legacy_lines = line_model.search([
            ('partner_id', '=', courier.id),
            ('paket_mutabakat_gerekli', '=', False),
            ('end_date', '>=', start_utc),
            ('end_date', '<', end_utc),
        ])

        approved_lines = reconciliation_lines.filtered(
            lambda line: line.paket_mutabakat_durumu
            in ('approved', 'auto_approved')
        )
        pending_lines = reconciliation_lines.filtered(
            lambda line: line.paket_mutabakat_durumu == 'pending'
        )
        rejected_lines = reconciliation_lines.filtered(
            lambda line: line.paket_mutabakat_durumu == 'rejected'
        )
        confirmed_total = (
            sum(approved_lines.mapped('mutabakat_toplam_kazanc'))
            + sum(legacy_lines.mapped('sale_price'))
            + sum(standalone_orders.mapped('sale_price'))
        )
        pending_total = sum(
            pending_lines.mapped('mutabakat_toplam_kazanc')
        )
        visible_total = confirmed_total + pending_total
        working_hours = (
            sum(reconciliation_lines.mapped('mutabakat_hesaplanan_saat'))
            + sum(legacy_lines.mapped('kurye_calisma_saati'))
        )

        query_suffix = '&approval_status=%s' % approval_status
        previous_url = '/odemeler?range=%s:%s%s' % (
            period,
            offset - 1,
            query_suffix,
        )
        next_url = '/odemeler?range=%s:%s%s' % (
            period,
            offset + 1,
            query_suffix,
        )
        period_label = (
            '%s %s'
            % (
                (
                    'Ocak',
                    'Şubat',
                    'Mart',
                    'Nisan',
                    'Mayıs',
                    'Haziran',
                    'Temmuz',
                    'Ağustos',
                    'Eylül',
                    'Ekim',
                    'Kasım',
                    'Aralık',
                )[start_date.month - 1],
                start_date.year,
            )
            if period == 'month'
            else '%s – %s'
            % (
                start_date.strftime('%d.%m.%Y'),
                (end_exclusive_date - timedelta(days=1)).strftime('%d.%m.%Y'),
            )
        )

        values = {
            'tamamlanan_siparisler': standalone_orders,
            'kurye_lines': legacy_lines,
            'reconciliation_lines': reconciliation_lines,
            'pending_reconciliation_lines': pending_lines,
            'approved_reconciliation_lines': approved_lines,
            'rejected_reconciliation_lines': rejected_lines,
            'onay_bekleyen_tutar': pending_total,
            'onaylanan_tutar': confirmed_total,
            'toplam_saatlik_tutar': (
                sum(reconciliation_lines.mapped('mutabakat_saatlik_kazanc'))
                + sum(legacy_lines.mapped('sale_price'))
            ),
            'kurye_calisma_saati': working_hours,
            'toplam_baz_tutar': (
                sum(reconciliation_lines.mapped('mutabakat_paket_kazanci'))
                + sum(standalone_orders.mapped('baz_price'))
            ),
            'toplam_km_tutar': (
                sum(reconciliation_lines.mapped('mutabakat_km_kazanci'))
                + sum(standalone_orders.mapped('toplam_km_price'))
            ),
            'toplam_promosyon_tutar': (
                sum(reconciliation_lines.mapped('mutabakat_promosyon_kazanci'))
                + sum(standalone_orders.mapped('promosyon_price'))
            ),
            'toplam_bahsis_tutar': sum(
                standalone_orders.mapped('bahsis_price')
            ),
            'toplam_sale_tutar': visible_total,
            'ortalama_saatlik_kazanc': (
                visible_total / working_hours if working_hours else 0.0
            ),
            'payment_period': period,
            'payment_offset': offset,
            'payment_range': '%s:%s' % (period, offset),
            'approval_status': approval_status,
            'period_label': period_label,
            'previous_url': previous_url,
            'next_url': next_url,
            'period_start_date': start_date,
            'period_end_date': end_exclusive_date - timedelta(days=1),
        }
        return request.render(
            'website.odemeler',
            values,
        )

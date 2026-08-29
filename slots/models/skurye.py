# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta

import pytz

from odoo import api, fields, models


# Creating Model/Table to Store Doctor Details
# https://www.youtube.com/watch?v=L6MxDR71_1k&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=2
class skuryeProfile(models.Model):
    _name = 'skurye.profile'
    _description = 'Skurye Record'

    name = fields.Char("Name")
    currency_id = fields.Many2one('res.currency', string='Currency Id')
    price = fields.Monetary(string="Amount", currency_field='currency_id')
    skurye_profile_status = fields.Selection([('not_paid','Not Paid'),('in_profile','In Profile'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
                                    string="Customer Profile Status ", default="not_paid", tracking=True
                                    )
    description = fields.Text("Description")
    sequence = fields.Integer(string="Sequence")
    color = fields.Integer(string="Color")
    
class skuryeProfileLines(models.Model):
    _name = 'skurye.profile.lines'
    _description = 'Skurye Lines Record'

    name = fields.Char("Name")
    slot_start_date = fields.Datetime(string="Vardiya Başlangıç Zamanı", copy=False)
    slot_end_date = fields.Datetime(string="Vardiya Bitiş Zamanı", copy=False)
    partner_id = fields.Many2one('res.partner', string="Kurye", copy=True, domain="[('user_role', '=', 'kurye')]")
    kurye_start_date = fields.Datetime(string="Kurye İş Başlangıcı", copy=False)
    kurye_end_date = fields.Datetime(string="Kurye İş Bitişi", copy=False)
    active = fields.Boolean(string="Aktif", default=True, copy=False)
    kurye_active = fields.Boolean(string="Kurye Aktiflik", default=True, copy=False)
    start_date = fields.Datetime(string="Başlattığı Zaman", copy=False)
    end_date = fields.Datetime(string="Bitirdiği Zaman", copy=False)
    kurye_yoklamasi = fields.Boolean(string="Yoklama", copy=False)
    gecikme_durumu = fields.Boolean(string="Gecikme Durumu", copy=False)
    gecikme_dakikasi = fields.Integer(string="Gecikme Dakikası", copy=False)
    erken_kapatma = fields.Boolean(string="Erken Kapatma", copy=False)
    bitise_kalan_dakika = fields.Integer(string="Bitişe Kalan Dakika", copy=False)
    slot_paket_sayisi = fields.Integer(string="Vardiya Paket Sayısı", copy=False)
    kurye_calisma_saati = fields.Float(string="Kuryenin Çalıştığı Saat", copy=False)
    operasyon_admin_durdurdu = fields.Boolean(
        string="Operasyon Yöneticisi Durdurdu",
        default=False,
        copy=False,
        index=True,
    )
    operasyon_duraklatma_zamani = fields.Datetime(
        string="Operasyon Duraklatma Zamanı",
        copy=False,
    )
    operasyon_toplam_duraklatma_saniyesi = fields.Integer(
        string="Toplam Duraklatma Süresi (Sn)",
        default=0,
        copy=False,
    )
    
    sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=32, tracking=True, copy=False)
    sale_price = fields.Monetary(string="Kurye Kazancı", currency_field='sale_price_currency_id', tracking=True, copy=False)
    baz_price = fields.Monetary(string="Baz", currency_field='sale_price_currency_id', tracking=True)
    toplam_km_price = fields.Monetary(string="Toplam Km Ücreti", currency_field='sale_price_currency_id', tracking=True)
    promosyon_price = fields.Monetary(string="Promosyon", currency_field='sale_price_currency_id', tracking=True)
    bahsis_price = fields.Monetary(string="Bahşiş", currency_field='sale_price_currency_id', tracking=True)
    kurye_odeme_durumu = fields.Selection([('not_paid','Not Paid'),('paid','Paid')],
                                    string="Kuryeye Ödeme Durumu", default="not_paid", tracking=True
                                    )
    restoran_borc_toplami = fields.Monetary(string="Restoran Borç Toplamı", currency_field='sale_price_currency_id', tracking=True)
    restoran_borc_durumu = fields.Selection([('not_paid','Not Paid'),('paid','Paid')],
                                    string="Restoran Borç Durumu", default="not_paid", tracking=True
                                    )
    # currency_id = fields.Many2one('res.currency', string='Currency Id')
    # price = fields.Monetary(string="Amount", currency_field='currency_id')
    # description = fields.Text("Description")
    # skurye_profile_status = fields.Selection([('not_paid','Not Paid'),('in_profile','In Profile'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
    #                                 string="Customer Profile Status ", default="not_paid"
    #                                 )
    # date = fields.Datetime(string="Date", default=fields.Datetime.now)
    order_sequence = fields.Integer(string="Sequence")
    sequence = fields.Integer(string="Sequence", index=True)
    color = fields.Integer(string="Color")

    def _courier_planned_period(self):
        self.ensure_one()
        slot = self.env['slots.profile'].browse(self.sequence).exists()
        if not slot:
            return slot, False, False
        if self.kurye_start_date and self.kurye_end_date:
            return slot, self.kurye_start_date, self.kurye_end_date
        return slot, slot.start_date, slot.end_date

    def calculate_worked_hours_until(self, ended_at):
        """Return payable net hours with the operational late-start rule.

        A start delay up to and including 20 minutes does not reduce payment.
        Once the delay exceeds 20 minutes, payment starts at the courier's
        actual check-in. Dashboard stop/resume gaps are always deducted.
        """
        self.ensure_one()
        if not self.start_date or not ended_at:
            return 0.0
        _slot, planned_start, _planned_end = self._courier_planned_period()
        paid_start = self.start_date
        if planned_start:
            delay_seconds = (self.start_date - planned_start).total_seconds()
            if delay_seconds <= 20 * 60:
                paid_start = planned_start
        if ended_at <= paid_start:
            return 0.0
        elapsed_seconds = (ended_at - paid_start).total_seconds()
        paused_seconds = max(
            self.operasyon_toplam_duraklatma_saniyesi or 0,
            0,
        )
        return max(elapsed_seconds - paused_seconds, 0.0) / 3600.0

    @api.model
    def get_current_courier_line(self, courier):
        """Return the courier line whose own planned period contains now."""
        if not courier:
            return self.browse()
        now = fields.Datetime.now()
        candidates = self.sudo().search([
            ('partner_id', '=', courier.id),
            ('active', '=', True),
            ('kurye_active', '=', True),
        ], order='kurye_start_date asc, id asc')
        for line in candidates:
            slot, planned_start, planned_end = line._courier_planned_period()
            if (
                slot
                and slot.active_status
                and planned_start
                and planned_end
                and planned_start <= now < planned_end
            ):
                return line
        return self.browse()

    @api.model
    def get_courier_upcoming_slots(self, courier, hours=3, limit=3):
        """Return active current/upcoming slots using courier-line periods."""
        if not courier:
            return self.env['slots.profile']
        now = fields.Datetime.now()
        horizon = now + timedelta(hours=max(int(hours or 0), 0))
        candidates = self.sudo().search([
            ('partner_id', '=', courier.id),
            ('active', '=', True),
            ('kurye_active', '=', True),
        ])
        eligible = []
        seen_slot_ids = set()
        for line in candidates:
            slot, planned_start, planned_end = line._courier_planned_period()
            if (
                slot
                and slot.active_status
                and slot.id not in seen_slot_ids
                and planned_start
                and planned_end
                and planned_end > now
                and planned_start <= horizon
            ):
                eligible.append((planned_start, slot))
                seen_slot_ids.add(slot.id)
        eligible.sort(key=lambda item: (item[0], item[1].id))
        slots = self.env['slots.profile']
        for _planned_start, slot in eligible[:max(int(limit or 0), 0)]:
            slots |= slot
        return slots

    @api.model
    def get_courier_day_slots(self, courier, selected_date):
        """Return courier slots belonging to the selected local calendar day.

        Excel-imported full-day parent slots start at 21:00 UTC on the
        previous day.  Their courier lines carry the actual local plan date,
        so filtering only ``slots.profile.start_date`` displays the shift one
        day early on the website.  Prefer that explicit plan date when the
        optional dashboard field exists and retain a timezone-aware fallback
        for legacy/manual slots.
        """
        slots = self.env['slots.profile']
        if not courier or not selected_date:
            return slots

        courier = self.env['res.partner'].browse(courier.id).exists()
        if not courier:
            return slots
        current_partner = self.env.user.partner_id
        if (
            current_partner.user_role == 'kurye'
            and courier != current_partner
        ):
            return slots

        try:
            target_date = fields.Date.to_date(selected_date)
        except (TypeError, ValueError):
            return slots

        try:
            timezone = pytz.timezone(self.env.user.tz or 'Europe/Istanbul')
        except pytz.UnknownTimeZoneError:
            timezone = pytz.timezone('Europe/Istanbul')
        local_start = timezone.localize(datetime.combine(target_date, time.min))
        local_end = local_start + timedelta(days=1)
        utc_start = local_start.astimezone(pytz.UTC).replace(tzinfo=None)
        utc_end = local_end.astimezone(pytz.UTC).replace(tzinfo=None)

        line_model = self.sudo()
        base_domain = [
            ('partner_id', '=', courier.id),
            ('active', '=', True),
        ]
        has_plan_date = 'shift_plan_date' in line_model._fields
        if has_plan_date:
            lines = line_model.search(
                base_domain + [('shift_plan_date', '=', target_date)],
                order='kurye_start_date, id',
            )
            legacy_lines = line_model.search(
                base_domain + [
                    ('shift_plan_date', '=', False),
                    ('kurye_start_date', '>=', utc_start),
                    ('kurye_start_date', '<', utc_end),
                ],
                order='kurye_start_date, id',
            )
        else:
            lines = line_model.browse()
            legacy_lines = line_model.search(
                base_domain + [
                    ('kurye_start_date', '>=', utc_start),
                    ('kurye_start_date', '<', utc_end),
                ],
                order='kurye_start_date, id',
            )

        result = slots
        seen_slot_ids = set()
        for line in lines | legacy_lines:
            slot = slots.sudo().browse(line.sequence).exists()
            if slot and slot.id not in seen_slot_ids:
                result |= slot
                seen_slot_ids.add(slot.id)

        # Old/manual records may not have courier-specific planned hours.
        legacy_slots = slots.sudo().search([
            ('skurye_profile_lines.partner_id', '=', courier.id),
            ('start_date', '>=', utc_start),
            ('start_date', '<', utc_end),
        ], order='start_date, id')
        for slot in legacy_slots:
            courier_lines = slot.skurye_profile_lines.filtered(
                lambda line: line.partner_id == courier and line.active
            )
            is_legacy = any(
                not line.kurye_start_date
                and (not has_plan_date or not line.shift_plan_date)
                for line in courier_lines
            )
            if is_legacy and slot.id not in seen_slot_ids:
                result |= slot
                seen_slot_ids.add(slot.id)
        return result
    
    
class realestatesProfileInherit(models.Model):
    _inherit = 'slots.profile'

    skurye_profile_lines = fields.One2many('skurye.profile.lines', 'sequence', string='Skurye Lines',tracking=True, copy=True)
    

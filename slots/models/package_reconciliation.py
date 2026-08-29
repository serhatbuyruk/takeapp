from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


PACKAGE_RECONCILIATION_FIELDS = {
    'paket_mutabakat_gerekli',
    'kurye_beyan_paket_sayisi',
    'kurye_paket_beyani_yapildi',
    'kurye_paket_beyan_zamani',
    'paket_mutabakat_durumu',
    'paket_mutabakat_slot_id',
    'paket_mutabakat_restoran_id',
    'paket_mutabakat_son_tarih',
    'paket_mutabakat_karar_zamani',
    'paket_mutabakat_karar_user_id',
    'paket_mutabakat_red_nedeni',
    'paket_sayisi_admin_revize_zamani',
    'paket_sayisi_admin_revize_user_id',
    'mutabakat_hesaplanan_saat',
    'mutabakat_paket_kazanci',
    'mutabakat_saatlik_kazanc',
    'mutabakat_km_kazanci',
    'mutabakat_promosyon_kazanci',
    'mutabakat_yuzdelik_kazanc',
    'mutabakat_toplam_kazanc',
}

PACKAGE_RECONCILIATION_APPROVAL_HOURS = 24


class SkuryeProfileLines(models.Model):
    _inherit = 'skurye.profile.lines'

    paket_mutabakat_gerekli = fields.Boolean(
        string='Paket Mutabakatı Gerekli',
        default=False,
        copy=False,
        index=True,
        help=(
            'Yalnızca özellik devreye alındıktan sonra oluşturulan sabit kurye '
            'slotları için işaretlenir. Böylece eski slotlar kuryenin ekranını '
            'geriye dönük olarak kilitlemez.'
        ),
    )
    kurye_beyan_paket_sayisi = fields.Integer(
        string='Kuryenin Belirttiği Paket Sayısı',
        copy=False,
    )
    kurye_paket_beyani_yapildi = fields.Boolean(
        string='Kurye Paket Beyanını Gönderdi',
        default=False,
        copy=False,
        index=True,
    )
    kurye_paket_beyan_zamani = fields.Datetime(
        string='Kurye Beyan Zamanı',
        copy=False,
        index=True,
    )
    paket_mutabakat_durumu = fields.Selection(
        [
            ('not_submitted', 'Kurye Beyanı Bekleniyor'),
            ('pending', 'Restoran Onayı Bekleniyor'),
            ('approved', 'Restoran Onayladı'),
            ('rejected', 'Restoran Reddetti'),
            ('auto_approved', 'Otomatik Onaylandı'),
        ],
        string='Paket Mutabakat Durumu',
        default='not_submitted',
        copy=False,
        required=True,
        index=True,
    )
    paket_mutabakat_slot_id = fields.Many2one(
        'slots.profile',
        string='Mutabakat Vardiyası',
        copy=False,
        index=True,
        ondelete='set null',
    )
    paket_mutabakat_restoran_id = fields.Many2one(
        'res.partner',
        string='Mutabakat Restoranı',
        copy=False,
        index=True,
        ondelete='set null',
    )
    paket_mutabakat_son_tarih = fields.Datetime(
        string='Restoran Son Onay Zamanı',
        copy=False,
        index=True,
    )
    paket_mutabakat_karar_zamani = fields.Datetime(
        string='Mutabakat Karar Zamanı',
        copy=False,
    )
    paket_mutabakat_karar_user_id = fields.Many2one(
        'res.users',
        string='Karar Veren',
        copy=False,
        ondelete='set null',
    )
    paket_mutabakat_red_nedeni = fields.Text(
        string='Restoran Ret Nedeni',
        copy=False,
        help='Restoranın paket beyanını reddederken zorunlu olarak girdiği açıklama.',
    )
    paket_sayisi_admin_revize_zamani = fields.Datetime(
        string='Admin Revize Zamanı',
        copy=False,
    )
    paket_sayisi_admin_revize_user_id = fields.Many2one(
        'res.users',
        string='Revize Eden Admin',
        copy=False,
        ondelete='set null',
    )
    mutabakat_hesaplanan_saat = fields.Float(
        string='Mutabakat Çalışma Saati',
        copy=False,
        readonly=True,
    )
    mutabakat_hesaplanan_paket_sayisi = fields.Integer(
        string='Ücretlendirilen Paket Sayısı',
        copy=False,
        compute='_compute_billable_package_count',
        readonly=True,
        help=(
            'Kurye beyanı ile restoranın kurye garanti paket sayısının yüksek '
            'olanıdır. Kuryenin gerçek beyanı ayrı alanda korunur.'
        ),
    )
    mutabakat_paket_kazanci = fields.Monetary(
        string='Mutabakat Paket Kazancı',
        currency_field='sale_price_currency_id',
        copy=False,
        readonly=True,
    )
    mutabakat_saatlik_kazanc = fields.Monetary(
        string='Mutabakat Saatlik Kazancı',
        currency_field='sale_price_currency_id',
        copy=False,
        readonly=True,
    )
    mutabakat_km_kazanci = fields.Monetary(
        string='Mutabakat Km Kazancı',
        currency_field='sale_price_currency_id',
        copy=False,
        readonly=True,
    )
    mutabakat_promosyon_kazanci = fields.Monetary(
        string='Mutabakat Promosyon Kazancı',
        currency_field='sale_price_currency_id',
        copy=False,
        readonly=True,
    )
    mutabakat_yuzdelik_kazanc = fields.Monetary(
        string='Mutabakat Yüzdelik Kazancı',
        currency_field='sale_price_currency_id',
        copy=False,
        readonly=True,
    )
    mutabakat_toplam_kazanc = fields.Monetary(
        string='Mutabakat Toplam Kazancı',
        currency_field='sale_price_currency_id',
        copy=False,
        readonly=True,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for line in records:
            slot = line._package_reconciliation_slot()
            if slot and slot.slot_tipi == 'sabit':
                line.with_context(package_reconciliation_write=True).write({
                    'paket_mutabakat_gerekli': True,
                    'paket_mutabakat_slot_id': slot.id,
                    'paket_mutabakat_restoran_id': slot.magazalar[:1].id,
                })
        return records

    def write(self, vals):
        protected = PACKAGE_RECONCILIATION_FIELDS.intersection(vals)
        if (
            protected
            and not self.env.context.get('package_reconciliation_write')
            and not self._is_package_reconciliation_admin()
        ):
            raise AccessError(
                _('Paket mutabakatı alanları yalnızca tanımlı işlem adımlarıyla değiştirilebilir.')
            )
        return super().write(vals)

    @api.constrains('kurye_beyan_paket_sayisi')
    def _check_courier_reported_package_count(self):
        for line in self:
            if line.kurye_beyan_paket_sayisi < 0:
                raise ValidationError(_('Paket sayısı negatif olamaz.'))

    def _is_package_reconciliation_admin(self):
        user = self.env.user
        return (
            user.has_group('base.group_system')
            or user.has_group('slots.slots_group_admin')
            or user.has_group('slots.slots_group_fullaccess')
            or user.has_group('corders.corders_group_admin')
            or user.has_group('corders.corders_group_fullaccess')
        )

    def _package_reconciliation_slot(self):
        self.ensure_one()
        if self.paket_mutabakat_slot_id:
            return self.paket_mutabakat_slot_id
        if not self.sequence:
            return self.env['slots.profile']
        # Bu projede One2many'nin legacy inverse alanı doğrudan slot kimliğini
        # taşıyan ``sequence`` kolonudur. Yeni satır oluşturulurken parent'ın
        # One2many önbelleği henüz güncel olmayabileceği için üyelik kontrolü
        # yapmak yanlış negatif üretir.
        return self.env['slots.profile'].browse(self.sequence).exists()

    def _package_reconciliation_effective_end(self, slot=None):
        self.ensure_one()
        slot = slot or self._package_reconciliation_slot()
        if self.end_date:
            return self.end_date
        if self.kurye_start_date and self.kurye_end_date:
            return self.kurye_end_date
        return slot.end_date if slot else False

    def _package_reconciliation_orders(self, slot=None, restaurant=None):
        """Return delivered orders whose delivery belongs to this fixed shift."""
        self.ensure_one()
        slot = slot or self._package_reconciliation_slot()
        restaurant = restaurant or self.paket_mutabakat_restoran_id or slot.magazalar[:1]
        if not slot or not restaurant or not self.partner_id:
            return self.env['corders.profile']
        return self.env['corders.profile'].sudo().search([
            ('kurye', '=', self.partner_id.id),
            ('magaza', '=', restaurant.id),
            ('siparis_durumu', '=', 'teslim_edildi'),
            '|',
            '&',
            ('paket_bitis_tarihi', '>=', slot.start_date),
            ('paket_bitis_tarihi', '<=', slot.end_date),
            '&',
            ('paket_bitis_tarihi', '=', False),
            '&',
            ('siparis_durumu_zamani', '>=', slot.start_date),
            ('siparis_durumu_zamani', '<=', slot.end_date),
        ])

    def _package_reconciliation_working_hours(self, slot=None):
        self.ensure_one()
        slot = slot or self._package_reconciliation_slot()
        if self.start_date:
            ended_at = self.end_date or self.kurye_end_date or (slot and slot.end_date)
            base_hours = self.calculate_worked_hours_until(ended_at)
        else:
            base_hours = self.kurye_calisma_saati or 0.0
        return max(base_hours, 0.0) + max(self.puantaj_ek_saat or 0.0, 0.0)

    def _billable_package_count(self, restaurant=None, tariff='courier'):
        """Return actual/reported packages with the selected guarantee floor."""
        self.ensure_one()
        slot = self._package_reconciliation_slot()
        restaurant = (
            restaurant
            or self.paket_mutabakat_restoran_id
            or (slot and slot.magazalar[:1])
        )
        actual_count = (
            self.kurye_beyan_paket_sayisi
            if self.kurye_paket_beyani_yapildi
            else (self.slot_paket_sayisi or 0)
        )
        actual_count += max(self.puantaj_ek_paket_sayisi or 0, 0)
        if not restaurant:
            return max(actual_count, 0)
        guarantee = (
            restaurant.restoran_garanti_paket_sayisi
            if tariff == 'restaurant'
            else restaurant.garanti_paket_sayisi
        )
        return max(actual_count, guarantee or 0, 0)

    @api.depends(
        'kurye_beyan_paket_sayisi',
        'kurye_paket_beyani_yapildi',
        'slot_paket_sayisi',
        'paket_mutabakat_restoran_id',
        'paket_mutabakat_restoran_id.garanti_paket_sayisi',
        'puantaj_ek_paket_sayisi',
    )
    def _compute_billable_package_count(self):
        for line in self:
            line.mutabakat_hesaplanan_paket_sayisi = (
                line._billable_package_count(tariff='courier')
            )

    def _refresh_package_reconciliation_earnings(self):
        """Calculate the courier earning using the restaurant's fixed-courier tariff."""
        for line in self:
            slot = line._package_reconciliation_slot()
            restaurant = line.paket_mutabakat_restoran_id or slot.magazalar[:1]
            if not slot or not restaurant:
                continue

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
            km_earning = sum(
                fee
                for fee in (
                    restaurant.get_distance_fee(
                        order.restoran_paket_mesafesi
                        or order.mesafe
                    ) for order in orders
                )
                if fee > 0
            )
            # Slot promosyonu mevcut fiyatlandırmada paket başına uygulanır.
            promotion_earning = (
                package_count * slot.slot_promosyon_ucret
                if slot.slot_promosyon_ucret > 0 else 0.0
            )
            percentage_earning = (
                sum(
                    restaurant.yuzdelik_kar_orani
                    / 100.0
                    * order.toplam_siparis_tutari
                    for order in orders
                )
                if restaurant.yuzdelik_kar_orani > 0 else 0.0
            )
            total = (
                package_earning
                + hourly_earning
                + km_earning
                + promotion_earning
                + percentage_earning
            )
            line.sudo().with_context(package_reconciliation_write=True).write({
                'mutabakat_hesaplanan_saat': working_hours,
                'mutabakat_paket_kazanci': package_earning,
                'mutabakat_saatlik_kazanc': hourly_earning,
                'mutabakat_km_kazanci': km_earning,
                'mutabakat_promosyon_kazanci': promotion_earning,
                'mutabakat_yuzdelik_kazanc': percentage_earning,
                'mutabakat_toplam_kazanc': total,
                'slot_paket_sayisi': package_count,
                'kurye_calisma_saati': working_hours,
                'baz_price': package_earning,
                'toplam_km_price': km_earning,
                'promosyon_price': promotion_earning,
                'sale_price': total,
            })
        return True

    @api.model
    def get_pending_courier_declaration(self, courier):
        if not courier or courier.user_role != 'kurye':
            return self.browse()
        candidates = self.sudo().search([
            ('partner_id', '=', courier.id),
            ('paket_mutabakat_gerekli', '=', True),
            ('kurye_paket_beyani_yapildi', '=', False),
            ('start_date', '!=', False),
        ], order='kurye_end_date asc, id asc', limit=100)
        now = fields.Datetime.now()
        for line in candidates:
            slot = line._package_reconciliation_slot()
            effective_end = line._package_reconciliation_effective_end(slot)
            if slot.slot_tipi == 'sabit' and effective_end and effective_end <= now:
                return line
        return self.browse()

    def submit_courier_package_count(self, courier, package_count):
        self.ensure_one()
        if not courier or courier.user_role != 'kurye':
            raise AccessError(_('Bu işlem yalnızca kurye hesapları tarafından yapılabilir.'))
        if self.partner_id != courier:
            raise AccessError(_('Yalnızca kendi vardiyanız için paket sayısı girebilirsiniz.'))
        if isinstance(package_count, bool):
            raise ValidationError(_('Geçerli bir paket sayısı girin.'))
        try:
            normalized_count = int(package_count)
        except (TypeError, ValueError):
            raise ValidationError(_('Geçerli bir tam sayı paket adedi girin.'))
        if str(package_count).strip() != str(normalized_count) and not isinstance(package_count, int):
            raise ValidationError(_('Paket sayısı tam sayı olmalıdır.'))
        if normalized_count < 0:
            raise ValidationError(_('Paket sayısı negatif olamaz.'))

        self.env.cr.execute(
            'SELECT id FROM skurye_profile_lines WHERE id = %s FOR UPDATE',
            [self.id],
        )
        self.invalidate_recordset()
        if self.kurye_paket_beyani_yapildi:
            raise UserError(_('Bu vardiya için paket sayısını daha önce gönderdiniz.'))
        if not self.paket_mutabakat_gerekli:
            raise UserError(_('Bu vardiya için paket mutabakatı gerekmiyor.'))
        if not self.start_date:
            raise UserError(_('Çalışılmamış bir vardiya için paket sayısı gönderilemez.'))

        slot = self._package_reconciliation_slot()
        effective_end = self._package_reconciliation_effective_end(slot)
        now = fields.Datetime.now()
        if not slot or slot.slot_tipi != 'sabit':
            raise UserError(_('Paket mutabakatı yalnızca sabit kuryeli vardiyalarda kullanılır.'))
        if not effective_end or effective_end > now:
            raise UserError(_('Vardiya süresi bitmeden paket sayısı gönderilemez.'))
        restaurant = slot.magazalar[:1]
        if not restaurant:
            raise UserError(_('Vardiyada mutabakat yapılacak restoran bulunamadı.'))

        deadline = now + timedelta(
            hours=PACKAGE_RECONCILIATION_APPROVAL_HOURS
        )
        self.sudo().with_context(package_reconciliation_write=True).write({
            'kurye_beyan_paket_sayisi': normalized_count,
            'kurye_paket_beyani_yapildi': True,
            'kurye_paket_beyan_zamani': now,
            'paket_mutabakat_durumu': 'pending',
            'paket_mutabakat_slot_id': slot.id,
            'paket_mutabakat_restoran_id': restaurant.id,
            'paket_mutabakat_son_tarih': deadline,
            'paket_mutabakat_red_nedeni': False,
        })
        self._refresh_package_reconciliation_earnings()
        reconciliation = self.env['slots.package.reconciliation'].sudo().search(
            [('line_id', '=', self.id)],
            limit=1,
        )
        if not reconciliation:
            reconciliation = self.env['slots.package.reconciliation'].sudo().create({
                'line_id': self.id,
            })
        return reconciliation


class SlotsPackageReconciliation(models.Model):
    _name = 'slots.package.reconciliation'
    _description = 'Kurye Paket Mutabakatı'
    _order = 'submitted_at desc, id desc'

    line_id = fields.Many2one(
        'skurye.profile.lines',
        string='Kurye Vardiya Satırı',
        required=True,
        index=True,
        ondelete='cascade',
    )
    courier_id = fields.Many2one(
        'res.partner',
        related='line_id.partner_id',
        string='Kurye',
        store=True,
        readonly=True,
    )
    slot_id = fields.Many2one(
        'slots.profile',
        related='line_id.paket_mutabakat_slot_id',
        string='Vardiya',
        store=True,
        readonly=True,
    )
    restaurant_id = fields.Many2one(
        'res.partner',
        related='line_id.paket_mutabakat_restoran_id',
        string='Restoran',
        store=True,
        readonly=True,
    )
    slot_date = fields.Datetime(
        related='slot_id.start_date',
        string='Vardiya Tarihi',
        store=True,
        readonly=True,
    )
    courier_reported_count = fields.Integer(
        related='line_id.kurye_beyan_paket_sayisi',
        string='Kuryenin Belirttiği Paket Sayısı',
        readonly=False,
    )
    billable_package_count = fields.Integer(
        related='line_id.mutabakat_hesaplanan_paket_sayisi',
        string='Ücretlendirilen Paket Sayısı',
        readonly=True,
    )
    state = fields.Selection(
        related='line_id.paket_mutabakat_durumu',
        string='Durum',
        store=True,
        index=True,
        readonly=True,
    )
    submitted_at = fields.Datetime(
        related='line_id.kurye_paket_beyan_zamani',
        string='Kurye Beyan Zamanı',
        store=True,
        readonly=True,
    )
    approval_deadline = fields.Datetime(
        related='line_id.paket_mutabakat_son_tarih',
        string='Onay Son Tarihi',
        store=True,
        index=True,
        readonly=True,
    )
    decided_at = fields.Datetime(
        related='line_id.paket_mutabakat_karar_zamani',
        string='Karar Zamanı',
        readonly=True,
    )
    decided_by_id = fields.Many2one(
        related='line_id.paket_mutabakat_karar_user_id',
        string='Karar Veren',
        readonly=True,
    )
    rejection_reason = fields.Text(
        related='line_id.paket_mutabakat_red_nedeni',
        string='Restoran Ret Nedeni',
        readonly=True,
    )

    _sql_constraints = [
        (
            'line_unique',
            'unique(line_id)',
            'Her kurye vardiya satırı için yalnızca bir paket mutabakatı olabilir.',
        ),
    ]

    def write(self, vals):
        if 'courier_reported_count' in vals:
            if not self.line_id._is_package_reconciliation_admin():
                raise AccessError(_('Paket sayısını yalnızca yöneticiler revize edebilir.'))
            try:
                package_count = int(vals['courier_reported_count'])
            except (TypeError, ValueError):
                raise ValidationError(_('Paket sayısı tam sayı olmalıdır.'))
            if package_count < 0:
                raise ValidationError(_('Paket sayısı negatif olamaz.'))
            result = super().write({'courier_reported_count': package_count})
            self.mapped('line_id').with_context(
                package_reconciliation_write=True
            ).write({
                'paket_sayisi_admin_revize_zamani': fields.Datetime.now(),
                'paket_sayisi_admin_revize_user_id': self.env.user.id,
            })
            self.mapped('line_id')._refresh_package_reconciliation_earnings()
            return result
        return super().write(vals)

    def _user_can_manage_restaurant(self, user):
        self.ensure_one()
        restaurant = self.restaurant_id
        partner = user.partner_id
        return bool(
            restaurant
            and (
                user in restaurant.yetkili_users
                or partner == restaurant
                or partner.parent_id == restaurant
            )
        )

    def _restaurant_decide(self, state, rejection_reason=None):
        now = fields.Datetime.now()
        rejection_reason = (rejection_reason or '').strip()
        if state == 'rejected' and not rejection_reason:
            raise ValidationError(_('Ret nedeni yazılması zorunludur.'))
        for reconciliation in self:
            if not reconciliation._user_can_manage_restaurant(self.env.user):
                raise AccessError(
                    _('Yalnızca ilgili restoranın yetkilisi bu mutabakatı değerlendirebilir.')
                )
            if reconciliation.state != 'pending':
                raise UserError(_('Bu paket mutabakatı daha önce sonuçlandırılmış.'))
            effective_deadline = (
                reconciliation.submitted_at
                + timedelta(hours=PACKAGE_RECONCILIATION_APPROVAL_HOURS)
                if reconciliation.submitted_at
                else reconciliation.approval_deadline
            )
            if effective_deadline and effective_deadline <= now:
                reconciliation.line_id.sudo().with_context(
                    package_reconciliation_write=True
                ).write({
                    'paket_mutabakat_durumu': 'auto_approved',
                    'paket_mutabakat_son_tarih': effective_deadline,
                    'paket_mutabakat_karar_zamani': now,
                    'paket_mutabakat_karar_user_id': False,
                })
                reconciliation.line_id._refresh_package_reconciliation_earnings()
                continue
            reconciliation.line_id.sudo().with_context(
                package_reconciliation_write=True
            ).write({
                'paket_mutabakat_durumu': state,
                'paket_mutabakat_son_tarih': effective_deadline,
                'paket_mutabakat_karar_zamani': now,
                'paket_mutabakat_karar_user_id': self.env.user.id,
                'paket_mutabakat_red_nedeni': (
                    rejection_reason if state == 'rejected' else False
                ),
            })
            if state == 'approved':
                reconciliation.line_id._refresh_package_reconciliation_earnings()
        return True

    def action_approve(self):
        return self._restaurant_decide('approved')

    def action_open_reject_wizard(self):
        self.ensure_one()
        if not self._user_can_manage_restaurant(self.env.user):
            raise AccessError(
                _('Yalnızca ilgili restoranın yetkilisi bu mutabakatı reddedebilir.')
            )
        if self.state != 'pending':
            raise UserError(_('Bu paket mutabakatı daha önce sonuçlandırılmış.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Paket Beyanını Reddet'),
            'res_model': 'slots.package.reconciliation.reject.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'slots.view_package_reconciliation_reject_wizard_form'
            ).id,
            'target': 'new',
            'context': {'default_reconciliation_id': self.id},
        }

    def action_reject(self, rejection_reason=None):
        return self._restaurant_decide('rejected', rejection_reason)

    def action_admin_accept_rejected(self):
        now = fields.Datetime.now()
        for reconciliation in self:
            if not reconciliation.line_id._is_package_reconciliation_admin():
                raise AccessError(
                    _('Reddedilen mutabakatı yalnızca yöneticiler kabul edebilir.')
                )
            if reconciliation.state != 'rejected':
                raise UserError(_('Yalnızca reddedilmiş bir mutabakat geri alınabilir.'))
            reconciliation.line_id.sudo().with_context(
                package_reconciliation_write=True
            ).write({
                'paket_mutabakat_durumu': 'approved',
                'paket_mutabakat_karar_zamani': now,
                'paket_mutabakat_karar_user_id': self.env.user.id,
            })
            reconciliation.line_id._refresh_package_reconciliation_earnings()
        return True

    @api.model
    def _cron_auto_approve(self):
        now = fields.Datetime.now()
        pending_reconciliations = self.sudo().search([('state', '=', 'pending')])
        reconciliations = self.sudo().browse()
        for reconciliation in pending_reconciliations:
            effective_deadline = (
                reconciliation.submitted_at
                + timedelta(hours=PACKAGE_RECONCILIATION_APPROVAL_HOURS)
                if reconciliation.submitted_at
                else reconciliation.approval_deadline
            )
            if (
                effective_deadline
                and reconciliation.approval_deadline != effective_deadline
            ):
                reconciliation.line_id.with_context(
                    package_reconciliation_write=True
                ).write({'paket_mutabakat_son_tarih': effective_deadline})
            if effective_deadline and effective_deadline <= now:
                reconciliations |= reconciliation
        if reconciliations:
            reconciliations.mapped('line_id').with_context(
                package_reconciliation_write=True
            ).write({
                'paket_mutabakat_durumu': 'auto_approved',
                'paket_mutabakat_karar_zamani': now,
                'paket_mutabakat_karar_user_id': False,
            })
            reconciliations.mapped(
                'line_id'
            )._refresh_package_reconciliation_earnings()
        return len(reconciliations)


class SlotsPackageReconciliationRejectWizard(models.TransientModel):
    _name = 'slots.package.reconciliation.reject.wizard'
    _description = 'Paket Mutabakatı Ret Nedeni'

    reconciliation_id = fields.Many2one(
        'slots.package.reconciliation',
        string='Paket Mutabakatı',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    rejection_reason = fields.Text(string='Ret Nedeni', required=True)

    def action_confirm_rejection(self):
        self.ensure_one()
        reason = (self.rejection_reason or '').strip()
        if not reason:
            raise ValidationError(_('Ret nedeni yazılması zorunludur.'))
        self.reconciliation_id.action_reject(reason)
        return {'type': 'ir.actions.act_window_close'}


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        refresh_courier_guarantee = 'garanti_paket_sayisi' in vals
        result = super().write(vals)
        if refresh_courier_guarantee and self:
            lines = self.env['skurye.profile.lines'].sudo().search([
                ('paket_mutabakat_restoran_id', 'in', self.ids),
                ('kurye_paket_beyani_yapildi', '=', True),
            ])
            if lines:
                lines._refresh_package_reconciliation_earnings()
        return result

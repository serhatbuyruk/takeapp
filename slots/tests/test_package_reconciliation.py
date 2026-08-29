from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'package_reconciliation')
class TestPackageReconciliation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tested_models = cls.env['ir.model'].search([
            (
                'model',
                'in',
                ['slots.profile', 'skurye.profile.lines', 'res.partner'],
            )
        ])
        cls.env['base.automation'].search([
            ('model_id', 'in', tested_models.ids),
            ('active', '=', True),
        ]).write({'active': False})
        cls.now = fields.Datetime.now()
        cls.restaurant = cls.env['res.partner'].create({
            'name': 'Mutabakat Test Restoranı',
            'user_role': 'magaza',
            'slot_tipi': 'sabit',
            'currency_id': cls.env.company.currency_id.id,
        })
        cls.courier = cls.env['res.partner'].create({
            'name': 'Mutabakat Test Kuryesi',
            'user_role': 'kurye',
            'currency_id': cls.env.company.currency_id.id,
        })
        cls.other_courier = cls.env['res.partner'].create({
            'name': 'Diğer Test Kuryesi',
            'user_role': 'kurye',
            'currency_id': cls.env.company.currency_id.id,
        })
        cls.restaurant_user = cls.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Restoran Yetkilisi',
            'login': 'package.restaurant@test.invalid',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })
        cls.restaurant.yetkili_users = [(4, cls.restaurant_user.id)]
        cls.other_restaurant_user = cls.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Başka Restoran Yetkilisi',
            'login': 'other.package.restaurant@test.invalid',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })

    def _create_worked_line(
        self,
        slot_type='sabit',
        courier=None,
        started=True,
        ended=True,
    ):
        start = self.now - timedelta(hours=3)
        end = self.now - timedelta(hours=1) if ended else self.now + timedelta(hours=1)
        slot = self.env['slots.profile'].create({
            'name': 'Paket Mutabakat Test Slotu',
            'slot_tipi': slot_type,
            'magazalar': [(6, 0, self.restaurant.ids)],
            'start_date': start,
            'end_date': end,
            'active_status': ended is False,
            'currency_id': self.env.company.currency_id.id,
        })
        line = self.env['skurye.profile.lines'].create({
            'name': 'Paket Mutabakat Test Satırı',
            'sequence': slot.id,
            'partner_id': (courier or self.courier).id,
            'start_date': start + timedelta(minutes=2) if started else False,
            'end_date': end if ended and started else False,
            'active': not ended,
            'kurye_active': not ended,
        })
        return slot, line

    def _submit(self, line, count=7):
        return line.submit_courier_package_count(self.courier, count)

    def test_new_fixed_slot_line_requires_reconciliation(self):
        slot, line = self._create_worked_line()
        self.assertTrue(line.paket_mutabakat_gerekli)
        self.assertEqual(line.paket_mutabakat_slot_id, slot)
        self.assertEqual(line.paket_mutabakat_restoran_id, self.restaurant)

    def test_region_slot_line_does_not_require_reconciliation(self):
        _slot, line = self._create_worked_line(slot_type='bolge')
        self.assertFalse(line.paket_mutabakat_gerekli)
        self.assertFalse(
            self.env['skurye.profile.lines'].get_pending_courier_declaration(
                self.courier
            )
        )

    def test_pending_declaration_only_after_slot_end(self):
        _slot, future_line = self._create_worked_line(ended=False)
        self.assertFalse(
            self.env['skurye.profile.lines'].get_pending_courier_declaration(
                self.courier
            )
        )
        with self.assertRaisesRegex(UserError, 'süresi bitmeden'):
            self._submit(future_line)
        future_line.write({
            'kurye_start_date': fields.Datetime.now() - timedelta(hours=1),
            'kurye_end_date': fields.Datetime.now() - timedelta(seconds=1),
        })
        self.assertEqual(
            self.env[
                'skurye.profile.lines'
            ].get_pending_courier_declaration(self.courier),
            future_line,
        )

    def test_unworked_slot_does_not_block_or_accept_declaration(self):
        _slot, line = self._create_worked_line(started=False)
        self.assertFalse(
            self.env['skurye.profile.lines'].get_pending_courier_declaration(
                self.courier
            )
        )
        with self.assertRaisesRegex(UserError, 'Çalışılmamış'):
            self._submit(line)

    def test_courier_can_submit_zero_packages(self):
        _slot, line = self._create_worked_line()
        reconciliation = self._submit(line, 0)
        self.assertTrue(line.kurye_paket_beyani_yapildi)
        self.assertEqual(line.kurye_beyan_paket_sayisi, 0)
        self.assertEqual(line.paket_mutabakat_durumu, 'pending')
        self.assertEqual(reconciliation.line_id, line)
        self.assertAlmostEqual(
            (
                line.paket_mutabakat_son_tarih
                - line.kurye_paket_beyan_zamani
            ).total_seconds(),
            24 * 3600,
            delta=1,
        )

    def test_courier_guaranteed_packages_are_used_for_earnings(self):
        self.restaurant.write({
            'paket_basi_ucret': 3.0,
            'garanti_paket_sayisi': 10,
        })
        slot, line = self._create_worked_line()
        slot.slot_promosyon_ucret = 2.0

        self._submit(line, 4)

        self.assertEqual(line.kurye_beyan_paket_sayisi, 4)
        self.assertEqual(line.mutabakat_hesaplanan_paket_sayisi, 10)
        self.assertEqual(line.slot_paket_sayisi, 10)
        self.assertEqual(line.mutabakat_paket_kazanci, 30.0)
        self.assertEqual(line.mutabakat_promosyon_kazanci, 20.0)

    def test_report_above_courier_guarantee_uses_reported_count(self):
        self.restaurant.write({
            'paket_basi_ucret': 3.0,
            'garanti_paket_sayisi': 10,
        })
        _slot, line = self._create_worked_line()

        self._submit(line, 12)

        self.assertEqual(line.kurye_beyan_paket_sayisi, 12)
        self.assertEqual(line.mutabakat_hesaplanan_paket_sayisi, 12)
        self.assertEqual(line.mutabakat_paket_kazanci, 36.0)

    def test_changing_courier_guarantee_refreshes_submitted_earnings(self):
        self.restaurant.paket_basi_ucret = 2.0
        _slot, line = self._create_worked_line()
        self._submit(line, 5)

        self.restaurant.garanti_paket_sayisi = 8

        self.assertEqual(line.mutabakat_hesaplanan_paket_sayisi, 8)
        self.assertEqual(line.mutabakat_paket_kazanci, 16.0)

    def test_courier_cannot_submit_fraction_or_negative_count(self):
        _slot, line = self._create_worked_line()
        with self.assertRaises(ValidationError):
            self._submit(line, '2.5')
        with self.assertRaises(ValidationError):
            self._submit(line, -1)

    def test_courier_cannot_submit_for_another_courier(self):
        _slot, line = self._create_worked_line(courier=self.other_courier)
        with self.assertRaises(AccessError):
            self._submit(line, 4)

    def test_courier_cannot_change_submitted_count(self):
        _slot, line = self._create_worked_line()
        self._submit(line, 5)
        with self.assertRaisesRegex(UserError, 'daha önce'):
            self._submit(line, 8)
        with self.assertRaises(AccessError):
            line.with_user(self.restaurant_user).write({
                'kurye_beyan_paket_sayisi': 9,
            })
        self.assertEqual(line.kurye_beyan_paket_sayisi, 5)

    def test_authorized_restaurant_can_approve(self):
        _slot, line = self._create_worked_line()
        reconciliation = self._submit(line, 6)
        reconciliation.with_user(self.restaurant_user).action_approve()
        self.assertEqual(line.paket_mutabakat_durumu, 'approved')
        self.assertEqual(
            line.paket_mutabakat_karar_user_id,
            self.restaurant_user,
        )

    def test_authorized_restaurant_can_reject_but_not_edit_count(self):
        _slot, line = self._create_worked_line()
        reconciliation = self._submit(line, 6)
        with self.assertRaises(AccessError):
            reconciliation.with_user(self.restaurant_user).write({
                'courier_reported_count': 10,
            })
        reconciliation.with_user(self.restaurant_user).action_reject(
            'Kurye beyanı restoran kayıtlarıyla uyuşmuyor.'
        )
        self.assertEqual(line.paket_mutabakat_durumu, 'rejected')
        self.assertEqual(
            line.paket_mutabakat_red_nedeni,
            'Kurye beyanı restoran kayıtlarıyla uyuşmuyor.',
        )
        with self.assertRaisesRegex(UserError, 'sonuçlandırılmış'):
            reconciliation.with_user(self.restaurant_user).action_approve()

    def test_restaurant_rejection_requires_reason_and_admin_can_accept(self):
        _slot, line = self._create_worked_line()
        reconciliation = self._submit(line, 6)

        with self.assertRaisesRegex(ValidationError, 'Ret nedeni'):
            reconciliation.with_user(self.restaurant_user).action_reject('   ')

        reconciliation.with_user(self.restaurant_user).action_reject(
            'Restoran sayımı farklı.'
        )
        reconciliation.action_admin_accept_rejected()

        self.assertEqual(line.paket_mutabakat_durumu, 'approved')
        self.assertEqual(line.paket_mutabakat_red_nedeni, 'Restoran sayımı farklı.')

    def test_unrelated_restaurant_user_cannot_decide(self):
        _slot, line = self._create_worked_line()
        reconciliation = self._submit(line, 3)
        with self.assertRaises(AccessError):
            reconciliation.with_user(
                self.other_restaurant_user
            ).action_approve()
        self.assertEqual(line.paket_mutabakat_durumu, 'pending')

    def test_restaurant_decision_after_deadline_is_auto_approved(self):
        _slot, line = self._create_worked_line()
        reconciliation = self._submit(line, 8)
        submitted_at = self.now - timedelta(hours=25)
        line.with_context(package_reconciliation_write=True).write({
            'kurye_paket_beyan_zamani': submitted_at,
            'paket_mutabakat_son_tarih': submitted_at + timedelta(hours=24),
        })
        reconciliation.with_user(self.restaurant_user).action_reject('Geçersiz beyan')
        self.assertEqual(line.paket_mutabakat_durumu, 'auto_approved')
        self.assertFalse(line.paket_mutabakat_karar_user_id)

    def test_cron_auto_approves_only_expired_pending_records(self):
        _slot, expired_line = self._create_worked_line()
        expired_reconciliation = self._submit(expired_line, 4)
        submitted_at = self.now - timedelta(hours=25)
        expired_line.with_context(package_reconciliation_write=True).write({
            'kurye_paket_beyan_zamani': submitted_at,
            'paket_mutabakat_son_tarih': submitted_at + timedelta(hours=24),
        })

        _slot, future_line = self._create_worked_line()
        self._submit(future_line, 5)
        processed = self.env[
            'slots.package.reconciliation'
        ]._cron_auto_approve()

        self.assertGreaterEqual(processed, 1)
        self.assertEqual(
            expired_reconciliation.state,
            'auto_approved',
        )
        self.assertEqual(future_line.paket_mutabakat_durumu, 'pending')

    def test_cron_applies_24_hour_rule_to_existing_pending_records(self):
        _slot, line = self._create_worked_line()
        reconciliation = self._submit(line, 4)
        submitted_at = self.now - timedelta(hours=25)
        line.with_context(package_reconciliation_write=True).write({
            'kurye_paket_beyan_zamani': submitted_at,
            'paket_mutabakat_son_tarih': self.now + timedelta(hours=23),
        })

        self.env['slots.package.reconciliation']._cron_auto_approve()

        self.assertEqual(reconciliation.state, 'auto_approved')
        self.assertEqual(
            line.paket_mutabakat_son_tarih,
            submitted_at + timedelta(hours=24),
        )

    def test_slots_admin_can_revise_submitted_count(self):
        _slot, line = self._create_worked_line()
        reconciliation = self._submit(line, 2)
        admin_user = self.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Slot Mutabakat Yöneticisi',
            'login': 'package.admin@test.invalid',
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('slots.slots_group_admin').id,
            ])],
        })
        reconciliation.with_user(admin_user).write({
            'courier_reported_count': 11,
        })
        self.assertEqual(line.kurye_beyan_paket_sayisi, 11)
        self.assertEqual(line.paket_sayisi_admin_revize_user_id, admin_user)

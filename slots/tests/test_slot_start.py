from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'courier_slot_start')
class TestCourierSlotStart(TransactionCase):

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
        cls.currency = cls.env.company.currency_id

    def setUp(self):
        super().setUp()
        self.now = fields.Datetime.now()
        self.restaurant = self.env['res.partner'].create({
            'name': 'Slot Başlatma Test Restoranı',
            'user_role': 'magaza',
            'slot_tipi': 'sabit',
            'lat': 36.884100,
            'lng': 30.705600,
            'sabit_slot_baslatma_yaricapi_m': 500,
            'currency_id': self.currency.id,
        })
        self.courier = self.env['res.partner'].create({
            'name': 'Slot Başlatma Test Kuryesi',
            'user_role': 'kurye',
            'kurye_durumu': 'mesgul',
            'currency_id': self.currency.id,
        })

    def _create_slot(self, slot_type='sabit', line_values=None):
        slot = self.env['slots.profile'].create({
            'name': 'Slot Başlatma Test Slotu',
            'slot_tipi': slot_type,
            'magazalar': [(6, 0, self.restaurant.ids)],
            'start_date': self.now - timedelta(hours=1),
            'end_date': self.now + timedelta(hours=4),
            'active_status': True,
            'lat': self.restaurant.lat,
            'lng': self.restaurant.lng,
            'currency_id': self.currency.id,
        })
        values = {
            'name': 'Test Kurye Satırı',
            'sequence': slot.id,
            'partner_id': self.courier.id,
            'active': True,
            'kurye_active': True,
        }
        values.update(line_values or {})
        line = self.env['skurye.profile.lines'].create(values)
        slot.invalidate_recordset(['skurye_profile_lines'])
        return slot, line

    def test_courier_can_start_inside_restaurant_radius(self):
        slot, line = self._create_slot()
        result = slot.start_courier_slot(
            self.courier,
            self.restaurant.lat + 0.001,
            self.restaurant.lng,
            8,
        )
        self.assertEqual(result['status'], 'success')
        self.assertLess(result['distance'], 500)
        self.assertTrue(line.start_date)
        self.assertTrue(line.kurye_yoklamasi)
        self.assertEqual(self.courier.kurye_durumu, 'musait')
        self.assertAlmostEqual(
            self.courier.lat,
            self.restaurant.lat + 0.001,
            places=6,
        )

    def test_courier_cannot_start_outside_restaurant_radius(self):
        slot, line = self._create_slot()
        with self.assertRaisesRegex(UserError, '500 metre'):
            slot.start_courier_slot(
                self.courier,
                self.restaurant.lat + 0.009,
                self.restaurant.lng,
                8,
            )
        self.assertFalse(line.start_date)
        self.assertAlmostEqual(
            self.courier.lat,
            self.restaurant.lat + 0.009,
            places=6,
        )

    def test_restaurant_can_increase_fixed_start_radius(self):
        self.restaurant.sabit_slot_baslatma_yaricapi_m = 1500
        slot, line = self._create_slot()
        slot.start_courier_slot(
            self.courier,
            self.restaurant.lat + 0.009,
            self.restaurant.lng,
            8,
        )
        self.assertTrue(line.start_date)

    def test_region_slot_keeps_existing_two_kilometre_radius(self):
        slot, line = self._create_slot(slot_type='bolge')
        result = slot.start_courier_slot(
            self.courier,
            self.restaurant.lat + 0.009,
            self.restaurant.lng,
            8,
        )
        self.assertEqual(result['allowed_radius'], 2000)
        self.assertTrue(line.start_date)

    def test_courier_specific_future_start_is_rejected(self):
        slot, line = self._create_slot(line_values={
            'kurye_start_date': self.now + timedelta(hours=1),
            'kurye_end_date': self.now + timedelta(hours=3),
        })
        with self.assertRaisesRegex(UserError, 'henüz başlamadı'):
            slot.start_courier_slot(
                self.courier,
                self.restaurant.lat,
                self.restaurant.lng,
            )
        self.assertFalse(line.start_date)

    def test_inactive_courier_line_is_rejected(self):
        slot, line = self._create_slot(line_values={'kurye_active': False})
        with self.assertRaisesRegex(UserError, 'aktiflik'):
            slot.start_courier_slot(
                self.courier,
                self.restaurant.lat,
                self.restaurant.lng,
            )
        self.assertFalse(line.start_date)

    def test_repeated_start_is_idempotent(self):
        slot, line = self._create_slot()
        slot.start_courier_slot(
            self.courier,
            self.restaurant.lat,
            self.restaurant.lng,
        )
        first_start = line.start_date
        slot.start_courier_slot(
            self.courier,
            self.restaurant.lat,
            self.restaurant.lng,
        )
        self.assertEqual(line.start_date, first_start)

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestRestaurantKmFee(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.restaurant = cls.env['res.partner'].search(
            [('user_role', '=', 'magaza')],
            limit=1,
        )
        if not cls.restaurant:
            cls.restaurant = cls.env.ref('base.main_partner')
        cls.range_model = cls.env['corders.restoran.km.ucret.araligi']
        cls.platform_range_model = cls.env[
            'corders.restoran.platform.km.ucret.araligi'
        ]

    def _create_range(self, start, end, fee):
        return self.range_model.create({
            'partner_id': self.restaurant.id,
            'baslangic_km': start,
            'bitis_km': end,
            'ucret': fee,
        })

    def _create_platform_range(self, start, end, fee):
        return self.platform_range_model.create({
            'partner_id': self.restaurant.id,
            'baslangic_km': start,
            'bitis_km': end,
            'ucret': fee,
        })

    def test_no_ranges_returns_zero(self):
        self.assertEqual(self.restaurant.get_distance_fee(3500), 0.0)

    def test_matching_ranges_return_flat_fee(self):
        self._create_range(0, 5, 5)
        self._create_range(5, 10, 7)
        self.assertEqual(self.restaurant.get_distance_fee(2500), 5.0)
        self.assertEqual(self.restaurant.get_distance_fee(7500), 7.0)

    def test_boundary_belongs_to_next_range(self):
        self._create_range(0, 5, 5)
        self._create_range(5, 10, 7)
        self.assertEqual(self.restaurant.get_distance_fee(5000), 7.0)

    def test_unconfigured_gap_returns_zero(self):
        self._create_range(0, 5, 5)
        self._create_range(7, 10, 9)
        self.assertEqual(self.restaurant.get_distance_fee(6000), 0.0)

    def test_negative_distance_is_treated_as_zero(self):
        self._create_range(0, 5, 5)
        self.assertEqual(self.restaurant.get_distance_fee(-1000), 5.0)

    def test_overlapping_ranges_are_rejected(self):
        self._create_range(0, 5, 5)
        with self.assertRaises(ValidationError):
            self._create_range(4, 8, 7)

    def test_invalid_range_is_rejected(self):
        with self.assertRaises(ValidationError):
            self._create_range(5, 5, 7)

    def test_negative_range_start_is_rejected(self):
        with self.assertRaises(ValidationError):
            self._create_range(-1, 5, 7)

    def test_platform_ranges_are_independent_from_courier_ranges(self):
        self._create_range(0, 5, 5)
        self._create_platform_range(0, 5, 12)
        self.assertEqual(self.restaurant.get_distance_fee(2500), 5.0)
        self.assertEqual(self.restaurant.get_platform_distance_fee(2500), 12.0)

    def test_platform_range_gap_and_missing_config_return_zero(self):
        self.assertEqual(self.restaurant.get_platform_distance_fee(2500), 0.0)
        self._create_platform_range(5, 10, 12)
        self.assertEqual(self.restaurant.get_platform_distance_fee(2500), 0.0)

    def test_platform_range_boundary_belongs_to_next_range(self):
        self._create_platform_range(0, 5, 8)
        self._create_platform_range(5, 10, 12)
        self.assertEqual(self.restaurant.get_platform_distance_fee(5000), 12.0)

    def test_overlapping_platform_ranges_are_rejected(self):
        self._create_platform_range(0, 5, 8)
        with self.assertRaises(ValidationError):
            self._create_platform_range(4, 8, 12)

    def test_fixed_slot_start_radius_defaults_to_500_metres(self):
        restaurant = self.env['res.partner'].new({'user_role': 'magaza'})
        self.assertEqual(restaurant.sabit_slot_baslatma_yaricapi_m, 500)

    def test_fixed_slot_start_radius_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.restaurant.write({'sabit_slot_baslatma_yaricapi_m': 0})

    def test_guaranteed_package_counts_default_to_zero(self):
        restaurant = self.env['res.partner'].new({'user_role': 'magaza'})
        self.assertEqual(restaurant.garanti_paket_sayisi, 0)
        self.assertEqual(restaurant.restoran_garanti_paket_sayisi, 0)

    def test_guaranteed_package_counts_cannot_be_negative(self):
        with self.assertRaises(ValidationError):
            self.restaurant.garanti_paket_sayisi = -1
        with self.assertRaises(ValidationError):
            self.restaurant.restoran_garanti_paket_sayisi = -1

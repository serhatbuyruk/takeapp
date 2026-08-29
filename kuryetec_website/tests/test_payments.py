from odoo import fields
from odoo.tests import HttpCase, new_test_user, tagged


@tagged('post_install', '-at_install', 'kuryetec_payments')
class TestCourierPaymentsPage(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tested_models = cls.env['ir.model'].search([
            (
                'model',
                'in',
                ['corders.profile', 'skurye.profile.lines', 'res.partner'],
            )
        ])
        cls.env['base.automation'].search([
            ('model_id', 'in', tested_models.ids),
            ('active', '=', True),
        ]).write({'active': False})
        cls.payments_page = cls.env.ref(
            'kuryetec_website.website_page_100'
        )
        # Hesaplama regresyon testleri sayfayı kontrollü olarak açar.
        cls.payments_page.is_published = True

        cls.user = new_test_user(
            cls.env,
            login='payment-courier',
            password='payment-courier',
            groups='base.group_user',
        )
        cls.user.partner_id.write({
            'name': 'Ödeme Test Kuryesi',
            'user_role': 'kurye',
        })
        cls.other_courier = cls.env['res.partner'].create({
            'name': 'Başka Ödeme Kuryesi',
            'user_role': 'kurye',
        })
        cls.restaurant = cls.env['res.partner'].create({
            'name': 'Ödeme Test Restoranı',
            'user_role': 'magaza',
        })
        now = fields.Datetime.now()

        def create_order(number, courier, payment_status):
            return cls.env['corders.profile'].create({
                'siparis_no': number,
                'magaza': cls.restaurant.id,
                'kurye': courier.id,
                'musteri_adi': 'Ödeme Test Müşterisi',
                'adres': 'Ödeme test adresi',
                'platform': 'telefon',
                'odeme_yontemi': 'online_odendi',
                'kurye_odeme_alma_yontemi': 'online_odendi',
                'siparis_tarihi': now,
                'siparis_durumu_zamani': now,
                'paket_bitis_tarihi': now,
                'siparis_durumu': 'teslim_edildi',
                'kurye_odeme_durumu': payment_status,
                'sale_price': 12.0,
                'baz_price': 8.0,
                'toplam_km_price': 4.0,
            })

        create_order('OWN-PAID-PAYMENT', cls.user.partner_id, 'paid')
        create_order('OWN-PENDING-PAYMENT', cls.user.partner_id, 'not_paid')
        create_order('OTHER-COURIER-PAYMENT', cls.other_courier, 'paid')

    def setUp(self):
        super().setUp()
        self.authenticate('payment-courier', 'payment-courier')

    def test_page_ignores_foreign_partner_parameter(self):
        response = self.url_open(
            '/odemeler?range=week:0&partner_id=%s'
            % self.other_courier.id
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('OWN-PAID-PAYMENT', response.text)
        self.assertIn('OWN-PENDING-PAYMENT', response.text)
        self.assertNotIn('OTHER-COURIER-PAYMENT', response.text)

    def test_paid_filter_only_lists_paid_earnings(self):
        response = self.url_open(
            '/odemeler?range=week:0&payment_status=paid'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('OWN-PAID-PAYMENT', response.text)
        self.assertNotIn('OWN-PENDING-PAYMENT', response.text)

    def test_pending_filter_only_lists_pending_earnings(self):
        response = self.url_open(
            '/odemeler?range=week:0&payment_status=not_paid'
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('OWN-PAID-PAYMENT', response.text)
        self.assertIn('OWN-PENDING-PAYMENT', response.text)

    def test_invalid_filter_values_fall_back_safely(self):
        response = self.url_open(
            '/odemeler?range=invalid&payment_status=invalid'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('OWN-PAID-PAYMENT', response.text)
        self.assertIn('OWN-PENDING-PAYMENT', response.text)

    def test_unpublished_page_is_not_directly_accessible(self):
        self.payments_page.is_published = False
        try:
            response = self.url_open('/odemeler')
            self.assertEqual(response.status_code, 404)
        finally:
            self.payments_page.is_published = True

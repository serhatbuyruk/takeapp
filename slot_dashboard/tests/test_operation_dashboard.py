from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'slot_dashboard')
class TestOperationDashboard(TransactionCase):

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
        cls.today = fields.Date.context_today(cls.env['slots.profile'])
        cls.currency = cls.env.company.currency_id
        cls.restaurant = cls.env['res.partner'].create({
            'name': 'Dashboard Test Restoranı',
            'user_role': 'magaza',
            'slot_tipi': 'sabit',
            'currency_id': cls.currency.id,
        })
        cls.admin_user = cls.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Dashboard Operasyon Yöneticisi',
            'login': 'operation.dashboard.admin@test.invalid',
            'tz': 'UTC',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('slots.slots_group_admin').id,
            ])],
        })
        cls.regular_user = cls.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Dashboard Yetkisiz Kullanıcı',
            'login': 'operation.dashboard.regular@test.invalid',
            'tz': 'UTC',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })
        cls.couriers = cls.env['res.partner']
        for index in range(4):
            cls.couriers |= cls.env['res.partner'].create({
                'name': 'Dashboard Test Kuryesi %s' % (index + 1),
                'user_role': 'kurye',
                'currency_id': cls.currency.id,
            })

    def setUp(self):
        super().setUp()
        self.baseline_today = self._dashboard(
            fields.Date.to_string(self.today)
        )

    def _metric_delta(self, data, metric, baseline=None):
        baseline = baseline or self.baseline_today
        return data['metrics'][metric] - baseline['metrics'][metric]

    def _create_slot(self, name, start, end, restaurant=None):
        return self.env['slots.profile'].create({
            'name': name,
            'slot_tipi': 'sabit',
            'magazalar': [(6, 0, (restaurant or self.restaurant).ids)],
            'start_date': start,
            'end_date': end,
            'active_status': True,
            'currency_id': self.currency.id,
        })

    def _create_line(
        self,
        slot,
        courier,
        planned_start,
        planned_end,
        actual_start=False,
        actual_end=False,
        late=False,
    ):
        return self.env['skurye.profile.lines'].create({
            'name': '%s vardiyası' % courier.name,
            'sequence': slot.id,
            'partner_id': courier.id,
            'kurye_start_date': planned_start,
            'kurye_end_date': planned_end,
            'start_date': actual_start,
            'end_date': actual_end,
            'gecikme_durumu': late,
            'gecikme_dakikasi': 15 if late else 0,
            'active': not bool(actual_end),
            'kurye_active': not bool(actual_end),
        })

    def _prepare_today_scenario(self):
        slot = self._create_slot(
            'Bugün Operasyon Test Slotu',
            self.now - timedelta(hours=2),
            self.now + timedelta(hours=3),
        )
        self._create_line(
            slot,
            self.couriers[0],
            self.now - timedelta(minutes=60),
            self.now + timedelta(hours=2),
            actual_start=self.now - timedelta(minutes=58),
        )
        self._create_line(
            slot,
            self.couriers[1],
            self.now - timedelta(minutes=45),
            self.now + timedelta(hours=2),
            actual_start=self.now - timedelta(minutes=30),
            late=True,
        )
        self._create_line(
            slot,
            self.couriers[2],
            self.now - timedelta(minutes=30),
            self.now + timedelta(hours=2),
        )
        self._create_line(
            slot,
            self.couriers[3],
            self.now + timedelta(minutes=45),
            self.now + timedelta(hours=2),
        )
        return slot

    def _dashboard(self, date=None, user=None):
        return self.env['slots.profile'].with_user(
            user or self.admin_user
        ).get_operation_dashboard_data(date)

    def test_today_metrics_and_health(self):
        self._prepare_today_scenario()
        data = self._dashboard(fields.Date.to_string(self.today))
        metrics = data['metrics']

        self.assertEqual(self._metric_delta(data, 'planned_slots'), 1)
        self.assertEqual(self._metric_delta(data, 'planned_shifts'), 4)
        self.assertEqual(self._metric_delta(data, 'planned_couriers'), 4)
        self.assertEqual(self._metric_delta(data, 'due_shifts'), 3)
        self.assertEqual(self._metric_delta(data, 'arrived'), 2)
        self.assertEqual(self._metric_delta(data, 'arrived_couriers'), 2)
        self.assertEqual(self._metric_delta(data, 'on_time'), 1)
        self.assertEqual(self._metric_delta(data, 'late'), 1)
        self.assertEqual(self._metric_delta(data, 'missing'), 1)
        self.assertEqual(self._metric_delta(data, 'upcoming'), 1)
        self.assertEqual(self._metric_delta(data, 'working_now'), 2)
        self.assertEqual(self._metric_delta(data, 'courier_planned'), 4)
        self.assertEqual(self._metric_delta(data, 'courier_due'), 3)
        self.assertEqual(self._metric_delta(data, 'courier_on_time'), 1)
        self.assertEqual(self._metric_delta(data, 'courier_late'), 1)
        self.assertEqual(self._metric_delta(data, 'courier_missing'), 1)
        self.assertEqual(self._metric_delta(data, 'courier_upcoming'), 1)
        self.assertEqual(data['health']['status'], 'danger')

        restaurant = next(
            item for item in data['restaurants']
            if item['name'] == self.restaurant.name
        )
        self.assertEqual(restaurant['planned'], 4)
        self.assertEqual(restaurant['due'], 3)
        self.assertEqual(restaurant['arrived'], 2)
        self.assertEqual(restaurant['on_time'], 1)
        self.assertEqual(restaurant['late'], 1)
        self.assertEqual(restaurant['missing'], 1)
        self.assertEqual(restaurant['upcoming'], 1)
        self.assertEqual(restaurant['entry_rate'], 67)

    def test_courier_with_multiple_shifts_is_counted_once(self):
        slot = self._create_slot(
            'Tekil Kurye Sayımı Test Slotu',
            self.now - timedelta(hours=2),
            self.now + timedelta(hours=2),
        )
        self._create_line(
            slot,
            self.couriers[0],
            self.now - timedelta(minutes=50),
            self.now + timedelta(minutes=10),
            actual_start=self.now - timedelta(minutes=49),
        )
        self._create_line(
            slot,
            self.couriers[0],
            self.now - timedelta(minutes=20),
            self.now + timedelta(hours=1),
        )

        data = self._dashboard()
        self.assertEqual(self._metric_delta(data, 'planned_shifts'), 2)
        self.assertEqual(self._metric_delta(data, 'courier_planned'), 1)
        self.assertEqual(self._metric_delta(data, 'courier_due'), 1)
        self.assertEqual(self._metric_delta(data, 'courier_missing'), 1)
        self.assertEqual(self._metric_delta(data, 'courier_on_time'), 0)
        self.assertEqual(self._metric_delta(data, 'courier_late'), 0)

        rows = [
            row for row in data['rows']
            if row['slot_name'] == 'Tekil Kurye Sayımı Test Slotu'
        ]
        self.assertEqual({row['courier_status'] for row in rows}, {'missing'})

    def test_selected_restaurants_limit_dashboard_scope(self):
        selected_slot = self._create_slot(
            'Dashboard Kapsamındaki Slot',
            self.now - timedelta(hours=1),
            self.now + timedelta(hours=1),
        )
        excluded_restaurant = self.env['res.partner'].create({
            'name': 'Dashboard Dışındaki Restoran',
            'user_role': 'magaza',
            'slot_tipi': 'sabit',
            'currency_id': self.currency.id,
        })
        excluded_slot = self._create_slot(
            'Dashboard Dışındaki Slot',
            self.now - timedelta(hours=1),
            self.now + timedelta(hours=1),
            restaurant=excluded_restaurant,
        )
        self._create_line(
            selected_slot,
            self.couriers[0],
            self.now - timedelta(minutes=30),
            self.now + timedelta(minutes=30),
            actual_start=self.now - timedelta(minutes=29),
        )
        self._create_line(
            excluded_slot,
            self.couriers[1],
            self.now - timedelta(minutes=30),
            self.now + timedelta(minutes=30),
            actual_start=self.now - timedelta(minutes=29),
        )

        self.restaurant.operation_dashboard_enabled = True
        data = self._dashboard()

        self.assertTrue(data['dashboard_scope_active'])
        self.assertEqual(data['dashboard_restaurant_count'], 1)
        self.assertEqual(data['metrics']['courier_compliance_rate'], 100)
        self.assertIn(
            'Dashboard Kapsamındaki Slot',
            {row['slot_name'] for row in data['rows']},
        )
        self.assertNotIn(
            'Dashboard Dışındaki Slot',
            {row['slot_name'] for row in data['rows']},
        )
    def test_attention_rows(self):
        self._prepare_today_scenario()
        data = self._dashboard()

        scenario_rows = [
            row for row in data['rows']
            if row['slot_name'] == 'Bugün Operasyon Test Slotu'
        ]
        self.assertEqual(
            {row['status'] for row in scenario_rows},
            {'working', 'late', 'missing', 'upcoming'},
        )

    def test_exact_ten_minutes_is_late_but_nine_minutes_is_on_time(self):
        slot = self._create_slot(
            'Gecikme Sınırı Test Slotu',
            self.now - timedelta(hours=1),
            self.now + timedelta(hours=1),
        )
        first_start = self.now - timedelta(minutes=30)
        second_start = self.now - timedelta(minutes=20)
        self._create_line(
            slot,
            self.couriers[0],
            first_start,
            self.now + timedelta(hours=1),
            actual_start=first_start + timedelta(minutes=10),
        )
        self._create_line(
            slot,
            self.couriers[1],
            second_start,
            self.now + timedelta(hours=1),
            actual_start=second_start + timedelta(minutes=9),
        )

        data = self._dashboard()
        self.assertEqual(self._metric_delta(data, 'late'), 1)
        self.assertEqual(self._metric_delta(data, 'on_time'), 1)

    def test_future_day_is_separate_and_not_due(self):
        tomorrow = self.today + timedelta(days=1)
        baseline_tomorrow = self._dashboard(fields.Date.to_string(tomorrow))
        tomorrow_start = self.now + timedelta(days=1)
        slot = self._create_slot(
            'Yarın Operasyon Test Slotu',
            tomorrow_start,
            tomorrow_start + timedelta(hours=4),
        )
        self._create_line(
            slot,
            self.couriers[0],
            tomorrow_start,
            tomorrow_start + timedelta(hours=4),
        )

        today_data = self._dashboard(fields.Date.to_string(self.today))
        tomorrow_data = self._dashboard(fields.Date.to_string(tomorrow))
        self.assertEqual(self._metric_delta(today_data, 'planned_shifts'), 0)
        self.assertEqual(
            self._metric_delta(
                tomorrow_data,
                'planned_shifts',
                baseline_tomorrow,
            ),
            1,
        )
        self.assertEqual(
            self._metric_delta(tomorrow_data, 'due_shifts', baseline_tomorrow),
            0,
        )
        self.assertEqual(
            self._metric_delta(tomorrow_data, 'upcoming', baseline_tomorrow),
            1,
        )

    def test_non_admin_cannot_read_dashboard_data(self):
        with self.assertRaises(AccessError):
            self._dashboard(user=self.regular_user)

    def test_dashboard_is_admin_home_action_and_main_app(self):
        action = self.env.ref('slot_dashboard.action_operation_dashboard')
        menu = self.env.ref('slot_dashboard.menu_slot_dashboard_root')
        system_admin = self.env.ref('base.user_admin')

        self.assertEqual(system_admin.action_id.id, action.id)
        self.assertFalse(menu.parent_id)
        self.assertEqual(menu.action.id, action.id)
        self.assertEqual(menu.sequence, 4)
        self.assertFalse(
            self.env.ref(
                'slots.menu_operation_dashboard',
                raise_if_not_found=False,
            )
        )

    def test_legacy_empty_courier_is_not_counted_as_a_planned_person(self):
        slot = self._create_slot(
            'Kuryesiz Operasyon Test Slotu',
            self.now - timedelta(hours=1),
            self.now + timedelta(hours=1),
        )
        placeholder = self.env['res.partner'].create({
            'name': 'Boş',
            'user_role': 'kurye',
            'email': 'boskurye.dashboard@test.invalid',
            'currency_id': self.currency.id,
        })
        self._create_line(
            slot,
            placeholder,
            self.now - timedelta(hours=1),
            self.now + timedelta(hours=1),
        )

        data = self._dashboard()
        self.assertEqual(self._metric_delta(data, 'planned_slots'), 1)
        self.assertEqual(self._metric_delta(data, 'planned_shifts'), 0)
        self.assertEqual(self._metric_delta(data, 'planned_couriers'), 0)
        self.assertEqual(self._metric_delta(data, 'unassigned_slots'), 1)
        self.assertEqual(data['health']['status'], 'danger')

    def test_get_shift_management_action_packages_opens_package_reconciliation_tree(self):
        action = self.env['slots.profile'].with_user(
            self.admin_user
        ).get_shift_management_action(
            selected_date=fields.Date.to_string(self.today),
            mode='packages',
        )
        self.assertEqual(action['res_model'], 'slots.package.reconciliation')
        self.assertEqual(action['name'], 'Kurye Paketleri')
        tree_view = self.env.ref('slots.view_package_reconciliation_tree')
        self.assertEqual(action['views'][0][0], tree_view.id)

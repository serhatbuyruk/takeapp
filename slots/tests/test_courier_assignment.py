from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "courier_assignment")
class TestCourierAssignmentEngine(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tested_models = cls.env["ir.model"].search(
            [
                (
                    "model",
                    "in",
                    [
                        "corders.profile",
                        "slots.profile",
                        "skurye.profile.lines",
                        "res.partner",
                        "ir.logging",
                    ],
                )
            ]
        )
        cls.env["base.automation"].search(
            [
                ("model_id", "in", tested_models.ids),
                ("active", "=", True),
            ]
        ).write({"active": False})
        cls.currency = cls.env.company.currency_id

    def setUp(self):
        super().setUp()
        self.now = fields.Datetime.now()
        self.restaurant = self._create_restaurant()

    def _create_restaurant(self, **overrides):
        values = {
            "name": "Test Restoran",
            "user_role": "magaza",
            "slot_tipi": "sabit",
            "lat": 36.884100,
            "lng": 30.705600,
            "akilli_paket_atama": True,
            "kurye_max_paket_sayisi": 3,
            "atanacak_paketler_arasi_yaricap_mesafesi": 1500,
            "currency_id": self.currency.id,
        }
        values.update(overrides)
        return self.env["res.partner"].create(values)

    def _create_courier(self, name, **overrides):
        values = {
            "name": name,
            "user_role": "kurye",
            "mobile": "5550000000",
            "kurye_durumu": "musait",
            "kurye_mola_durumu": False,
            "lat": 36.886100,
            "lng": 30.705600,
            "currency_id": self.currency.id,
        }
        values.update(overrides)
        return self.env["res.partner"].create(values)

    def _create_slot(
        self,
        couriers,
        slot_type=None,
        start_delta=-1,
        end_delta=8,
        line_overrides=None,
    ):
        slot_type = slot_type or self.restaurant.slot_tipi
        slot = self.env["slots.profile"].create(
            {
                "name": "Atama Test Slotu",
                "slot_tipi": slot_type,
                "magazalar": [(6, 0, self.restaurant.ids)],
                "start_date": self.now + timedelta(hours=start_delta),
                "end_date": self.now + timedelta(hours=end_delta),
                "active_status": True,
                "slot_acik_adresi": "Test adresi",
                "lat": self.restaurant.lat,
                "lng": self.restaurant.lng,
                "paket_basi_ucret": 1.0,
                "currency_id": self.currency.id,
            }
        )
        lines = {}
        for courier in couriers:
            values = {
                "name": "%s | %s" % (slot.name, courier.name),
                "sequence": slot.id,
                "partner_id": courier.id,
                "active": True,
                "kurye_active": True,
                "slot_paket_sayisi": 0,
            }
            values.update((line_overrides or {}).get(courier.id, {}))
            lines[courier.id] = self.env["skurye.profile.lines"].create(values)
        slot.invalidate_recordset(["skurye_profile_lines"])
        return slot, lines

    def _create_order(self, **overrides):
        values = {
            "siparis_no": "TEST-%s" % fields.Datetime.now().timestamp(),
            "magaza": self.restaurant.id,
            "musteri_adi": "Test Müşteri",
            "musteri_telefonu": "5551112233",
            "adres": "Test teslimat adresi",
            "platform": "telefon",
            "odeme_yontemi": "online_odendi",
            "siparis_tarihi": self.now,
            "siparis_durumu": "onay_bekliyor",
            "lat": 36.894100,
            "lng": 30.705600,
        }
        values.update(overrides)
        return self.env["corders.profile"].create(values)

    def _create_open_order(self, courier, hours_ago=1, **overrides):
        values = {
            "kurye": courier.id,
            "kurye_telefonu": courier.mobile,
            "siparis_tarihi": self.now - timedelta(hours=hours_ago),
            "siparis_durumu": "hazirlaniyor",
        }
        values.update(overrides)
        return self._create_order(**values)

    def test_01_nearest_available_courier_is_selected(self):
        nearest = self._create_courier(
            "Yakın Kurye",
            lat=36.885100,
        )
        farther = self._create_courier(
            "Uzak Kurye",
            lat=36.890100,
        )
        self._create_slot(nearest | farther)

        order = self._create_order()
        selected = order.auto_assign_courier()

        self.assertEqual(selected, nearest)
        self.assertEqual(order.kurye, nearest)
        self.assertEqual(order.otomatik_atama_senaryosu, "Sabit-A1")

    def test_02_courier_on_break_is_skipped(self):
        paused = self._create_courier(
            "Moladaki Kurye",
            lat=36.885100,
            kurye_mola_durumu=True,
        )
        available = self._create_courier(
            "Müsait Kurye",
            lat=36.886100,
        )
        self._create_slot(paused | available)

        selected = self._create_order().auto_assign_courier()

        self.assertEqual(selected, available)

    def test_03_busy_courier_is_skipped(self):
        busy = self._create_courier(
            "Meşgul Kurye",
            lat=36.885100,
            kurye_durumu="mesgul",
        )
        available = self._create_courier(
            "Müsait Kurye",
            lat=36.886100,
        )
        self._create_slot(busy | available)

        selected = self._create_order().auto_assign_courier()

        self.assertEqual(selected, available)

    def test_04_courier_without_location_is_skipped(self):
        missing_location = self._create_courier(
            "Konumsuz Kurye",
            lat=0,
            lng=0,
        )
        located = self._create_courier("Konumlu Kurye")
        self._create_slot(missing_location | located)

        selected = self._create_order().auto_assign_courier()

        self.assertEqual(selected, located)

    def test_05_full_courier_is_skipped_for_next_courier(self):
        full = self._create_courier(
            "Kapasitesi Dolu",
            lat=36.885100,
        )
        next_courier = self._create_courier(
            "Sıradaki Kurye",
            lat=36.886100,
        )
        self._create_slot(full | next_courier)
        for index in range(3):
            self._create_open_order(
                full,
                yon="0",
                siparis_no="FULL-%s" % index,
            )

        selected = self._create_order().auto_assign_courier()

        self.assertEqual(selected, next_courier)

    def test_06_restaurant_capacity_setting_is_respected(self):
        self.restaurant.kurye_max_paket_sayisi = 2
        first = self._create_courier("İki Paketli Kurye", lat=36.885100)
        second = self._create_courier("Boş Kurye", lat=36.886100)
        self._create_slot(first | second)
        self._create_open_order(first, yon="0", siparis_no="CAP-1")
        self._create_open_order(first, yon="0", siparis_no="CAP-2")

        selected = self._create_order().auto_assign_courier()

        self.assertEqual(selected, second)

    def test_07_order_older_than_24_hours_does_not_consume_capacity(self):
        courier = self._create_courier("Eski Siparişli Kurye")
        self._create_slot(courier)
        for index in range(4):
            self._create_open_order(
                courier,
                hours_ago=25,
                yon="0",
                siparis_no="STALE-%s" % index,
            )

        selected = self._create_order().auto_assign_courier()

        self.assertEqual(selected, courier)

    def test_08_recent_assignments_count_even_if_stored_counter_is_zero(self):
        self.restaurant.kurye_max_paket_sayisi = 1
        full = self._create_courier(
            "Sayaç Sıfır Ama Dolu",
            lat=36.885100,
            anlik_tasinan_paket_sayisi=0,
        )
        empty = self._create_courier(
            "Gerçekten Boş",
            lat=36.886100,
        )
        self._create_slot(full | empty)
        self._create_open_order(full, yon="0")

        selected = self._create_order().auto_assign_courier()

        self.assertEqual(selected, empty)

    def test_09_fixed_route_uses_closest_angle_not_farthest_angle(self):
        courier = self._create_courier(
            "Rotası Uygun Kurye",
            kurye_durumu="pakette",
            lat=36.886100,
        )
        self._create_slot(courier)
        self._create_open_order(courier, yon="90", siparis_no="ANGLE-90")
        self._create_open_order(courier, yon="10", siparis_no="ANGLE-10")

        order = self._create_order(lat=36.904100, lng=30.705600)
        selected = order.auto_assign_courier()

        self.assertEqual(selected, courier)
        self.assertEqual(order.otomatik_atama_senaryosu, "Sabit-A3")

    def test_10_fixed_incompatible_route_is_not_assigned_to_loaded_courier(self):
        courier = self._create_courier(
            "Ters Rotadaki Kurye",
            kurye_durumu="pakette",
            lat=36.886100,
        )
        self._create_slot(courier)
        self._create_open_order(courier, yon="180")

        selected = self._create_order(
            lat=36.904100,
            lng=30.705600,
        ).auto_assign_courier()

        self.assertFalse(selected)

    def test_11_region_route_uses_closest_existing_package(self):
        self.restaurant.write({"slot_tipi": "bolge"})
        courier = self._create_courier(
            "Bölge Rotası Uygun",
            kurye_durumu="pakette",
            lat=36.886100,
        )
        self._create_slot(courier, slot_type="bolge")
        self._create_open_order(
            courier,
            lat=36.895100,
            lng=30.705600,
            siparis_no="NEAR-PACKAGE",
        )
        self._create_open_order(
            courier,
            lat=36.950000,
            lng=30.705600,
            siparis_no="FAR-PACKAGE",
        )

        order = self._create_order(lat=36.894100, lng=30.705600)
        selected = order.auto_assign_courier()

        self.assertEqual(selected, courier)
        self.assertEqual(order.otomatik_atama_senaryosu, "Bölge-A3")

    def test_12_region_incompatible_route_is_not_assigned_to_loaded_courier(self):
        self.restaurant.write({"slot_tipi": "bolge"})
        courier = self._create_courier(
            "Bölge Rotası Uzak",
            kurye_durumu="pakette",
            lat=36.886100,
        )
        self._create_slot(courier, slot_type="bolge")
        self._create_open_order(
            courier,
            lat=36.950000,
            lng=30.705600,
        )

        selected = self._create_order(
            lat=36.894100,
            lng=30.705600,
        ).auto_assign_courier()

        self.assertFalse(selected)

    def test_13_safe_fallback_balances_by_slot_package_count(self):
        high_count = self._create_courier(
            "Çok Paket Taşıyan",
            lat=36.886100,
        )
        low_count = self._create_courier(
            "Az Paket Taşıyan",
            lat=36.890100,
        )
        _, lines = self._create_slot(
            high_count | low_count,
            line_overrides={
                high_count.id: {"slot_paket_sayisi": 8},
                low_count.id: {"slot_paket_sayisi": 1},
            },
        )
        self._create_open_order(high_count, yon="180")
        self._create_open_order(low_count, yon="180")

        order = self._create_order(lat=36.904100, lng=30.705600)
        selected = order.auto_assign_courier()

        self.assertEqual(selected, low_count)
        self.assertEqual(order.otomatik_atama_senaryosu, "Sabit-A7")
        self.assertEqual(lines[low_count.id].slot_paket_sayisi, 2)

    def test_14_smart_assignment_disabled_leaves_order_unassigned(self):
        self.restaurant.akilli_paket_atama = False
        courier = self._create_courier("Atanmaması Gereken Kurye")
        self._create_slot(courier)

        selected = self._create_order().auto_assign_courier()

        self.assertFalse(selected)

    def test_15_inactive_slot_line_is_skipped(self):
        inactive = self._create_courier(
            "Pasif Satırdaki Kurye",
            lat=36.885100,
        )
        active = self._create_courier(
            "Aktif Satırdaki Kurye",
            lat=36.886100,
        )
        self._create_slot(
            inactive | active,
            line_overrides={inactive.id: {"active": False}},
        )

        selected = self._create_order().auto_assign_courier()

        self.assertEqual(selected, active)

    def test_16_ended_courier_line_is_skipped(self):
        ended = self._create_courier(
            "İşi Bitmiş Kurye",
            lat=36.885100,
        )
        active = self._create_courier(
            "Çalışan Kurye",
            lat=36.886100,
        )
        self._create_slot(
            ended | active,
            line_overrides={ended.id: {"kurye_active": False}},
        )

        selected = self._create_order().auto_assign_courier()

        self.assertEqual(selected, active)

    def test_17_no_active_slot_leaves_order_unassigned(self):
        courier = self._create_courier("Slotsuz Kurye")
        self._create_slot(
            courier,
            start_delta=-8,
            end_delta=-1,
        )

        selected = self._create_order().auto_assign_courier()

        self.assertFalse(selected)

    def test_18_latest_overlapping_slot_is_selected_deterministically(self):
        old_slot_courier = self._create_courier(
            "Eski Slot Kuryesi",
            lat=36.885100,
        )
        new_slot_courier = self._create_courier(
            "Yeni Slot Kuryesi",
            lat=36.886100,
        )
        self._create_slot(
            old_slot_courier,
            start_delta=-2,
        )
        self._create_slot(
            new_slot_courier,
            start_delta=-1,
        )

        selected = self._create_order().auto_assign_courier()

        self.assertEqual(selected, new_slot_courier)

    def test_19_capacity_boundary_does_not_assign_fourth_package(self):
        courier = self._create_courier("Üç Paketli Kurye")
        self._create_slot(courier)
        for index in range(3):
            self._create_open_order(
                courier,
                yon="0",
                siparis_no="BOUNDARY-%s" % index,
            )

        selected = self._create_order().auto_assign_courier()

        self.assertFalse(selected)

    def test_20_order_without_coordinates_is_not_auto_assigned(self):
        courier = self._create_courier("Konumlu Kurye")
        self._create_slot(courier)

        selected = self._create_order(lat=0, lng=0).auto_assign_courier()

        self.assertFalse(selected)

    def test_21_real_automated_action_calls_assignment_engine(self):
        courier = self._create_courier("Action Tarafından Atanan Kurye")
        self._create_slot(courier)
        assignment_action = self.env.ref("corders.automation_21")
        assignment_action.active = True

        order = self._create_order(siparis_no="ACTION-END-TO-END")

        self.assertEqual(order.kurye, courier)
        self.assertEqual(order.otomatik_atama_senaryosu, "Sabit-A1")
        assignment_action.active = False

import logging
from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class CordersProfileCourierAssignment(models.Model):
    _inherit = "corders.profile"

    otomatik_atama_senaryosu = fields.Char(
        string="Otomatik Atama Senaryosu",
        copy=False,
        readonly=True,
    )

    _ASSIGNMENT_FINAL_STATES = ("teslim_edildi", "iptal_edildi")
    _ASSIGNMENT_WINDOW_HOURS = 24
    _FIXED_DIRECTION_TOLERANCE = 50.0

    @staticmethod
    def _assignment_has_coordinates(record):
        return bool(
            record
            and record.lat
            and record.lng
            and -90.0 <= record.lat <= 90.0
            and -180.0 <= record.lng <= 180.0
        )

    def _assignment_find_slot(self):
        self.ensure_one()
        if not self.magaza or not self.siparis_tarihi:
            return self.env["slots.profile"]
        return self.env["slots.profile"].search(
            [
                ("active_status", "=", True),
                ("magazalar", "in", self.magaza.id),
                ("start_date", "<=", self.siparis_tarihi),
                ("end_date", ">=", self.siparis_tarihi),
            ],
            order="start_date desc, id desc",
            limit=1,
        )

    def _assignment_open_orders_by_courier(self, courier_ids):
        self.ensure_one()
        grouped_orders = defaultdict(lambda: self.env["corders.profile"])
        if not courier_ids:
            return grouped_orders

        cutoff = fields.Datetime.now() - timedelta(hours=self._ASSIGNMENT_WINDOW_HOURS)
        open_orders = self.env["corders.profile"].search(
            [
                ("id", "!=", self.id),
                ("kurye", "in", courier_ids),
                ("siparis_durumu", "not in", self._ASSIGNMENT_FINAL_STATES),
                ("siparis_tarihi", ">=", cutoff),
            ],
            order="siparis_tarihi desc, id desc",
        )
        for order in open_orders:
            grouped_orders[order.kurye.id] |= order
        return grouped_orders

    def _assignment_direction(self, order):
        if order.yon:
            try:
                return float(order.yon)
            except (TypeError, ValueError):
                pass
        if (
            self._assignment_has_coordinates(order)
            and self._assignment_has_coordinates(order.magaza)
        ):
            return self.yon_tespiti(
                order.magaza.lat,
                order.magaza.lng,
                order.lat,
                order.lng,
            )
        return None

    @staticmethod
    def _assignment_angle_difference(first_angle, second_angle):
        difference = abs(float(first_angle) - float(second_angle)) % 360.0
        return min(difference, 360.0 - difference)

    def _assignment_route_matches(self, slot_type, open_orders):
        self.ensure_one()
        if not open_orders:
            return True

        if slot_type == "sabit":
            new_direction = self._assignment_direction(self)
            if new_direction is None:
                return False
            differences = [
                self._assignment_angle_difference(
                    new_direction,
                    existing_direction,
                )
                for existing_order in open_orders
                for existing_direction in [self._assignment_direction(existing_order)]
                if existing_direction is not None
            ]
            return bool(
                differences
                and min(differences) <= self._FIXED_DIRECTION_TOLERANCE
            )

        if not self._assignment_has_coordinates(self):
            return False
        valid_existing_orders = open_orders.filtered(
            self._assignment_has_coordinates
        )
        if not valid_existing_orders:
            return False
        grouping_radius = (
            self.magaza.atanacak_paketler_arasi_yaricap_mesafesi or 1500
        )
        closest_package_distance = min(
            self.find_distance(
                self.lat,
                self.lng,
                existing_order.lat,
                existing_order.lng,
            )
            for existing_order in valid_existing_orders
        )
        return closest_package_distance <= grouping_radius

    def _assignment_build_candidates(self, slot, excluded_courier_ids=None):
        self.ensure_one()
        excluded_courier_ids = set(excluded_courier_ids or ())
        if (
            not slot
            or not self._assignment_has_coordinates(self.magaza)
        ):
            return []

        active_lines = slot.skurye_profile_lines.filtered(
            lambda line: (
                line.active
                and line.kurye_active
                and line.partner_id
                and line.partner_id.id not in excluded_courier_ids
            )
        )
        courier_ids = active_lines.mapped("partner_id").ids
        open_orders_by_courier = self._assignment_open_orders_by_courier(
            courier_ids
        )
        max_packages = max(int(self.magaza.kurye_max_paket_sayisi or 3), 1)
        candidates = []

        for line in active_lines:
            courier = line.partner_id
            if (
                courier.kurye_mola_durumu
                or courier.kurye_durumu not in ("musait", "pakette")
                or not self._assignment_has_coordinates(courier)
            ):
                continue
            open_orders = open_orders_by_courier[courier.id]
            if len(open_orders) >= max_packages:
                continue
            candidates.append(
                {
                    "line": line,
                    "courier": courier,
                    "distance": self.find_distance(
                        self.magaza.lat,
                        self.magaza.lng,
                        courier.lat,
                        courier.lng,
                    ),
                    "open_orders": open_orders,
                    "open_count": len(open_orders),
                    "route_matches": self._assignment_route_matches(
                        slot.slot_tipi,
                        open_orders,
                    ),
                }
            )
        return candidates

    @staticmethod
    def _assignment_phase_candidates(
        candidates,
        statuses,
        max_distance=None,
        require_route=True,
    ):
        return [
            candidate
            for candidate in candidates
            if (
                candidate["courier"].kurye_durumu in statuses
                and (
                    max_distance is None
                    or candidate["distance"] <= max_distance
                )
                and (
                    not require_route
                    or candidate["route_matches"]
                )
            )
        ]

    def _assignment_select_candidate(self, slot, excluded_courier_ids=None):
        self.ensure_one()
        candidates = self._assignment_build_candidates(
            slot,
            excluded_courier_ids=excluded_courier_ids,
        )
        if not candidates:
            return None, None

        phases = (
            ("A1", ("musait",), 500.0, True, False),
            ("A2", ("musait",), 1200.0, True, False),
            ("A3", ("pakette",), 750.0, True, False),
            ("A4", ("musait",), 2000.0, True, False),
            ("A5", ("musait", "pakette"), None, True, False),
            ("A7", ("musait",), None, False, True),
        )
        for scenario, statuses, max_distance, require_route, fair_fallback in phases:
            phase_candidates = self._assignment_phase_candidates(
                candidates,
                statuses=statuses,
                max_distance=max_distance,
                require_route=require_route,
            )
            if not phase_candidates:
                continue
            if fair_fallback:
                phase_candidates.sort(
                    key=lambda candidate: (
                        candidate["line"].slot_paket_sayisi,
                        candidate["open_count"],
                        candidate["distance"],
                        candidate["courier"].id,
                    )
                )
            else:
                phase_candidates.sort(
                    key=lambda candidate: (
                        candidate["distance"],
                        candidate["open_count"],
                        candidate["line"].slot_paket_sayisi,
                        candidate["courier"].id,
                    )
                )
            return phase_candidates[0], scenario
        return None, None

    def _assignment_lock_courier(self, courier):
        self.ensure_one()
        self.env.cr.execute(
            "SELECT id FROM res_partner WHERE id = %s FOR UPDATE",
            [courier.id],
        )
        courier.invalidate_recordset(
            [
                "kurye_durumu",
                "kurye_mola_durumu",
                "lat",
                "lng",
            ]
        )

    def _assignment_candidate_still_valid(self, slot, candidate, scenario):
        self.ensure_one()
        courier = candidate["courier"]
        line = candidate["line"]
        line.invalidate_recordset(["active", "kurye_active", "slot_paket_sayisi"])
        if (
            not line.active
            or not line.kurye_active
            or courier.kurye_mola_durumu
            or courier.kurye_durumu not in ("musait", "pakette")
            or not self._assignment_has_coordinates(courier)
        ):
            return False

        max_packages = max(int(self.magaza.kurye_max_paket_sayisi or 3), 1)
        open_orders = self._assignment_open_orders_by_courier(
            [courier.id]
        )[courier.id]
        if len(open_orders) >= max_packages:
            return False

        if scenario != "A7" and not self._assignment_route_matches(
            slot.slot_tipi,
            open_orders,
        ):
            return False
        if scenario == "A7" and courier.kurye_durumu != "musait":
            return False
        return True

    def _assignment_force_working_courier(self, slot):
        """Never leave an order idle while its slot has a working courier."""
        self.ensure_one()
        empty_courier = self.env["res.partner"]
        excluded_courier_ids = set()

        while True:
            working_lines = slot.skurye_profile_lines.filtered(
                lambda line: (
                    line.active
                    and line.kurye_active
                    and line.partner_id
                    and line.partner_id.id not in excluded_courier_ids
                    and not line.partner_id.kurye_mola_durumu
                    and line.partner_id.kurye_durumu in ("musait", "pakette")
                )
            )
            if not working_lines:
                return empty_courier

            courier_ids = working_lines.mapped("partner_id").ids
            open_orders_by_courier = self._assignment_open_orders_by_courier(
                courier_ids
            )

            def forced_priority(line):
                courier = line.partner_id
                distance = float("inf")
                if (
                    self._assignment_has_coordinates(self.magaza)
                    and self._assignment_has_coordinates(courier)
                ):
                    distance = self.find_distance(
                        self.magaza.lat,
                        self.magaza.lng,
                        courier.lat,
                        courier.lng,
                    )
                return (
                    len(open_orders_by_courier[courier.id]),
                    line.slot_paket_sayisi,
                    distance,
                    courier.id,
                )

            line = sorted(working_lines, key=forced_priority)[0]
            courier = line.partner_id
            self._assignment_lock_courier(courier)
            line.invalidate_recordset(
                ["active", "kurye_active", "slot_paket_sayisi"]
            )
            if (
                not line.active
                or not line.kurye_active
                or courier.kurye_mola_durumu
                or courier.kurye_durumu not in ("musait", "pakette")
            ):
                excluded_courier_ids.add(courier.id)
                continue

            values = {
                "kurye": courier.id,
                "kurye_telefonu": courier.mobile,
                "otomatik_atama_senaryosu": "%s-Zorunlu-%s"
                % (
                    "Sabit" if slot.slot_tipi == "sabit" else "Bölge",
                    "TekKurye"
                    if len(working_lines) == 1
                    else "Fallback",
                ),
            }
            if (
                self._assignment_has_coordinates(self)
                and self._assignment_has_coordinates(self.magaza)
            ):
                values.update(
                    {
                        "mesafe": min(
                            self.find_distance(
                                self.magaza.lat,
                                self.magaza.lng,
                                self.lat,
                                self.lng,
                            ),
                            6000.0,
                        ),
                        "yon": str(
                            self.yon_tespiti(
                                self.magaza.lat,
                                self.magaza.lng,
                                self.lat,
                                self.lng,
                            )
                        ),
                    }
                )
            self.write(values)
            line.write(
                {
                    "slot_paket_sayisi": line.slot_paket_sayisi + 1,
                }
            )
            _logger.info(
                "%s siparişi %s kuryesine %s senaryosuyla zorunlu atandı.",
                self.siparis_no or self.id,
                courier.display_name,
                values["otomatik_atama_senaryosu"],
            )
            return courier

    def auto_assign_courier(self):
        """Assign one courier safely and return it, or an empty recordset."""
        self.ensure_one()
        empty_courier = self.env["res.partner"]
        if self.kurye:
            return self.kurye
        if not self.magaza or not self.magaza.akilli_paket_atama:
            return empty_courier
        if not self.siparis_tarihi:
            self.siparis_tarihi = fields.Datetime.now()

        slot = self._assignment_find_slot()
        if not slot:
            return empty_courier

        working_lines = slot.skurye_profile_lines.filtered(
            lambda line: (
                line.active
                and line.kurye_active
                and line.partner_id
                and not line.partner_id.kurye_mola_durumu
                and line.partner_id.kurye_durumu in ("musait", "pakette")
            )
        )
        if len(working_lines) == 1:
            return self._assignment_force_working_courier(slot)

        if (
            not self._assignment_has_coordinates(self)
            or not self._assignment_has_coordinates(self.magaza)
        ):
            return self._assignment_force_working_courier(slot)

        excluded_courier_ids = set()
        while True:
            candidate, scenario = self._assignment_select_candidate(
                slot,
                excluded_courier_ids=excluded_courier_ids,
            )
            if not candidate:
                return self._assignment_force_working_courier(slot)

            courier = candidate["courier"]
            self._assignment_lock_courier(courier)
            if not self._assignment_candidate_still_valid(
                slot,
                candidate,
                scenario,
            ):
                excluded_courier_ids.add(courier.id)
                continue

            order_direction = self.yon_tespiti(
                self.magaza.lat,
                self.magaza.lng,
                self.lat,
                self.lng,
            )
            order_distance = self.find_distance(
                self.magaza.lat,
                self.magaza.lng,
                self.lat,
                self.lng,
            )
            scenario_name = "%s-%s" % (
                "Sabit" if slot.slot_tipi == "sabit" else "Bölge",
                scenario,
            )
            self.write(
                {
                    "kurye": courier.id,
                    "kurye_telefonu": courier.mobile,
                    "mesafe": min(order_distance, 6000.0),
                    "yon": str(order_direction),
                    "otomatik_atama_senaryosu": scenario_name,
                }
            )
            candidate["line"].write(
                {
                    "slot_paket_sayisi":
                        candidate["line"].slot_paket_sayisi + 1,
                }
            )
            _logger.info(
                "%s siparişi %s kuryesine %s senaryosuyla atandı.",
                self.siparis_no or self.id,
                courier.display_name,
                scenario_name,
            )
            return courier

    def prepare_and_auto_assign_courier(self):
        """Validate/prepare an order and run the tested assignment engine."""
        self.ensure_one()
        if not self.pos_entegrasyon_firmasi:
            missing_fields = [
                (self.musteri_adi, "Lütfen Müşteri Adını Giriniz!"),
                (self.adres, "Lütfen Adres Alanını Giriniz!"),
                (self.odeme_yontemi, "Lütfen Ödeme Yöntemi Alanını Giriniz!"),
                (self.platform, "Lütfen Platform Alanını Giriniz!"),
                (self.magaza, "Lütfen Mağaza Alanını Giriniz!"),
            ]
            for value, message in missing_fields:
                if not value:
                    raise UserError(message)
        if not self.musteri_telefonu:
            raise UserError("Lütfen Müşteri Telefonu Alanını Giriniz!")

        preparation_values = {"siparis_tarihi": fields.Datetime.now()}
        if not self.siparis_no and not self.pos_entegrasyon_firmasi:
            preparation_values["siparis_no"] = self.generate_random_code()
        self.write(preparation_values)

        if (
            not self._assignment_has_coordinates(self)
            and self.adres
        ):
            try:
                response = self.get_lat_lng(
                    self.id,
                    "%s %s" % (self.adres, self.adres_tarifi or ""),
                )
                location = (
                    response.get("results", [{}])[0]
                    .get("geometry", {})
                    .get("location", {})
                ) if response.get("status") == "OK" else {}
                if location.get("lat") and location.get("lng"):
                    self.write(
                        {
                            "lat": location["lat"],
                            "lng": location["lng"],
                        }
                    )
            except Exception:
                _logger.exception(
                    "%s siparişinin adresi koordinata çevrilemedi.",
                    self.siparis_no or self.id,
                )
        return self.auto_assign_courier()

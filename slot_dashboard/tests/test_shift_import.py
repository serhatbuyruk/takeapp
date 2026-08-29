import base64
from datetime import datetime, time, timedelta
from io import BytesIO

import xlsxwriter

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'slot_dashboard_shift_import')
class TestSlotDashboardShiftImport(TransactionCase):

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
        cls.admin = cls.env['res.users'].with_context(
            no_reset_password=True
        ).create({
            'name': 'Vardiya İçe Aktarma Yöneticisi',
            'login': 'shift.import.admin@test.invalid',
            'tz': 'Europe/Istanbul',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('slots.slots_group_admin').id,
            ])],
        })
        cls.restaurant = cls.env['res.partner'].create({
            'name': 'Atlas Burger Lara',
            'user_role': 'magaza',
            'slot_tipi': 'sabit',
            'street': 'Test Caddesi 1',
            'currency_id': cls.currency.id,
        })
        cls.courier_1 = cls.env['res.partner'].create({
            'name': 'Ali Vardiya Test',
            'user_role': 'kurye',
            'currency_id': cls.currency.id,
        })
        cls.courier_2 = cls.env['res.partner'].create({
            'name': 'Ayşe Vardiya Test',
            'user_role': 'kurye',
            'currency_id': cls.currency.id,
        })
        cls.plan_date = fields.Date.context_today(
            cls.env['slots.profile']
        ) + timedelta(days=30)

    @staticmethod
    def _xlsx(rows, headers=None):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Sayfa1')
        date_format = workbook.add_format({'num_format': 'dd.mm.yyyy'})
        time_format = workbook.add_format({'num_format': 'hh:mm'})
        headers = headers or [
            'TARİH',
            'BÖLGE',
            'PROJE',
            'ŞUBE',
            'KURYE',
            'VARDİYA GİRİŞ',
            'VARDİYA ÇIKIŞ',
        ]
        for column, header in enumerate(headers):
            worksheet.write(0, column, header)
        for row_index, row in enumerate(rows, start=1):
            worksheet.write_datetime(
                row_index,
                0,
                datetime.combine(row[0], time.min),
                date_format,
            )
            for column in range(1, 5):
                worksheet.write(row_index, column, row[column])
            start_fraction = (
                row[5].hour * 3600 + row[5].minute * 60 + row[5].second
            ) / 86400
            end_fraction = (
                row[6].hour * 3600 + row[6].minute * 60 + row[6].second
            ) / 86400
            worksheet.write_number(row_index, 5, start_fraction, time_format)
            worksheet.write_number(row_index, 6, end_fraction, time_format)
        workbook.close()
        return base64.b64encode(output.getvalue())

    def _row(
        self,
        courier=None,
        start=time(9, 0),
        end=time(18, 0),
        project='Atlas Burger',
        branch='Lara',
        plan_date=None,
    ):
        return (
            plan_date or self.plan_date,
            'Antalya',
            project,
            branch,
            courier or self.courier_1.name,
            start,
            end,
        )

    def _import(self, rows, filename='vardiya-plani.xlsx', headers=None):
        wizard = self.env[
            'slot.dashboard.shift.import.wizard'
        ].with_user(self.admin).create({
            'filename': filename,
            'upload_file': self._xlsx(rows, headers=headers),
        })
        wizard.action_preview()
        if not wizard.valid_row_count:
            raise ValidationError(wizard.preview_message)
        wizard.action_import_valid_rows()
        return self.env[
            'slot.dashboard.shift.import.batch'
        ].search([('filename', '=', filename)], order='id desc', limit=1)

    def test_import_groups_restaurant_rows_into_one_fixed_slot(self):
        batch = self._import([
            self._row(),
            self._row(
                courier=self.courier_2.name,
                start=time(12, 0),
                end=time(23, 0),
            ),
        ])

        self.assertEqual(batch.slot_count, 1)
        self.assertEqual(batch.shift_count, 2)
        self.assertEqual(batch.skipped_count, 0)
        slot = batch.slot_ids
        self.assertEqual(slot.slot_tipi, 'sabit')
        self.assertEqual(slot.magazalar, self.restaurant)
        self.assertEqual(
            slot.skurye_profile_lines.mapped('partner_id'),
            self.courier_1 | self.courier_2,
        )
        self.assertTrue(
            all(slot.skurye_profile_lines.mapped('paket_mutabakat_gerekli'))
        )
        self.assertEqual(
            set(slot.skurye_profile_lines.mapped('shift_plan_project')),
            {'Atlas Burger'},
        )

    def test_second_identical_upload_does_not_create_duplicates(self):
        rows = [self._row()]
        first_batch = self._import(rows, filename='ilk-plan.xlsx')
        slot = first_batch.slot_ids
        slot_count = self.env['slots.profile'].search_count([
            ('id', 'in', slot.ids),
        ])

        second_batch = self._import(rows, filename='ikinci-plan.xlsx')

        self.assertEqual(slot_count, 1)
        self.assertEqual(second_batch.slot_count, 0)
        self.assertEqual(second_batch.updated_slot_count, 1)
        self.assertEqual(second_batch.shift_count, 1)
        self.assertEqual(second_batch.skipped_count, 0)
        self.assertEqual(len(slot.skurye_profile_lines), 1)

    def test_midnight_crossing_shift_ends_on_next_day(self):
        batch = self._import([
            self._row(start=time(12, 0), end=time(0, 0)),
        ])
        line = batch.line_ids

        self.assertEqual(
            line.kurye_end_date - line.kurye_start_date,
            timedelta(hours=11, minutes=59, seconds=59),
        )
        self.assertEqual(batch.slot_ids.end_date, line.kurye_end_date)

    def test_import_converts_matched_restaurant_to_fixed_model(self):
        region_restaurant = self.env['res.partner'].create({
            'name': 'Bölgeden Sabite Geçen Restoran',
            'user_role': 'magaza',
            'slot_tipi': 'bolge',
            'street': 'Dönüşüm Caddesi',
            'currency_id': self.currency.id,
        })
        batch = self._import([
            self._row(
                project=region_restaurant.name,
                branch='Merkez',
            ),
        ], filename='sabit-modele-donusum.xlsx')

        self.assertEqual(batch.slot_ids.magazalar, region_restaurant)
        self.assertEqual(region_restaurant.slot_tipi, 'sabit')
        self.assertFalse(region_restaurant.kuryeler)

    def test_existing_manual_restaurant_overlap_is_reported(self):
        start = datetime.combine(self.plan_date, time(7, 0))
        existing = self.env['slots.profile'].create({
            'name': 'Mevcut Çakışan Restoran Slotu',
            'slot_tipi': 'sabit',
            'magazalar': [(6, 0, self.restaurant.ids)],
            'start_date': start,
            'end_date': start + timedelta(hours=5),
            'slot_acik_adresi': self.restaurant.street,
            'currency_id': self.currency.id,
        })
        batch_count = self.env[
            'slot.dashboard.shift.import.batch'
        ].search_count([])

        with self.assertRaisesRegex(ValidationError, 'mevcut.*çakışıyor'):
            self._import([self._row(start=time(10), end=time(18))])

        self.assertTrue(existing.exists())
        self.assertEqual(
            self.env[
                'slot.dashboard.shift.import.batch'
            ].search_count([]),
            batch_count,
        )

    def test_existing_courier_overlap_at_other_restaurant_aborts_import(self):
        other_restaurant = self.env['res.partner'].create({
            'name': 'Başka Restoran',
            'user_role': 'magaza',
            'slot_tipi': 'sabit',
            'street': 'Başka Cadde',
            'currency_id': self.currency.id,
        })
        start = datetime.combine(self.plan_date, time(8, 0))
        slot = self.env['slots.profile'].create({
            'name': 'Başka Restoran Mevcut Slot',
            'slot_tipi': 'sabit',
            'magazalar': [(6, 0, other_restaurant.ids)],
            'start_date': start,
            'end_date': start + timedelta(hours=10),
            'slot_acik_adresi': other_restaurant.street,
        })
        self.env['skurye.profile.lines'].create({
            'sequence': slot.id,
            'partner_id': self.courier_1.id,
            'kurye_start_date': start,
            'kurye_end_date': start + timedelta(hours=10),
        })

        with self.assertRaisesRegex(ValidationError, 'mevcut.*vardiyasıyla'):
            self._import([self._row(start=time(10), end=time(17))])

    def test_unmatched_courier_is_reported_and_valid_row_is_imported(self):
        slot_count = self.env['slots.profile'].search_count([])
        batch = self._import([
            self._row(),
            self._row(courier='Sistemde Olmayan Kurye'),
        ])
        self.assertEqual(
            self.env['slots.profile'].search_count([]),
            slot_count + 1,
        )
        self.assertEqual(batch.shift_count, 1)
        self.assertEqual(batch.skipped_count, 1)

    def test_ambiguous_restaurant_aborts_import(self):
        self.env['res.partner'].create({
            'name': 'Atlas Burger Lara',
            'user_role': 'magaza',
            'slot_tipi': 'sabit',
            'currency_id': self.currency.id,
        })
        with self.assertRaisesRegex(ValidationError, 'birden fazla kayıtla'):
            self._import([self._row()])

    def test_repeated_courier_in_same_file_uses_last_row(self):
        batch = self._import([
            self._row(start=time(9), end=time(15)),
            self._row(start=time(14), end=time(20)),
        ])
        self.assertEqual(batch.shift_count, 1)
        self.assertEqual(batch.skipped_count, 1)
        line = batch.slot_ids.skurye_profile_lines.filtered(
            lambda item: item.partner_id == self.courier_1
        )
        self.assertEqual(line.kurye_start_date.hour, 11)
        self.assertEqual(line.kurye_end_date.hour, 17)

    def test_cross_midnight_restaurant_conflict_skips_later_group(self):
        batch = self._import([
            self._row(start=time(21), end=time(5)),
            self._row(
                courier=self.courier_2.name,
                start=time(4),
                end=time(12),
                plan_date=self.plan_date + timedelta(days=1),
            ),
        ])
        self.assertEqual(batch.shift_count, 1)
        self.assertEqual(batch.skipped_count, 1)

    def test_later_upload_merges_new_courier_and_updates_repeated_one(self):
        first_batch = self._import([
            self._row(start=time(9), end=time(18)),
        ], filename='ilk-birlesim.xlsx')
        slot = first_batch.slot_ids

        self._import([
            self._row(
                courier=self.courier_2.name,
                start=time(12),
                end=time(23),
            ),
        ], filename='ek-kurye.xlsx')
        self.assertEqual(
            slot.skurye_profile_lines.mapped('partner_id'),
            self.courier_1 | self.courier_2,
        )

        self._import([
            self._row(start=time(10), end=time(19)),
        ], filename='kurye-guncelle.xlsx')
        courier_1_line = slot.skurye_profile_lines.filtered(
            lambda item: item.partner_id == self.courier_1
        )
        self.assertEqual(courier_1_line.kurye_start_date.hour, 7)
        self.assertEqual(courier_1_line.kurye_end_date.hour, 16)
        self.assertIn(self.courier_2, slot.skurye_profile_lines.partner_id)

    def test_changed_headers_are_rejected(self):
        headers = [
            'TARİH',
            'BÖLGE',
            'RESTORAN',
            'ŞUBE',
            'KURYE',
            'VARDİYA GİRİŞ',
            'VARDİYA ÇIKIŞ',
        ]
        with self.assertRaisesRegex(ValidationError, 'başlıkları'):
            self._import([self._row()], headers=headers)

    def test_package_status_colors_follow_end_and_declaration(self):
        batch = self._import([self._row()])
        line = batch.line_ids
        self.assertEqual(line.dashboard_package_state, 'upcoming')

        line.kurye_end_date = fields.Datetime.now() - timedelta(seconds=1)
        self.assertEqual(line.dashboard_package_state, 'missing')

        line.with_context(package_reconciliation_write=True).write({
            'kurye_paket_beyani_yapildi': True,
            'kurye_beyan_paket_sayisi': 8,
        })
        self.assertEqual(line.dashboard_package_state, 'submitted')

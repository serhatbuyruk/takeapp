from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from odoo import fields
from odoo.tests import TransactionCase, new_test_user, tagged

from ..controllers.package_reconciliation import (
    CourierPackageReconciliationController,
)


@tagged('post_install', '-at_install', 'package_reconciliation_controller')
class TestCourierPackageReconciliationController(TransactionCase):

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
        cls.user = new_test_user(
            cls.env,
            login='package-popup-courier',
            password='package-popup-courier',
            groups='base.group_user',
        )
        cls.user.partner_id.write({
            'name': 'Popup Zaman Test Kuryesi',
            'user_role': 'kurye',
        })
        cls.restaurant = cls.env['res.partner'].create({
            'name': 'Popup Zaman Test Restoranı',
            'user_role': 'magaza',
            'slot_tipi': 'sabit',
            'currency_id': cls.env.company.currency_id.id,
        })
        now = fields.Datetime.now()
        cls.slot = cls.env['slots.profile'].create({
            'name': 'Popup Zaman Sınırı Test Slotu',
            'slot_tipi': 'sabit',
            'magazalar': [(6, 0, cls.restaurant.ids)],
            'start_date': now - timedelta(hours=1),
            'end_date': now + timedelta(hours=2),
            'active_status': True,
            'currency_id': cls.env.company.currency_id.id,
        })
        cls.line = cls.env['skurye.profile.lines'].create({
            'name': 'Popup Zaman Sınırı Test Satırı',
            'sequence': cls.slot.id,
            'partner_id': cls.user.partner_id.id,
            'kurye_start_date': now - timedelta(hours=1),
            'kurye_end_date': now + timedelta(hours=1),
            'start_date': now - timedelta(minutes=59),
            'active': True,
            'kurye_active': True,
        })

    def _controller_request(self):
        return patch(
            'odoo.addons.kuryetec_website.controllers.'
            'package_reconciliation.request',
            SimpleNamespace(env=self.env(user=self.user)),
        )

    def test_controller_popup_requirement_changes_when_slot_ends(self):
        controller = CourierPackageReconciliationController()
        with self._controller_request():
            before_end = controller.pending_package_reconciliation()
        self.assertFalse(
            before_end['required'],
            'Popup kurye bitiş saatinden önce açılmamalı.',
        )

        self.line.kurye_end_date = fields.Datetime.now() - timedelta(seconds=1)
        self.env.flush_all()

        with self._controller_request():
            after_end = controller.pending_package_reconciliation()
        self.assertTrue(
            after_end['required'],
            'Popup kurye bitiş saati geçince zorunlu olmalı.',
        )
        self.assertEqual(after_end['line_id'], self.line.id)
        self.assertEqual(after_end['slot_name'], self.slot.name)
        self.assertEqual(after_end['restaurant_name'], self.restaurant.name)

    def test_controller_submission_clears_popup_requirement(self):
        self.line.kurye_end_date = fields.Datetime.now() - timedelta(seconds=1)
        self.env.flush_all()
        controller = CourierPackageReconciliationController()

        with self._controller_request():
            result = controller.submit_package_reconciliation(
                line_id=self.line.id,
                package_count=12,
            )
        self.assertEqual(result['status'], 'success')

        with self._controller_request():
            after_submit = controller.pending_package_reconciliation()
        self.assertFalse(
            after_submit['required'],
            'Beyan gönderilince aynı slot popupı tekrar açılmamalı.',
        )

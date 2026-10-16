from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    partners = env['res.partner'].search([
        ('courier_field_manager_partner_id', '=', False),
        ('courier_field_manager_id', '!=', False),
    ])
    for partner in partners:
        partner.courier_field_manager_partner_id = partner.courier_field_manager_id.partner_id

    calls = env['partner.courier.call'].search([
        ('manager_partner_id', '=', False),
        ('manager_user_id', '!=', False),
    ])
    for call in calls:
        call.manager_partner_id = call.manager_user_id.partner_id

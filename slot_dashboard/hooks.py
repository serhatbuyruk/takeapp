from odoo import SUPERUSER_ID, api


ADMIN_GROUP_XMLIDS = (
    'base.group_system',
    'slots.slots_group_admin',
    'slots.slots_group_fullaccess',
    'corders.corders_group_admin',
    'corders.corders_group_fullaccess',
)


def _dashboard_admin_users(env):
    users = env['res.users']
    for xmlid in ADMIN_GROUP_XMLIDS:
        group = env.ref(xmlid, raise_if_not_found=False)
        if group:
            users |= group.users
    return users.filtered(lambda user: user.active and not user.share)


def _remove_legacy_dashboard(env):
    for xmlid in (
        'slots.menu_operation_dashboard',
        'slots.action_operation_dashboard',
    ):
        record = env.ref(xmlid, raise_if_not_found=False)
        if record:
            record.sudo().unlink()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _remove_legacy_dashboard(env)
    action = env.ref('slot_dashboard.action_operation_dashboard')
    _dashboard_admin_users(env).sudo().write({'action_id': action.id})


def pre_uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    action = env.ref(
        'slot_dashboard.action_operation_dashboard',
        raise_if_not_found=False,
    )
    if action:
        env['res.users'].sudo().search([
            ('action_id', '=', action.id),
        ]).write({'action_id': False})

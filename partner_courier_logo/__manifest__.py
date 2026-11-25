{
    'name': 'Partner Courier Logo',
    'version': '16.0.2.0.9',
    'category': 'Contacts',
    'summary': 'Logo Isbasi courier invoice integration with central account login',
    'depends': ['partner_courier_accounting'],
    'author': 'Esa Teknik',
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/partner_courier_logo_invoice_views.xml',
        'views/courier_logo_portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

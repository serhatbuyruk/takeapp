{
    'name': 'Partner Courier Notification',
    'version': '16.0.1.0.0',
    'category': 'Contacts',
    'summary': 'Send OneSignal notifications to couriers',
    'depends': ['contacts', 'mail', 'partner_courier_accounting'],
    'author': 'Esa Teknik',
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/partner_courier_notification_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

{
    'name': 'Partner Courier Notification',
    'version': '16.0.2.2.1',
    'category': 'Contacts',
    'summary': 'Send OneSignal or Firebase notifications to couriers',
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

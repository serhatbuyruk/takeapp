{
    'name': 'Partner Courier Call',
    'version': '16.0.1.16.0',
    'category': 'Contacts',
    'summary': 'Courier to field manager voice and video calls',
    'depends': [
        'mail',
        'website',
        'partner_courier_accounting',
        'partner_courier_notification',
    ],
    'author': 'Esa Teknik',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/partner_courier_call_cron.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/partner_courier_call_views.xml',
        'views/courier_call_portal_templates.xml',
        'views/courier_call_public_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'partner_courier_call/static/src/scss/courier_call_portal.scss',
        ],
        'mail.assets_discuss_public': [
            'partner_courier_call/static/src/js/discuss_public_audio_call.js',
            'partner_courier_call/static/src/scss/courier_call_public.scss',
            'partner_courier_call/static/src/xml/courier_call_components.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

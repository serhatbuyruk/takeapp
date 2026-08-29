{
    'name': 'Kuryetec Website Pages',
    'version': '16.0.1.11.9',
    'category': 'Website',
    'summary': 'Code-managed Kuryetec frontend pages',
    'depends': ['website', 'corders', 'slots', 'notifier'],
    'data': [
        'views/website_pages.xml',
        'views/package_reconciliation_templates.xml',
        'data/website_configuration.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'kuryetec_website/static/src/css/courier_home.css',
            'kuryetec_website/static/src/css/welcome_home.css',
            'kuryetec_website/static/src/css/history_page.css',
            'kuryetec_website/static/src/css/payments_page.css',
            'kuryetec_website/static/src/css/mobile_pages.css',
            'kuryetec_website/static/src/css/package_reconciliation.css',
            'kuryetec_website/static/src/js/remove_battery_warning.js',
            'kuryetec_website/static/src/js/courier_slot_start.js',
            'kuryetec_website/static/src/js/package_reconciliation.js',
        ],
    },
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

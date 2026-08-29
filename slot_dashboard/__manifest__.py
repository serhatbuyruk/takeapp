{
    'name': 'Vardiya Operasyon Dashboardu',
    'version': '16.0.1.7.4',
    'category': 'Operations',
    'summary': 'Kuryetec günlük vardiya ve kurye operasyon dashboardu',
    'author': 'Autoronics',
    'website': 'https://www.autoronics.com',
    'depends': [
        'web',
        'slots',
        'corders',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/restaurant_views.xml',
        'views/shift_management_views.xml',
        'views/earnings_views.xml',
        'views/dashboard_views.xml',
    ],
    'external_dependencies': {
        'python': ['xlrd', 'xlsxwriter'],
    },
    'assets': {
        'web.assets_backend': [
            'slot_dashboard/static/src/js/operation_dashboard.js',
            'slot_dashboard/static/src/xml/operation_dashboard.xml',
            'slot_dashboard/static/src/scss/operation_dashboard.scss',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'pre_uninstall_hook': 'pre_uninstall_hook',
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
{
    'name': "PayTR Payment Provider",
    'summary': """Easily get paid by credit card""",
    'description': """Easily get paid by credit card""",
    'author': "Çağlar MERSİNLİ",
    'maintainer': 'Çağlar MERSİNLİ',
    'website': "https://caglarmersinli.com.tr",
    'category': 'Accounting/Payment Providers',
    'version': '16.0.0',
    'depends': ['payment', 'event_sale'],
    'external_dependencies': {'python': ['phonenumbers']},
    'data': [
        'views/payment_paytr_templates.xml',
        'views/payment_provider_view.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_trpay/static/src/js/payment_form.js',
        ],
        'web.assets_frontend_minimal': [
            'payment_trpay/static/src/js/iframeResizer.min.js',
        ]
    },
    "installable": True,
    'application': False,
    'license': 'OPL-1',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'price': 89.00,
    'currency': 'EUR',
    "support": "ceremy@gmail.com",
    "images": ['static/description/banner.png'],

}

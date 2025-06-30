{
    'name': 'Allow Many2one Open New Tab Or Popup',
    'summary': "Allow to configure Many2one field behaviour. Many2one can open in new tab or showing popup.",
    'description': """
        Allow to configure Many2one field behaviour. Many2one can open in new tab or showing popup.
    """,
    'author': "Sonny Huynh",
    'version': '0.1',
    'depends': ['web', 'sale', 'mail'],

    'data': [
        'views/res_config_settings_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'many2one_field_behaviour/static/src/js/many2one_field.js',
            'many2one_field_behaviour/static/src/js/message_model.js',
            'many2one_field_behaviour/static/src/js/message_view.js',
        ],
    },

    'images': ['static/description/banner.gif'],
    'application': False,
    'license': 'OPL-1',
    'price': 45.00,
    'currency': 'EUR',
}
{
    'name':'translations',
    'version': '1.5.19',
    'author': 'Serhat Buyruk',
    'summary': 'Translations Management System',
    'sequence': 1,
    'description':'This module is ai based translations management system software suppored in Odoo',
    'category':'translations',
    'website':'https://www.autoronics.com',
    'depends':['base','website','queue_job'],

    'data':[
        'security/ir.model.access.csv',
        'views/textline_profile_views.xml',
        'views/ir_ui_view.xml',
        'views/res_config_settings_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [

        ],
        'web.assets_backend': [
            'translations/static/src/css/translation_editor.css',
        ],
        'installable': True,
    }

}

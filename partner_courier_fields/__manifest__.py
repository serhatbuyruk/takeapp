{
    'name': 'Partner Courier Extra Fields',
    'version': '16.0.1.0.0',
    'summary': 'Adds courier-related fields to res.partner',
    'depends': ['base','contacts'],
    'author': 'Esa Teknik',
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'wizard/partner_courier_tc_import_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}

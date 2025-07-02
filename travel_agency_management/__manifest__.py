{
    'name': 'Travel Agency Management',
    'version': '16.0.2.2.0', # Sürümü artırmak iyi bir pratiktir
    'summary': 'A comprehensive module to manage a travel agency business.',
    'description': """
        Implements a custom "flat form" for sales orders while maintaining
        compatibility with standard Odoo invoicing through a background
        order line. Adds a custom travel itinerary report.
    """,
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'category': 'Services/Travel',
    'depends': [
        'base', 
        'sale_management',
        'contacts',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/travel_service_type_data.xml',
        'data/travel_airport_data.xml',
        'data/travel_product_data.xml',
        'views/travel_service_type_views.xml',  # <-- BU SATIRI EKLEYİN
        'views/travel_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/main_menus.xml',
        'report/travel_reports.xml',
    ],
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
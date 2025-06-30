{
    'name':'rentals',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Rentals Home Management System',
    'sequence': 1,
    'description':'This is rentals home management system software suppored in Odoo',
    'category':'rentals',
    'website':'https://www.autoronics.com',
    'depends':['base','website','product'],

    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
        #'views/all_records_list.xml',
        # 'views/record_item.xml',
        #'views/form_response.xml',
        #'views/sale_order.xml',
        #'views/form_request.xml',
        #'views/car_view.xml',
        #'views/extra.xml',
        #'views/city.xml',
        #'views/snippets/s_booking_widget.xml',
        #'views/snippets/demo/s_cart_product/s_cart_products.xml',
        #'views/snippets/demo/snippets.xml',
        'views/rentals_view.xml',
        'views/rentals_wizard.xml',
        'views/inherit_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'rentals/static/src/css/intlTelInput.css',
            # 'rentals/static/src/css/jquery-clockpicker.min.css',
            # 'rentals/static/src/css/style.css',
            # 'rentals/static/src/js/jquery-clockpicker.min.js',
            # 'rentals/static/src/js/intlTelInput.min.js',
            # 'rentals/static/src/js/utils.js',
            # 'rentals/static/src/js/reservation.js',
            # 'rentals/static/src/js/script.js',
            'rentals/static/src/css/xml_form.css',
            'rentals/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            'rentals/static/src/js/thunkableWebviewerExtension.js',
            'rentals/static/src/css/xml_form.css',
            'rentals/static/src/css/theme.css',
            #'rentals/static/src/js/test.js',
        ]
    }

}

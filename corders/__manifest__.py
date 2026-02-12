{
    'name':'corders',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Corders Home Management System',
    'sequence': 1,
    'description':'This is corders home management system software suppored in Odoo',
    'category':'corders',
    'website':'https://www.autoronics.com',
    'depends':['base','contacts','website','product'],

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
        'views/corders_view.xml',
        'views/orderline_view.xml',
        'views/corders_wizard.xml',
        'views/inherit_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'corders/static/src/css/intlTelInput.css',
            # 'corders/static/src/css/jquery-clockpicker.min.css',
            # 'corders/static/src/css/style.css',
            # 'corders/static/src/js/jquery-clockpicker.min.js',
            # 'corders/static/src/js/intlTelInput.min.js',
            # 'corders/static/src/js/utils.js',
            # 'corders/static/src/js/reservation.js',
            # 'corders/static/src/js/script.js',
            'corders/static/src/css/xml_form.css',
            'corders/static/src/css/leaflet.css',
            'corders/static/src/js/leaflet.js',
            'corders/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            #'corders/static/src/js/thunkableWebviewerExtension.js',
            #'corders/static/src/css/xml_form.css',
            'corders/static/src/css/theme.css',
            #'corders/static/src/js/test.js',
        ]
    }

}

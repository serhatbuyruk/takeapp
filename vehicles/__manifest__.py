{
    'name':'vehicles',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Vehicles Management System',
    'sequence': 1,
    'description':'This is vehicles management system software suppored in Odoo',
    'category':'vehicles',
    'website':'https://www.autoronics.com',
    'depends':['base','website','product','corders','contacts'],

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
        'views/vehicles_view.xml',
        'views/vehicles_wizard.xml',
        'views/type_view.xml',
        'views/vehicle_lines_view.xml',
        #'views/skurye_view.xml',
        #'views/inherit_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'vehicles/static/src/css/intlTelInput.css',
            # 'vehicles/static/src/css/jquery-clockpicker.min.css',
            # 'vehicles/static/src/css/style.css',
            # 'vehicles/static/src/js/jquery-clockpicker.min.js',
            # 'vehicles/static/src/js/intlTelInput.min.js',
            # 'vehicles/static/src/js/utils.js',
            # 'vehicles/static/src/js/reservation.js',
            # 'vehicles/static/src/js/script.js',
            #'vehicles/static/src/css/xml_form.css',
            #'vehicles/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            #'vehicles/static/src/js/thunkableWebviewerExtension.js',
            #'vehicles/static/src/css/xml_form.css',
            #'vehicles/static/src/css/theme.css',
            #'vehicles/static/src/js/test.js',
        ]
    }

}

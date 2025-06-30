{
    'name':'realestates',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Real Estates Home Management System',
    'sequence': 1,
    'description':'This is realestates home management system software suppored in Odoo',
    'category':'realestates',
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
        'views/realestates_view.xml',
        #'views/realestates_wizard.xml',
        #'views/inherit_view.xml',
        'views/customerpayment.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'realestates/static/src/css/intlTelInput.css',
            # 'realestates/static/src/css/jquery-clockpicker.min.css',
            # 'realestates/static/src/css/style.css',
            # 'realestates/static/src/js/jquery-clockpicker.min.js',
            # 'realestates/static/src/js/intlTelInput.min.js',
            # 'realestates/static/src/js/utils.js',
            # 'realestates/static/src/js/reservation.js',
            # 'realestates/static/src/js/script.js',
            'realestates/static/src/css/xml_form.css',
            'realestates/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            'realestates/static/src/js/thunkableWebviewerExtension.js',
            'realestates/static/src/css/xml_form.css',
            'realestates/static/src/css/theme.css',
            #'realestates/static/src/js/test.js',
        ]
    }

}

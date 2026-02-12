{
    'name':'slots',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Slots Home Management System',
    'sequence': 1,
    'description':'This is slots home management system software suppored in Odoo',
    'category':'slots',
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
        'views/slots_view.xml',
        'views/slots_wizard.xml',
        'views/skurye_view.xml',
        #'views/inherit_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'slots/static/src/css/intlTelInput.css',
            # 'slots/static/src/css/jquery-clockpicker.min.css',
            # 'slots/static/src/css/style.css',
            # 'slots/static/src/js/jquery-clockpicker.min.js',
            # 'slots/static/src/js/intlTelInput.min.js',
            # 'slots/static/src/js/utils.js',
            # 'slots/static/src/js/reservation.js',
            # 'slots/static/src/js/script.js',
            #'slots/static/src/css/xml_form.css',
            #'slots/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            #'slots/static/src/js/thunkableWebviewerExtension.js',
            #'slots/static/src/css/xml_form.css',
            #'slots/static/src/css/theme.css',
            #'slots/static/src/js/test.js',
        ]
    }

}

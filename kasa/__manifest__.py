{
    'name':'KASA',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'KASA System By Autoronics',
    'sequence': 1,
    'description':'This is KASA API management system software',
    'category':'KASA',
    'website':'https://www.autoronics.com',
    'depends':['base','website'],

    'data':[
        'security/ir.model.access.csv',
        #'security/security.xml',
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
        'views/kasa_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/kasa_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'kasa/static/src/css/intlTelInput.css',
            # 'kasa/static/src/css/jquery-clockpicker.min.css',
            # 'kasa/static/src/css/style.css',
            # 'kasa/static/src/js/jquery-clockpicker.min.js',
            # 'kasa/static/src/js/intlTelInput.min.js',
            # 'kasa/static/src/js/utils.js',
            # 'kasa/static/src/js/reservation.js',
            # 'kasa/static/src/js/script.js',
            'kasa/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            # 'kasa/static/src/js/thunkableWebviewerExtension.js',
            # 'kasa/static/src/css/xml_form.css'
        ]
    }

}

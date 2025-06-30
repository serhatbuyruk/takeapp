{
    'name':'payment_reminder',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'payment_reminder System By Autoronics',
    'sequence': 1,
    'description':'This is payment_reminder API management system software',
    'category':'payment_reminder',
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
        'views/payment_reminder_view.xml',
        'views/customerpayment.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/payment_reminder_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'payment_reminder/static/src/css/intlTelInput.css',
            # 'payment_reminder/static/src/css/jquery-clockpicker.min.css',
            # 'payment_reminder/static/src/css/style.css',
            # 'payment_reminder/static/src/js/jquery-clockpicker.min.js',
            # 'payment_reminder/static/src/js/intlTelInput.min.js',
            # 'payment_reminder/static/src/js/utils.js',
            # 'payment_reminder/static/src/js/reservation.js',
            # 'payment_reminder/static/src/js/script.js',
            'payment_reminder/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            # 'payment_reminder/static/src/js/thunkableWebviewerExtension.js',
            # 'payment_reminder/static/src/css/xml_form.css'
        ]
    }

}

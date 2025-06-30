{
    'name':'Push Notification',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Push Notification System By Autoronics',
    'sequence': 1,
    'description':'This is Push Notification management system software',
    'category':'Push Notification',
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
        'views/push_notification_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/push_notification_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'push_notification/static/src/css/intlTelInput.css',
            # 'push_notification/static/src/css/jquery-clockpicker.min.css',
            # 'push_notification/static/src/css/style.css',
            # 'push_notification/static/src/js/jquery-clockpicker.min.js',
            # 'push_notification/static/src/js/intlTelInput.min.js',
            # 'push_notification/static/src/js/utils.js',
            # 'push_notification/static/src/js/reservation.js',
            # 'push_notification/static/src/js/script.js',
            'push_notification/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            # 'push_notification/static/src/js/thunkableWebviewerExtension.js',
            # 'push_notification/static/src/css/xml_form.css'
        ]
    }

}

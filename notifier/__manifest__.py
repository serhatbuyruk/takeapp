{
    'name':'notifier',
    'version': '16.0.1.8.0',
    'author': 'Autoronics',
    'summary': 'Notifier System By Autoronics',
    'sequence': 1,
    'description':'This is notifier management system software',
    'category':'notifier',
    'website':'https://www.autoronics.com',
    'depends':['base','base_automation','website','corders'],

    'data':[
        'security/ir.model.access.csv',
        'security/manual_security.xml',
        'data/technical_actions.xml',
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
        'views/notifier_view.xml',
        #'views/model_views.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/notifier_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'notifier/static/src/css/intlTelInput.css',
            # 'notifier/static/src/css/jquery-clockpicker.min.css',
            # 'notifier/static/src/css/style.css',
            # 'notifier/static/src/js/jquery-clockpicker.min.js',
            # 'notifier/static/src/js/intlTelInput.min.js',
            # 'notifier/static/src/js/utils.js',
            # 'notifier/static/src/js/reservation.js',
            # 'notifier/static/src/js/script.js',
            'notifier/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            # 'notifier/static/src/js/thunkableWebviewerExtension.js',
            # 'notifier/static/src/css/xml_form.css'
            #'notifier/static/src/js/google_maps_widget.js',
            #'notifier/static/src/css/google_maps_widget.css',
        ],
        'qweb': [
        #'static/src/xml/*.xml',
        ]
    }

}

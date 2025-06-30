{
    'name':'ttsigortaelementer',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'ttsigortaelementer System By Autoronics',
    'sequence': 1,
    'description':'This is ttsigortaelementer API management system software',
    'category':'ttsigortaelementer',
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
        'views/ttsigortaelementer_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/ttsigortaelementer_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'ttsigortaelementer/static/src/css/intlTelInput.css',
            # 'ttsigortaelementer/static/src/css/jquery-clockpicker.min.css',
            # 'ttsigortaelementer/static/src/css/style.css',
            # 'ttsigortaelementer/static/src/js/jquery-clockpicker.min.js',
            # 'ttsigortaelementer/static/src/js/intlTelInput.min.js',
            # 'ttsigortaelementer/static/src/js/utils.js',
            # 'ttsigortaelementer/static/src/js/reservation.js',
            # 'ttsigortaelementer/static/src/js/script.js',
            'ttsigortaelementer/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            # 'ttsigortaelementer/static/src/js/thunkableWebviewerExtension.js',
            # 'ttsigortaelementer/static/src/css/xml_form.css'
        ]
    }

}

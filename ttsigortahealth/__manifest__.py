{
    'name':'ttsigortahealth',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'ttsigortahealth System By Autoronics',
    'sequence': 1,
    'description':'This is ttsigortahealth API management system software',
    'category':'ttsigortahealth',
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
        'views/ttsigortahealth_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/ttsigortahealth_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'ttsigortahealth/static/src/css/intlTelInput.css',
            # 'ttsigortahealth/static/src/css/jquery-clockpicker.min.css',
            # 'ttsigortahealth/static/src/css/style.css',
            # 'ttsigortahealth/static/src/js/jquery-clockpicker.min.js',
            # 'ttsigortahealth/static/src/js/intlTelInput.min.js',
            # 'ttsigortahealth/static/src/js/utils.js',
            # 'ttsigortahealth/static/src/js/reservation.js',
            # 'ttsigortahealth/static/src/js/script.js',
            'ttsigortahealth/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            # 'ttsigortahealth/static/src/js/thunkableWebviewerExtension.js',
            # 'ttsigortahealth/static/src/css/xml_form.css'
        ]
    }

}

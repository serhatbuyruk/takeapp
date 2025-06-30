{
    'name':'ttsigortaindividualretirement',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'ttsigortaindividualretirement System By Autoronics',
    'sequence': 1,
    'description':'This is ttsigortaindividualretirement API management system software',
    'category':'ttsigortaindividualretirement',
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
        'views/ttsigortaindividualretirement_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/ttsigortaindividualretirement_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'ttsigortaindividualretirement/static/src/css/intlTelInput.css',
            # 'ttsigortaindividualretirement/static/src/css/jquery-clockpicker.min.css',
            # 'ttsigortaindividualretirement/static/src/css/style.css',
            # 'ttsigortaindividualretirement/static/src/js/jquery-clockpicker.min.js',
            # 'ttsigortaindividualretirement/static/src/js/intlTelInput.min.js',
            # 'ttsigortaindividualretirement/static/src/js/utils.js',
            # 'ttsigortaindividualretirement/static/src/js/reservation.js',
            # 'ttsigortaindividualretirement/static/src/js/script.js',
            'ttsigortaindividualretirement/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            # 'ttsigortaindividualretirement/static/src/js/thunkableWebviewerExtension.js',
            # 'ttsigortaindividualretirement/static/src/css/xml_form.css'
        ]
    }

}

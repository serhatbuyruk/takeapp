{
    'name':'Satın Alma',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Satın Alma System By Autoronics',
    'sequence': 1,
    'description':'This is Satın Alma API management system software',
    'category':'Satın Alma',
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
        'views/satin_alma_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/html_parser_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'html_parser/static/src/css/intlTelInput.css',
            # 'html_parser/static/src/css/jquery-clockpicker.min.css',
            # 'html_parser/static/src/css/style.css',
            # 'html_parser/static/src/js/jquery-clockpicker.min.js',
            # 'html_parser/static/src/js/intlTelInput.min.js',
            # 'html_parser/static/src/js/utils.js',
            # 'html_parser/static/src/js/reservation.js',
            # 'html_parser/static/src/js/script.js',
            'satin_alma/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            # 'html_parser/static/src/js/thunkableWebviewerExtension.js',
            # 'html_parser/static/src/css/xml_form.css'
        ]
    }

}

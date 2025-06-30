{
    'name':'ttsigorta',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'ttsigorta System By Autoronics',
    'sequence': 1,
    'description':'This is ttsigorta API management system software',
    'category':'ttsigorta',
    'website':'https://www.autoronics.com',
    'depends':['base','website','contacts'],

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
        'views/ttsigorta_view.xml',
        #'views/customerpayment.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/ttsigorta_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'ttsigorta/static/src/css/intlTelInput.css',
            # 'ttsigorta/static/src/css/jquery-clockpicker.min.css',
            # 'ttsigorta/static/src/css/style.css',
            # 'ttsigorta/static/src/js/jquery-clockpicker.min.js',
            # 'ttsigorta/static/src/js/intlTelInput.min.js',
            # 'ttsigorta/static/src/js/utils.js',
            # 'ttsigorta/static/src/js/reservation.js',
            # 'ttsigorta/static/src/js/script.js',
            'ttsigorta/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            # 'ttsigorta/static/src/js/thunkableWebviewerExtension.js',
            # 'ttsigorta/static/src/css/xml_form.css'
        ]
    }

}

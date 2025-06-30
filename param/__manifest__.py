{
    'name':'Param',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Param System By Autoronics',
    'sequence': 1,
    'description':'This is Param API management system software',
    'category':'Param API Modul',
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
        'views/param_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/param_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'param/static/src/css/intlTelInput.css',
            # 'param/static/src/css/jquery-clockpicker.min.css',
            # 'param/static/src/css/style.css',
            # 'param/static/src/js/jquery-clockpicker.min.js',
            # 'param/static/src/js/intlTelInput.min.js',
            # 'param/static/src/js/utils.js',
            # 'param/static/src/js/reservation.js',
            # 'param/static/src/js/script.js',
            'param/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            # 'param/static/src/js/thunkableWebviewerExtension.js',
            # 'param/static/src/css/xml_form.css'
        ]
    }

}

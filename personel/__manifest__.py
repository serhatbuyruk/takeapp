{
    'name':'personel',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Personel Home Management System',
    'sequence': 1,
    'description':'This is personel home management system software suppored in Odoo',
    'category':'personel',
    'website':'https://www.autoronics.com',
    'depends':['base','website'],

    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
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
        'views/personel_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'personel/static/src/css/intlTelInput.css',
            # 'personel/static/src/css/jquery-clockpicker.min.css',
            # 'personel/static/src/css/style.css',
            # 'personel/static/src/js/jquery-clockpicker.min.js',
            # 'personel/static/src/js/intlTelInput.min.js',
            # 'personel/static/src/js/utils.js',
            # 'personel/static/src/js/reservation.js',
            # 'personel/static/src/js/script.js',
            'personel/static/src/css/xml_form.css',
            'personel/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            'personel/static/src/js/thunkableWebviewerExtension.js',
            'personel/static/src/css/xml_form.css'
        ]
    }

}

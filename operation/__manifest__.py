{
    'name':'operation',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Operation Home Management System',
    'sequence': 1,
    'description':'This is operation home management system software suppored in Odoo',
    'category':'operation',
    'website':'https://www.autoronics.com',
    'depends':['base','website','contacts','project'],

    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/box_view.xml',
        'views/stage_view.xml',
        #'views/appointment_view.xml',
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
        'views/operation_view.xml',
        'views/inherit_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'operation/static/src/css/intlTelInput.css',
            # 'operation/static/src/css/jquery-clockpicker.min.css',
            # 'operation/static/src/css/style.css',
            # 'operation/static/src/js/jquery-clockpicker.min.js',
            # 'operation/static/src/js/intlTelInput.min.js',
            # 'operation/static/src/js/utils.js',
            # 'operation/static/src/js/reservation.js',
            # 'operation/static/src/js/script.js',
            'operation/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            'operation/static/src/js/thunkableWebviewerExtension.js',
            'operation/static/src/css/xml_form.css'
        ]
    }

}

{
    'name':'Reports',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Reports Home Management System',
    'sequence': 1,
    'description':'This is reports home management system software suppored in Odoo v15',
    'category':'reports',
    'website':'https://www.autoronics.com',
    'depends':['base','website','devices'],

    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
        #'security/security.xml',
        'views/all_records_list.xml',
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
        'views/reports_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/reports_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'reports/static/src/css/intlTelInput.css',
            # 'reports/static/src/css/jquery-clockpicker.min.css',
            # 'reports/static/src/css/style.css',
            # 'reports/static/src/js/jquery-clockpicker.min.js',
            # 'reports/static/src/js/intlTelInput.min.js',
            # 'reports/static/src/js/utils.js',
            # 'reports/static/src/js/reservation.js',
            # 'reports/static/src/js/script.js'
        ]
    }

}
{
    'name':'hbookings',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Hbookings Home Management System',
    'sequence': 1,
    'description':'This is hbookings home management system software suppored in Odoo',
    'category':'hbookings',
    'website':'https://www.autoronics.com',
    'depends':['base','website','product'],

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
        'views/hbookings_view.xml',
        'views/rooms_view.xml',
        #'views/hbookings_wizard.xml',
        #'views/inherit_view.xml',
        #'views/customerpayment.xml',
        #'views/documents_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'hbookings/static/src/css/intlTelInput.css',
            # 'hbookings/static/src/css/jquery-clockpicker.min.css',
            # 'hbookings/static/src/css/style.css',
            # 'hbookings/static/src/js/jquery-clockpicker.min.js',
            # 'hbookings/static/src/js/intlTelInput.min.js',
            # 'hbookings/static/src/js/utils.js',
            # 'hbookings/static/src/js/reservation.js',
            'hbookings/static/src/css/tabulator_site.min.css',
            'hbookings/static/src/js/tabulator_site.min.js',
            'hbookings/static/src/css/xml_form.css',
            'hbookings/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            'hbookings/static/src/js/thunkableWebviewerExtension.js',
            'hbookings/static/src/css/xml_form.css',
            'hbookings/static/src/css/theme.css',
            #'hbookings/static/src/js/test.js',
        ]
    }

}

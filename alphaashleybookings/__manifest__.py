{
    'name':'alphaashleybookings',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'alphaashleybookings Home Management System',
    'sequence': 1,
    'description':'This is alphaashleybookings home management system software suppored in Odoo',
    'category':'alphaashleybookings',
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
        'views/alphaashleybookings_view.xml',
        #'views/rooms_view.xml',
        #'views/alphaashleybookings_wizard.xml',
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
            # 'alphaashleybookings/static/src/css/intlTelInput.css',
            # 'alphaashleybookings/static/src/css/jquery-clockpicker.min.css',
            # 'alphaashleybookings/static/src/css/style.css',
            # 'alphaashleybookings/static/src/js/jquery-clockpicker.min.js',
            # 'alphaashleybookings/static/src/js/intlTelInput.min.js',
            # 'alphaashleybookings/static/src/js/utils.js',
            # 'alphaashleybookings/static/src/js/reservation.js',
            'alphaashleybookings/static/src/css/tabulator_site.min.css',
            'alphaashleybookings/static/src/js/tabulator_site.min.js',
            'alphaashleybookings/static/src/css/xml_form.css',
            'alphaashleybookings/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            'alphaashleybookings/static/src/js/thunkableWebviewerExtension.js',
            'alphaashleybookings/static/src/css/xml_form.css',
            'alphaashleybookings/static/src/css/theme.css',
            #'alphaashleybookings/static/src/js/test.js',
        ]
    }

}

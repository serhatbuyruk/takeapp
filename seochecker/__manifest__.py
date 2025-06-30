{
    'name':'seochecker',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'seochecker Home Management System',
    'sequence': 1,
    'description':'This is seochecker home management system software suppored in Odoo v15',
    'category':'seochecker',
    'website':'https://www.autoronics.com',
    'depends':['base','website','contacts'],

    'data':[
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
        #'views/harbour.xml',
        #'views/snippets/s_booking_widget.xml',
        #'views/snippets/demo/s_cart_product/s_cart_products.xml',
        #'views/snippets/demo/snippets.xml',
        #'views/languages.xml',
        #'views/notary.xml',
        'views/settings.xml',
        'views/seochecker_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/seochecker_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'seochecker/static/src/css/intlTelInput.css',
            # 'seochecker/static/src/css/jquery-clockpicker.min.css',
            # 'seochecker/static/src/css/style.css',
            # 'seochecker/static/src/js/jquery-clockpicker.min.js',
            # 'seochecker/static/src/js/intlTelInput.min.js',
            # 'seochecker/static/src/js/utils.js',
            # 'seochecker/static/src/js/reservation.js',
            # 'seochecker/static/src/js/script.js',
            'seochecker/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
        'seochecker/static/src/js/thunkableWebviewerExtension.js',
	    'seochecker/static/src/css/theme.css'
        ]
    }

}

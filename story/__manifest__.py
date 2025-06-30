{
    'name':'story',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Story Home Management System',
    'sequence': 1,
    'description':'This is story home management system software suppored in Odoo',
    'category':'story',
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
        'views/story_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'story/static/src/css/intlTelInput.css',
            # 'story/static/src/css/jquery-clockpicker.min.css',
            # 'story/static/src/css/style.css',
            # 'story/static/src/js/jquery-clockpicker.min.js',
            # 'story/static/src/js/intlTelInput.min.js',
            # 'story/static/src/js/utils.js',
            # 'story/static/src/js/reservation.js',
            # 'story/static/src/js/script.js',
            'story/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            'story/static/src/js/thunkableWebviewerExtension.js',
            'story/static/src/css/xml_form.css'
        ]
    }

}

{
    'name':'Task',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Task System By Autoronics',
    'sequence': 1,
    'description':'This is task API management system software',
    'category':'Task',
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
        'views/task_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/task_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'task/static/src/css/intlTelInput.css',
            # 'task/static/src/css/jquery-clockpicker.min.css',
            # 'task/static/src/css/style.css',
            # 'task/static/src/js/jquery-clockpicker.min.js',
            # 'task/static/src/js/intlTelInput.min.js',
            # 'task/static/src/js/utils.js',
            # 'task/static/src/js/reservation.js',
            # 'task/static/src/js/script.js',
            'task/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            # 'task/static/src/js/thunkableWebviewerExtension.js',
            # 'task/static/src/css/xml_form.css'
        ]
    }

}

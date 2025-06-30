{
    'name':'WebStory',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'webstory Home Management System',
    'sequence': 1,
    'description':'This is webstory home management system software suppored in Odoo',
    'category':'webstory',
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
        'views/webstory_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml',
        #'views/story.xml',
       'views/test.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            # 'webstory/static/src/css/intlTelInput.css',
            # 'webstory/static/src/css/jquery-clockpicker.min.css',
            # 'webstory/static/src/css/style.css',
            # 'webstory/static/src/js/jquery-clockpicker.min.js',
            # 'webstory/static/src/js/intlTelInput.min.js',
            # 'webstory/static/src/js/utils.js',
            # 'webstory/static/src/js/reservation.js',
            # 'webstory/static/src/js/script.js',
            'webstory/static/src/js/thunkableWebviewerExtension.js',
            'webstory/static/src/js/story.js',
            'webstory/static/src/css/story.css',
            
        ],
        'web.assets_backend': [
            'webstory/static/src/js/thunkableWebviewerExtension.js',
            'webstory/static/src/css/xml_form.css'
        ]
    }

}

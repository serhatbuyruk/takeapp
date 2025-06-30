{
    'name':'citizenships',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'Citizenships Home Management System',
    'sequence': 1,
    'description':'This is citizenships home management system software suppored in Odoo',
    'category':'citizenships',
    'website':'https://www.autoronics.com',
    'depends':['base','website','product','realestates'],

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
        'views/citizenships_view.xml',
        #'views/citizenships_wizard.xml',
        #'views/inherit_view.xml',
        #'views/customerpayment.xml',
        'views/documents_view.xml',
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'citizenships/static/src/css/intlTelInput.css',
            # 'citizenships/static/src/css/jquery-clockpicker.min.css',
            # 'citizenships/static/src/css/style.css',
            # 'citizenships/static/src/js/jquery-clockpicker.min.js',
            # 'citizenships/static/src/js/intlTelInput.min.js',
            # 'citizenships/static/src/js/utils.js',
            # 'citizenships/static/src/js/reservation.js',
            # 'citizenships/static/src/js/script.js',
            'citizenships/static/src/css/xml_form.css',
            'citizenships/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            'citizenships/static/src/js/thunkableWebviewerExtension.js',
            'citizenships/static/src/css/xml_form.css',
            'citizenships/static/src/css/theme.css',
            #'citizenships/static/src/js/test.js',
        ]
    }

}

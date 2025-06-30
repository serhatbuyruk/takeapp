{
    'name':'kreatif',
    'version': '1.5.19',
    'author': 'Autoronics',
    'summary': 'kreatif Home Management System',
    'sequence': 1,
    'description':'This is kreatif home management system software suppored in Odoo',
    'category':'kreatif',
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
        'views/kreatif_view.xml',
        'views/templates.xml',
        'views/turuncu_product_list_template.xml',
        'views/tum_urunler_varyant_product_template.xml',
        'views/tum_kategoriler_category_template.xml',
        'views/ustkategoriler_template.xml',
        'views/altkategoriler_template.xml',
        'views/kategoriler_hiyerasi_template.xml',
        'views/etkin_promosyon_kategoriler_page.xml',
        'views/etkin_promosyon_urunler_page.xml',
        'views/etkin_promosyon_varyant_urunler_page.xml',
        'views/etkin_promosyon_varyant_urun_detay_page.xml',
     
        # 'views/snippets/s_car_select.xml',
        # 'views/snippets/s_reservation_form.xml',
        # 'reports/links_report_views.xml',
        #'data/antalyahermes.xml'
    ],

    'assets': {
        'web.assets_frontend': [
            # 'kreatif/static/src/css/intlTelInput.css',
            # 'kreatif/static/src/css/jquery-clockpicker.min.css',
            # 'kreatif/static/src/css/style.css',
            # 'kreatif/static/src/js/jquery-clockpicker.min.js',
            # 'kreatif/static/src/js/intlTelInput.min.js',
            # 'kreatif/static/src/js/utils.js',
            # 'kreatif/static/src/js/reservation.js',
            # 'kreatif/static/src/js/script.js',
            'kreatif/static/src/js/thunkableWebviewerExtension.js',
        ],
        'web.assets_backend': [
            'kreatif/static/src/js/thunkableWebviewerExtension.js',
            'kreatif/static/src/css/xml_form.css'
        ]
    }

}

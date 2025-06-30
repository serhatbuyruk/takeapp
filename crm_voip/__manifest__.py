# -*- coding: utf-8 -*-
{
    'name': "CRM VoIP",

    'summary': """VoIP Services""",

    'description': """""",

    'author': "Ertisya",
    'website': "https://www.ertisya.com.",
    'category': 'CRM',
    'version': '0.1',
    'depends': ['base', 'bus', 'mail', 'crm'],
    'data': [
        'security/groups.xml',
        'sms/views/sms_log.xml',
        'sms/views/sms_answer.xml',
        'crm/views/customer.xml',
        'crm/views/customer_phone.xml',
        'crm/views/customer_call.xml',
        'crm/views/customer_source.xml',
        'crm/views/customer_question.xml',
        'crm/views/seller.xml',
        'crm/wizard/create_customer.xml',
        'crm/wizard/send_sms.xml',
        'crm/wizard/crm_call.xml',
        'provider/views/pbx.xml',
        'provider/wizard/fetch_pbx_detail.xml',
        'provider/data/cron.xml',
        'sms/views/sms.xml',
        'sms/views/sms_log.xml',
        'sms/views/sms_answer.xml',
        'menu.xml',
        # 'assets.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_qweb': [
            'crm_voip/static/src/xml/pbx.xml',
            'crm_voip/static/src/xml/mp3_player.xml',
        ],
        'web.assets_backend': [
            'crm_voip/static/src/js/pbx.js',
            'crm_voip/static/src/js/mp3.js',
            'crm_voip/static/src/css/pbx.css',
        ],
    },
    'demo': [

    ]
}

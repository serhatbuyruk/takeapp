from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
import datetime
from datetime import date, datetime, timedelta
from base64 import b64encode
import time
 
cookie = "payment_reminder"
import logging
_logger = logging.getLogger(__name__)

class payment_reminder(models.Model):
    _name = "payment_reminder.profile"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Payment Reminder"

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    sequence = fields.Integer(string="Sequence", default=1)

     
    payment_type = fields.Selection([('personel','Personel'),('individual','Individual'),('corporate','Corporate Payment'), ],
                                    string="Payment Type", default="individual", tracking=True
                                    )
    insurance_selection = fields.Selection([('elementer','Elementer'),('health','Health'),('individual_retirement', 'Individual Retirement')],
                                    string="Insurance Selection", default="individual_retirement", tracking=True
                                    )

    elementer_selection = fields.Selection(
        [
            ('oto', 'Araç Sigortaları'),
            ('konut', 'Konut'),
            ('isyeri', 'İşyeri Sigortası')
        ],
        string="Elementer Sigortalar",
        default=""
    )

    color = fields.Char(string="Color")

    # Araç Sigortaları
    ruhsat = fields.Char(string="Ruhsat")
    phone = fields.Char(string="Telefon")
    plaka = fields.Char(string="Plaka")
    seri_no = fields.Char(string="Seri No")
    marka = fields.Char(string="Marka")
    model = fields.Char(string="Model")

    tc = fields.Char(string="Bina Sahibi TC kimlik")
    adress = fields.Char(string="Açık adress(UluslararasıAVT)")
    daire_metrekare = fields.Char(string="Daire Metre Karesi")
    bina_yas = fields.Integer(string="Bina Yaşı")
    bina_kat_adet = fields.Integer(string="Binan toplam kat adeti")
    bina_kat = fields.Integer(string="Daire Kaçıncı Katta Olduğu")
    raic_bedel = fields.Float(string="Raiç Eşya bedeli")
    kira_mal_sahibi = fields.Selection(
        [
            ('kira', 'Kira'),           
            ('malsahibi', ' Mal sahibi')
        ],
        string="Kira mı Mal sahibi",
        default=""
    )
    ne_is_yapiyor = fields.Char(string="Ne iş yapıyor")
    satmak_istedigi_mal = fields.Char(string="Var ise satmaya sunduğu emtiya mal bedeli")
    demirbas_bedeli = fields.Float(string="Demirbaş Bedeli")
    guvenlik_onlemleri = fields.Char(string="Güvenlik Önlemleri")
    yangin_onlemleri = fields.Char(string="Yangın Önlemleri")
    calisan_sayisi = fields.Integer(string="Çalışan Sayısı")



    person_paid = fields.Many2one('res.partner', string="Person to be Paid",tracking=True)
    partner_id = fields.Many2one('res.partner', string="Customer",tracking=True)
    product_id = fields.Many2one('product.product', string="Product/Service",tracking=True)
    saleperson = fields.Many2one('res.partner', string="Saleperson",tracking=True)
    start_date = fields.Datetime(string="Start Date",tracking=True)
    end_date = fields.Datetime(string="End Date",tracking=True)
    delivery_details = fields.Char(string="Delivery Details", tracking=True)
    days_interval = fields.Integer(string="Days Interval", tracking=True)
 
    contracts_attachment_ids = fields.Many2many('ir.attachment', 'attachment_rel_contracts_payment_reminder', 'pro_id_contracts_payment_reminder', 'attach_id_contracts_payment_reminder', string='Contracts')
    
    #attachment_ids = fields.Many2many('ir.attachment','attachment_rel_realestates','pro_id_realestates','attach_id_realestates', string='Attachments',) 
    
    #partner_ids = fields.Many2many('res.partner', string='Partners')
    #users_can_edit = fields.Many2many('res.users',relation='x_citizenships_profile_res_users_rel', column1='citizenships_users_id',column2='res_users_id', string="Users Can Edit")
    partner_ids = fields.Many2many(
       'res.partner', 
        relation='payment_reminder_res_partner_rel',
        column1='payment_reminder_model_id',
        column2='partner_id',
        string='Contacts'
    )
    repeat_count = fields.Integer(string="Repeat Count", tracking=True)
    repeat_status = fields.Boolean(string="Repeat Status", tracking=True)
    repeat_type = fields.Selection([('once','Once'),('day','Day'),('week','Week'),('Month','Month'),('year','Year')],
                                    string="Repeat Type", default="once", tracking=True
                                    )

    first_payment_date = fields.Datetime(string="First Payment Date", default=fields.Datetime.now, tracking=True)
    next_payment_date = fields.Datetime(string="Next Payment Date",tracking=True)
    last_payment_date = fields.Datetime(string="Last Payment Date",tracking=True)
    sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=32, tracking=True)
    sale_price = fields.Monetary(string="Sale Price", currency_field='sale_price_currency_id', tracking=True)
    deposit_price_currency_id = fields.Many2one('res.currency', string='Deposit Currency',default=32, tracking=True)
    deposit_price = fields.Monetary(string="Deposit Price", currency_field='deposit_price_currency_id', tracking=True)
    sale_description = fields.Char(string="Sale Description", tracking=True)

    received_amount_currency_id = fields.Many2one('res.currency', string='Received Amount Currency',default=32, tracking=True)
    received_amount = fields.Monetary(string="Received Amount", currency_field='received_amount_currency_id', tracking=True)
    received_amount_1 = fields.Monetary(string="Received Amount-1", currency_field='received_amount_currency_id', tracking=True)
    received_amount_2 = fields.Monetary(string="Received Amount-2", currency_field='received_amount_currency_id', tracking=True)
    received_amount_3 = fields.Monetary(string="Received Amount-3", currency_field='received_amount_currency_id', tracking=True)
    received_amount_4 = fields.Monetary(string="Received Amount-4", currency_field='received_amount_currency_id', tracking=True)
    received_amount_5 = fields.Monetary(string="Received Amount-5", currency_field='received_amount_currency_id', tracking=True)
    received_amount_6 = fields.Monetary(string="Received Amount-6", currency_field='received_amount_currency_id', tracking=True)
    received_amount_7 = fields.Monetary(string="Received Amount-7", currency_field='received_amount_currency_id', tracking=True)
    received_amount_8 = fields.Monetary(string="Received Amount-8", currency_field='received_amount_currency_id', tracking=True)
    received_amount_total = fields.Monetary(string="Received Amount Total", currency_field='received_amount_currency_id', tracking=True)
    remaining_amount_currency_id = fields.Many2one('res.currency', string='Remaining Amount Currency',default=32, tracking=True)
    remaining_amount = fields.Monetary(string="Remaining Amount", currency_field='remaining_amount_currency_id', tracking=True)


    customer_payment_status = fields.Selection([('not_paid','Not Paid'),('in_payment','In Payment'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
                                    string="Customer Payment Status ", default="not_paid", tracking=True
                                    )
    

    amount_due = fields.Float(string='Amount Due', required=True)
    due_date = fields.Date(string='Due Date', required=True)

    
    @api.model
    def get_payments_for_week(self):
        today = fields.Date.context_today(self)
        next_week = today + timedelta(days=7)
        payments = self.search([('due_date', '>=', today), ('due_date', '<=', next_week)])
        return payments

    @api.model
    def send_Sms(self,usercode,password,msgheader,gsmno,message):

        url = 'https://api.netgsm.com.tr/sms/send/get?usercode='+ usercode + '&password=' + password + '&msgheader=' + msgheader + '&gsmno=' + gsmno + '&message=' + message
        x = requests.get(url)
        """ notifer = self.env['push_notification.profile'].sudo().create({
                    'name': "SMS: " + str(gsmno) + " => " + str(message)
                }) """
        #_logger.info("\nSMS: " + str(x.text) + " - " + str(x.status_code) + "\n")
        return str(x.status_code) + " " + str(x.text)
        #-------------------------------------------------------------------
    
    @api.model
    def send_Push_Notification_With_Playerid(self,auth_key,app_id,player_ids,message):
                 
        _logger = logging.getLogger(__name__)
        header = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {auth_key}',
                'Connection': "keep-alive",
                  }
        payload = {
                    "app_id": app_id,
                    "include_subscription_ids": player_ids,
                    #"headings": {"en": "Notification Title"},
                    "contents": {
                        "en": message
                    }
                }
        payload_json = json.dumps(payload)
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=payload_json)
        print(req.status_code, req.reason)
        _logger.info("\n" + str(auth_key) + " " + str(app_id) + " " + str(player_ids) + " " + str(message) + str(req.text) + str(req.status_code) + str(req.reason) + "\n")
        return True

    @api.model
    def send_payment_reminders(self):
        today = fields.Date.today()
        reminders = self.search([('due_date', '=', today)])
        for reminder in reminders:
            template_id = self.env.ref('payment_reminder.email_template_payment_reminder').id
            self.env['mail.template'].browse(template_id).send_mail(reminder.id, force_send=True)

    @api.onchange('deposit_price')
    def deposite_price_calculation(self):
        self["remaining_amount"] = self.sale_price - self.received_amount - self.received_amount_1 - self.received_amount_2 - self.received_amount_3 - self.received_amount_4 - self.received_amount_5 - self.received_amount_6 - self.received_amount_7 - self.deposit_price
        self["received_amount_total"] = self.received_amount + self.received_amount_1 + self.received_amount_2 + self.received_amount_3 + self.received_amount_4 + self.received_amount_5 + self.received_amount_6 + self.received_amount_7
        if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
            self["customer_payment_status"] = "paid"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
            self["customer_payment_status"] = "partial"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
            self["customer_payment_status"] = "not_paid"

    @api.onchange('end_date')
    def end_date_calculation(self):
        if self.end_date != False and self.start_date != False:
            self["days_interval"] = int((self.end_date - self.start_date).days)

    def from_profile(self):
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'realestates.profile',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]'
        }






    


 


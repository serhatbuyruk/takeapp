from odoo import tools, fields, models, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime, timedelta
from base64 import b64encode

cookie = "carwash"
import math
import time


class carwashProfile(models.Model):
    _name = "carwash.profile"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", tracking=True)
    card_id = fields.Char(string="Card Id")
    sequence = fields.Integer(string="Sequence", default=1)
    # sequence = fields.Selection([('1','1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20')],
    #                                string="Sequence", default="1"
    #                                )
    # link_type = fields.Selection([('1','Mobile'),('2', 'Phone'),('3', 'Location'),('4', 'Whatsapp'),('5', 'Instagram')],
    #                                string="Title", default="1"
    #                                )
    visibility = fields.Boolean(string="Visibility", default=True)
    users_can_edit = fields.Many2many(
        'res.users',
        relation='x_carwash_profile_res_users_rel',
        column1='carwash_users_id',
        column2='res_users_id',
        string="Users Can Edit",
    )
    card_owner = fields.Many2one('res.partner', string="Card Owner")
    carwash_image = fields.Binary(string="Image")
    color = fields.Integer(string="Color")

    product_id = fields.Many2many('product.product', string="Product/Service", tracking=True)
    product_status = fields.Selection(
        [('available', 'Available'), ('busy', 'Busy')], string="Product Status", default="available"
    )
    partner_id = fields.Many2one('res.partner', string="Customer", tracking=True)
    delivery_details = fields.Char(string="Delivery Details", tracking=True)
    start_date = fields.Datetime(string="Start Date", default=datetime.now(), tracking=True)
    end_date = fields.Datetime(string="End Date", tracking=True)
    job_start_date = fields.Datetime(string="Job Start Date", tracking=True)
    job_end_date = fields.Datetime(string="Job End Date", tracking=True)
    job_process_time = fields.Float(string="Job Process Time", tracking=True)
    days_interval = fields.Integer(string="Days Interval", tracking=True)
    turkey_entrance_datetime = fields.Datetime(string="Turkey Entrance", tracking=True)
    saleperson = fields.Many2one('res.partner', string="Saleperson", tracking=True)
    dealer = fields.Many2one('res.partner', string="Dealer", tracking=True)
    driver_status = fields.Boolean(string="Driver Status", tracking=True)
    driver = fields.Many2one('res.partner', string="Driver", tracking=True)
    car_petrol_status = fields.Selection(
        [('1', '1/4'), ('2', '2/4'), ('3', '3/4'), ('4', '4/4')],
        string="Car Petrol Status",
        default="4",
        tracking=True,
    )
    job_status = fields.Selection(
        [('waiting', 'Waiting'), ('on_process', 'On Process'), ('finished', 'Finished'), ('canceled', 'Canceled')],
        string="Job Status",
        default="waiting",
        tracking=True,
    )
    contracts_attachment_ids = fields.Many2many(
        'ir.attachment',
        'attachment_rel_contracts',
        'pro_id_contracts',
        'attach_id_contracts',
        string='Contracts',
    )

    repeat_count = fields.Integer(string="Repeat Count", tracking=True)
    repeat_status = fields.Boolean(string="Repeat Status", tracking=True)
    repeat_type = fields.Selection(
        [('once', 'Once'), ('day', 'Day'), ('week', 'Week'), ('Month', 'Month'), ('year', 'Year')],
        string="Repeat Type",
        default="once",
        tracking=True,
    )
    sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency', default=32, tracking=True)
    sale_price = fields.Monetary(string="Sale Price", currency_field='sale_price_currency_id', tracking=True)
    auto_update_price = fields.Boolean(string="Auto Update Price", default=True)
    deposit_price_currency_id = fields.Many2one(
        'res.currency', string='Deposit Currency', default=32, tracking=True
    )
    deposit_price = fields.Monetary(
        string="Deposit Price", currency_field='deposit_price_currency_id', tracking=True
    )
    sale_description = fields.Char(string="Sale Description", tracking=True)
    received_amount_currency_id = fields.Many2one(
        'res.currency', string='Received Amount Currency', default=32, tracking=True
    )
    received_amount = fields.Monetary(
        string="Received Amount", currency_field='received_amount_currency_id', tracking=True
    )
    received_amount_1 = fields.Monetary(
        string="Received Amount-1", currency_field='received_amount_currency_id', tracking=True
    )
    received_amount_2 = fields.Monetary(
        string="Received Amount-2", currency_field='received_amount_currency_id', tracking=True
    )
    received_amount_3 = fields.Monetary(
        string="Received Amount-3", currency_field='received_amount_currency_id', tracking=True
    )
    received_amount_4 = fields.Monetary(
        string="Received Amount-4", currency_field='received_amount_currency_id', tracking=True
    )
    received_amount_5 = fields.Monetary(
        string="Received Amount-5", currency_field='received_amount_currency_id', tracking=True
    )
    received_amount_6 = fields.Monetary(
        string="Received Amount-6", currency_field='received_amount_currency_id', tracking=True
    )
    received_amount_7 = fields.Monetary(
        string="Received Amount-7", currency_field='received_amount_currency_id', tracking=True
    )
    received_amount_8 = fields.Monetary(
        string="Received Amount-8", currency_field='received_amount_currency_id', tracking=True
    )
    received_amount_total = fields.Monetary(
        string="Received Amount Total", currency_field='received_amount_currency_id', tracking=True
    )
    remaining_amount_currency_id = fields.Many2one(
        'res.currency', string='Remaining Amount Currency', default=32, tracking=True
    )
    remaining_amount = fields.Monetary(
        string="Remaining Amount", currency_field='remaining_amount_currency_id', tracking=True
    )
    commission_rate = fields.Float(string="Commission Rate", tracking=True)
    commission_amount_currency_id = fields.Many2one(
        'res.currency', string='Commission Currency %', default=32, tracking=True
    )
    commission_amount = fields.Monetary(
        string="Commission Amount", currency_field='commission_amount_currency_id', tracking=True
    )
    customer_payment_status = fields.Selection(
        [
            ('not_paid', 'Not Paid'),
            ('in_payment', 'In Payment'),
            ('paid', 'Paid'),
            ('partial', 'Partial'),
            ('reversed', 'Reversed'),
            ('invoicing_legacy', 'Invoicing App Legacy'),
        ],
        string="Customer Payment Status ",
        default="not_paid",
        tracking=True,
    )
    invoice_status = fields.Selection(
        [('draft', 'Draft'), ('posted', 'Posted'), ('canceled', 'Canceled')],
        string="Customer Invoice Status ",
        default="draft",
        tracking=True,
    )
    sale_payment_receiver = fields.Many2one('res.partner', string="Payment Receiver", tracking=True)
    sale_payment_type = fields.Selection(
        [('bank', 'Bank'), ('cash', 'Cash')], string="Payment Type", default="cash", tracking=True
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'attachment_rel_1',
        'pro_id_1',
        'attach_id_1',
        string='Attachments',
    )

    scan_date = fields.Datetime(string="Scan Date")
    entry_date = fields.Datetime(string="Entry Date")
    exit_date = fields.Datetime(string="Exit Date")

    email = fields.Char(string="Email")
    tc = fields.Char(string="TC")
    mobile = fields.Char(string="Mobile")
    company_id = fields.Many2one('res.company', string="Company")
    parent_id = fields.Many2one('res.partner', string="Related Company")
    scan_type = fields.Selection(
        [('entry', 'Entry'), ('exit', 'Exit'), ('mola', 'Mola')], string="Scan Type ", default=""
    )
    lat = fields.Float(string="Latitude", digits=(12, 6))
    lng = fields.Float(string="Longitude", digits=(12, 6))
    working_hours = fields.Float(string="Working Hours")
    working_minutes = fields.Integer(string="Working Minutes")
    distance = fields.Integer(string="Distance")
    suspect_level = fields.Integer(string="Suspect Level")
    suspect_level_entry = fields.Integer(string="Suspect Level Entry")
    suspect_level_exit = fields.Integer(string="Suspect Level Exit")

    contact_name = fields.Char(string="Contact Name")
    company_name = fields.Char(string="Company Name")
    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', string="Country")

    license_plate = fields.Char(string="License Plate")
    should_send_msg = fields.Boolean(string="Send Message?")
    car_model = fields.Char(string="Car Model")
    car_brand = fields.Char(string="Car Brand")
    phone = fields.Char(string="Mobile Phone")
    price = fields.Float(string="Price", compute="_compute_price")
    discount = fields.Integer(string="Discount")
    in_process = fields.Boolean(string="In Process")
    car_image = fields.Binary(string="Image", stored=True, attachment=True)
    payment_type = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_1 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_2 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_3 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_4 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_5 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_6 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )
    payment_type_7 = fields.Selection(
        [('cash', 'Cash'), ('credit', 'Credit Card'), ('transfer', 'Transfer')],
        string="Payment Type",
    )

    total_cash = fields.Monetary(string="Total Cash", currency_field='sale_price_currency_id', tracking=True)
    total_credit_card = fields.Monetary(
        string="Total Credit Card", currency_field='sale_price_currency_id', tracking=True
    )
    total_transfer = fields.Monetary(
        string="Total Transfer", currency_field='sale_price_currency_id', tracking=True
    )

    # Buttons
    def cancel_action(self):
        pass

    def show_details(self):
        pass

    def close_action(self):
        self.unlink()

    def call(self):
        pass

    def print(self):
        pass

    @api.depends('product_id')
    def _compute_price(self):
        for record in self:
            record.price = sum(product.list_price for product in record.product_id)

    @api.onchange('product_id', 'auto_update_price')
    def _onchange_product_id(self):
        for record in self:
            if record.auto_update_price:
                record.sale_price = record.price
            self._calculate_amounts()

    @api.onchange(
        'sale_price',
        'discount',
        'received_amount',
        'received_amount_1',
        'received_amount_2',
        'received_amount_3',
        'received_amount_4',
        'received_amount_5',
        'received_amount_6',
        'received_amount_7',
    )
    def _onchange_sale_price(self):
        if self.sale_price != self.price:
            self.auto_update_price = False
        self._calculate_amounts()

    def _calculate_amounts(self):
        self.remaining_amount = (
            self.sale_price
            - self.discount
            - self.received_amount
            - self.received_amount_1
            - self.received_amount_2
            - self.received_amount_3
            - self.received_amount_4
            - self.received_amount_5
            - self.received_amount_6
            - self.received_amount_7
        )
        self.received_amount_total = (
            self.received_amount
            + self.received_amount_1
            + self.received_amount_2
            + self.received_amount_3
            + self.received_amount_4
            + self.received_amount_5
            + self.received_amount_6
            + self.received_amount_7
        )
        if self.sale_price > 0:
            if self.remaining_amount == 0 and self.received_amount > 0:
                self.customer_payment_status = "paid"
            elif self.remaining_amount > 0 and self.received_amount > 0:
                self.customer_payment_status = "partial"
            elif self.remaining_amount > 0 and self.received_amount == 0:
                self.customer_payment_status = "not_paid"

    def open_to_form_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Form View',
            'view_mode': 'form',
            'res_model': 'carwash.profile',
            'res_id': self.id,
            'target': 'new',  # Use 'current' if you don't want a popup (default -> new)
        }

    @api.onchange('license_plate', 'car_brand', 'car_model', 'discount', 'mobile')
    def apply_to_customer(self):
        customer = self.env["res.partner"].sudo().search([("id", "=", self.partner_id.id)], limit=1)
        customer.sudo().write(
            {
                "license_plate": self.license_plate,
                "car_brand": self.car_brand,
                "car_model": self.car_model,
                "discount": self.discount,
                "mobile": self.mobile,
            }
        )

    @api.onchange('partner_id')
    def apply_to_carwash_entry(self):
        customer = self.env["res.partner"].sudo().search([("id", "=", self.partner_id.id)], limit=1)
        self.sudo().write(
            {
                "license_plate": customer.license_plate,
                "car_brand": customer.car_brand,
                "car_model": customer.car_model,
                #"discount": customer.discount,
                "mobile": customer.mobile,
            }
        )

    @api.onchange('discount')
    def discount_calculate(self):
        self["remaining_amount"] = (
            self.sale_price
            - self.discount
            - self.received_amount
            - self.received_amount_1
            - self.received_amount_2
            - self.received_amount_3
            - self.received_amount_4
            - self.received_amount_5
            - self.received_amount_6
            - self.received_amount_7
        )
        self["received_amount_total"] = (
            self.received_amount
            + self.received_amount_1
            + self.received_amount_2
            + self.received_amount_3
            + self.received_amount_4
            + self.received_amount_5
            + self.received_amount_6
            + self.received_amount_7
        )
        if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
            self["customer_payment_status"] = "paid"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
            self["customer_payment_status"] = "partial"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
            self["customer_payment_status"] = "not_paid"

    @api.onchange(
        'received_amount',
        'received_amount_1',
        'received_amount_2',
        'received_amount_3',
        'received_amount_4',
        'received_amount_5',
        'received_amount_6',
        'received_amount_7',
    )
    def received_amount_calculation(self):
        self["remaining_amount"] = (
            self.sale_price
            - self.discount
            - self.received_amount
            - self.received_amount_1
            - self.received_amount_2
            - self.received_amount_3
            - self.received_amount_4
            - self.received_amount_5
            - self.received_amount_6
            - self.received_amount_7
        )
        self["received_amount_total"] = (
            self.received_amount
            + self.received_amount_1
            + self.received_amount_2
            + self.received_amount_3
            + self.received_amount_4
            + self.received_amount_5
            + self.received_amount_6
            + self.received_amount_7
        )
        if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
            self["customer_payment_status"] = "paid"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
            self["customer_payment_status"] = "partial"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
            self["customer_payment_status"] = "not_paid"
        # return {
        #         'warning': {
        #             'title': "Ödeme Başarılı!",
        #             'message': str(self.received_amount) + str(self.received_amount_currency_id.name) + " Tutarında Ödeme Alındı. Kalan Tutar: " + str(self.remaining_amount) + str(self.remaining_amount_currency_id.name),
        #         }
        #     }

    @api.onchange('deposit_price')
    def deposite_price_calculation(self):
        self["remaining_amount"] = (
            self.sale_price
            - self.discount
            - self.received_amount
            - self.received_amount_1
            - self.received_amount_2
            - self.received_amount_3
            - self.received_amount_4
            - self.received_amount_5
            - self.received_amount_6
            - self.received_amount_7
        )
        self["received_amount_total"] = (
            self.received_amount
            + self.received_amount_1
            + self.received_amount_2
            + self.received_amount_3
            + self.received_amount_4
            + self.received_amount_5
            + self.received_amount_6
            + self.received_amount_7
        )
        if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
            self["customer_payment_status"] = "paid"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
            self["customer_payment_status"] = "partial"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
            self["customer_payment_status"] = "not_paid"
        # if self.deposit_price > 0:
        #    self["sale_description"] = self.sale_description + str(datetime.now().strftime("%d-%m-%Y %H:%M")) + " tarihinde " + str(self.deposit_price) + " " + str(self.deposit_price_currency_id.name) + " ödeme alındı.\n"
        # return {
        #         'warning': {
        #             'title': "Deposit Ödemesi Başarılı!",
        #             'message': str(self.deposit_price) + str(self.deposit_price_currency_id.name) + " Tutarında Ödeme Alındı. Kalan Tutar: " + str(self.remaining_amount) + str(self.remaining_amount_currency_id.name),
        #         }
        #     }

    @api.onchange('turkey_entrance_datetime')
    def turkey_entrance_datetime_calculation(self):
        if datetime.today() and self.turkey_entrance_datetime:
            return {
                'warning': {
                    'title': "Ehliyet Kullanım Tarihi Hesaplandı!",
                    'message': str(180 - (datetime.today() - self.turkey_entrance_datetime).days)
                    + " Gün Sonra Ehliyetin Kullanım Süresi Bitecektir.",
                }
            }

    @api.onchange('start_date')
    def start_date_calculation(self):
        if self.start_date != False:
            self["end_date"] = self.start_date + timedelta(minutes=45)
            # return {
            #         'warning': {
            #             'title': "Ehliyet Kullanım Tarihi Hesaplandı!",
            #             'message': str((self.end_date - self.start_date).days) + " Gün Hesaplanmıştır.",
            #         }
            #     }

    @api.onchange('end_date')
    def end_date_calculation(self):
        if self.end_date != False and self.start_date != False:
            self["days_interval"] = int((self.end_date - self.start_date).days)
            # return {
            #         'warning': {
            #             'title': "Ehliyet Kullanım Tarihi Hesaplandı!",
            #             'message': str((self.end_date - self.start_date).days) + " Gün Hesaplanmıştır.",
            #         }
            #     }

    @api.onchange('commission_rate')
    def commission_calculation(self):
        self["commission_amount"] = (self.sale_price - self.discount) * self.commission_rate / 100

    @api.model
    def time_sleep(self):
        time.sleep(6000000)
        return True

    def see_profile(self):
        if len(self.card_id) > 4:
            return {
                'name': 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url': ("/nfc/profile/" + str(self.card_id)),
            }
        if len(self.card_id) == 4:
            return {
                'name': 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url': ("/panel/touch/" + str(self.card_id)),
            }

    @api.model
    def find_distance(self, lat1, lon1, lat2, lon2):
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        # Radius of the Earth in meters
        R = 6371000  # meters
        distance = R * c
        return distance

    def from_profile(self):
        return {
            'name': _("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'carwash.profile',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
        }
        # return { 'name': 'Go to Form Profile',
        #         'res_model': 'ir.actions.act_url',
        #         'type': 'ir.actions.act_url',
        #         'target' : 'self',
        #         'url': ("/web/#id=" + str(119) + "&menu_id=284&action=390&model=carwash.profile&view_type=form/")
        #        }

    # @api.onchange('device_status','device_status_1','device_status_2','device_status_3','device_status_4','device_status_5')
    # def _get_partner(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     for rec in self:
    #         rec.last_action_user = partner.id

    # def write_Link_Status_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_Passive(self):
    #     if self.device_update == False:
    #         pet = self.env['pets.profile'].sudo().search([["device_id.id","=",self.id]],limit=1)
    #         reports_number = 0
    #         reports = self.env['reports.profile'].search(["&","&","&",["device_id.id","=",self.id],["ademco_id","ilike","E602"],["date",">",pet.registration_date],["date","<",datetime.now()]])
    #         temperature_average = 0
    #         temperature_max = 0
    #         temperature_min = 0
    #         humidity_average = 0
    #         humidity_max = 0
    #         humidity_min = 0
    #         oxygen_average = 0
    #         oxygen_max = 0
    #         oxygen_min = 0
    #         bpm_average = 0
    #         bpm_max = 0
    #         bpm_min = 0
    #         if len(reports) > 0:
    #             reports_number = len(reports)
    #             temperature_average = sum(reports.mapped("sensor_1_value")) / reports_number
    #             temperature_max = max(reports.mapped("sensor_1_value"))
    #             temperature_min = min(reports.mapped("sensor_1_value"))
    #             humidity_average = sum(reports.mapped("sensor_2_value")) / reports_number
    #             humidity_max = max(reports.mapped("sensor_2_value"))
    #             humidity_min = min(reports.mapped("sensor_2_value"))
    #             oxygen_average = sum(reports.mapped("sensor_3_value")) / reports_number
    #             oxygen_max = max(reports.mapped("sensor_3_value"))
    #             oxygen_min = min(reports.mapped("sensor_3_value"))
    #             bpm_average = sum(reports.mapped("sensor_4_value")) / reports_number
    #             bpm_max = max(reports.mapped("sensor_4_value"))
    #             bpm_min = min(reports.mapped("sensor_4_value"))
    #         pet['exit_date'] = datetime.now()
    #         pet['temperature'] = 0
    #         pet['device_id'] = False
    #         pet['values_calculation'] = ("*Süreç Boyunca " + str(round(reports_number,2)) + " Adet Rapor Değerlendirildi. \n*Kabin İçinde Minimum Sıcaklık: " + str(round(temperature_min,2)) +  " Maksimum Sıcaklık: " + str(round(temperature_max,2)) + " Ortalama Sıcaklık : " + str(round(temperature_average,2))
    #         + " Olarak Değişti. \n*Kabin İçinde Minimum Nem Oranı: %" + str(round(humidity_min,2)) +  " Maksimum Oksijen Oranı: %" + str(round(humidity_max,2)) + " Ortalama Oksijen Oranı : %" + str(round(humidity_average,2)) + " Olarak Değişti. \n*Kabin İçinde Minimum Oksijen Oranı: %" + str(round(oxygen_min,2)) +  " Maksimum Oksijen Oranı: %" + str(round(oxygen_max,2)) + " Ortalama Oksijen Oranı : %" + str(round(oxygen_average,2))
    #         + " Olarak Değişti. \n*Hasta Kalp Atışı; Minimum Bpm: " + str(round(bpm_min,2)) +  " Maksimum Bpm: " + str(round(bpm_max,2)) + " Ortalama Bpm: " + str(round(bpm_average,2)) + " Olarak Değişti.")
    #         self.write({'device_status': 'passive'})
    #         self.write({'device_update': True})
    #         self.write({'pet_id': False})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_Home(self):
    #     if self.device_update == False:
    #         self.write({'device_status': 'home'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_1_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_1': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_1_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_1': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_2_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_2': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_2_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_2': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_3_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_3': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_3_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_3': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_4_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_4': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_4_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_4': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_5_Active(self):
    #     if self.device_update == False:
    #         self.write({'device_status_5': 'active'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def write_Link_Status_5_Passive(self):
    #     if self.device_update == False:
    #         self.write({'device_status_5': 'passive'})
    #         self.write({'device_update': True})
    #         partner = self.env['res.users'].browse(self.env.uid).partner_id
    #         for rec in self:
    #             rec.last_action_user = partner.id
    #     else:
    #         raise ValidationError("Cihaz Son Yaptığınız Ayarları Henüz Almadı. 1 Dakika Sonra Tekrar Deneyiniz.")

    # def create_emergency_report(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     user_name = "Belirlenemeyen"
    #     for rec in self:
    #         user_name = partner.name
    #     self.env['reports.profile'].sudo().create({
    #         'name': user_name + " Adlı kullanıcı Acil Durum Çağrısında Bulundu.",
    #         'ademco_id': "B001-000"
    #         })
    # def create_ambulance_report(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     user_name = "Belirlenemeyen"
    #     for rec in self:
    #         user_name = partner.name
    #     self.env['reports.profile'].sudo().create({
    #         'name': user_name + " Adlı kullanıcı Ambulans Çağrısında Bulundu.",
    #         'ademco_id': "B002-000"
    #         })
    # def create_fire_report(self):
    #     partner = self.env['res.users'].browse(self.env.uid).partner_id
    #     user_name = "Belirlenemeyen"
    #     for rec in self:
    #         user_name = partner.name
    #     self.env['reports.profile'].sudo().create({
    #         'name': user_name + " Adlı kullanıcı Yangın Çağrısında Bulundu.",
    #         'ademco_id': "B003-000"
    #         })


# discount_percentage = fields.Float("Discount Percentage")

# gender = fields.Selection([('male','Male'),('female', 'Female'),('other', 'Other'),],string="Gender")
# type_of_person = fields.Selection([('adult','Adult'),('child', 'Child'),('baby', 'Baby'),('driver', 'Driver')],string="Person Type")

# How to OverRide Create Method Of a Model
# https://www.youtube.com/watch?v=AS08H3G9x1U&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=26

# @api.model
# def create(self, vals_list):
#    res = super(ResPartners, self).create(vals_list)
#    print("yes working")
#    # do the custom coding here
#    return res

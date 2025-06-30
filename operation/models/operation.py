from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
cookie = "operation"
import random
import string

class operationProfile(models.Model):
    _name = "operation.profile"

    name = fields.Char(string="Name", default="Kart Ayarları")
    card_id = fields.Char(string="Card Id")
    sequence = fields.Integer(string="Sequence", default=1)
    # sequence = fields.Selection([('1','1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20')],
    #                                string="Sequence", default="1"
    #                                )
    # link_type = fields.Selection([('1','Mobile'),('2', 'Phone'),('3', 'Location'),('4', 'Whatsapp'),('5', 'Instagram')],
    #                                string="Title", default="1"
    #                                )
    visibility = fields.Boolean(string="Visibility", default=True)
    users_can_edit = fields.Many2many('res.users',relation='x_operation_profile_res_users_rel', column1='operation_users_id',column2='res_users_id', string="Users Can Edit")
    card_owner = fields.Many2one('res.partner', string="Card Owner")
    operation_image = fields.Binary(string="Image")
    color = fields.Integer(string="Color")
    scan_date = fields.Datetime(string="Scan Date")
    entry_date = fields.Datetime(string="Entry Date")
    exit_date = fields.Datetime(string="Exit Date")
    partner_id = fields.Many2one('res.partner', string="Operation")
    email = fields.Char(string="Email")
    tc = fields.Char(string="TC")
    mobile = fields.Char(string="Mobile")
    company_id = fields.Many2one('res.company', string="Company")
    parent_id = fields.Many2one('res.partner', string="Related Company")
    scan_type = fields.Selection([('entry','Entry'),('exit','Exit'),('mola','Mola')],
                                    string="Scan Type ", default=""
                                    )
    lat = fields.Float(string="Latitude", digits=(12, 6))
    lng = fields.Float(string="Longitude", digits=(12, 6))
    working_hours = fields.Float(string="Working Hours")
    working_minutes = fields.Integer(string="Working Minutes")
    distance = fields.Integer(string="Distance")
    suspect_level = fields.Integer(string="Suspect Level")

    contact_name = fields.Char(string="Contact Name")
    company_name = fields.Char(string="Company Name")
    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', string="Country")

    def see_profile(self):
        if len(self.card_id) > 4:
            return { 'name': 'Go to website',
                    'res_model': 'ir.actions.act_url',
                    'type': 'ir.actions.act_url',
                    'target' : 'self',
                    'url': ("/nfc/profile/" + str(self.card_id))
                }
        if len(self.card_id) == 4:
            return { 'name': 'Go to website',
                    'res_model': 'ir.actions.act_url',
                    'type': 'ir.actions.act_url',
                    'target' : 'self',
                    'url': ("/panel/touch/" + str(self.card_id))
                }
    
    def from_profile(self):
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'operation.profile',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]'
        }
        # return { 'name': 'Go to Form Profile',
        #         'res_model': 'ir.actions.act_url',
        #         'type': 'ir.actions.act_url',
        #         'target' : 'self',
        #         'url': ("/web/#id=" + str(119) + "&menu_id=284&action=390&model=operation.profile&view_type=form/")
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
        

                              
class ResPartnersInherit(models.Model):
    _inherit = 'res.partner'

    passport_no = fields.Char(string="Passport No", tracking=True)
    passport_attachment = fields.Many2many('ir.attachment','attachment_rel_2','pro_id_2','attach_id_2', string='Passport Attachments', tracking=True)
    lat = fields.Float(string="Latitude", digits=(12, 6))
    lng = fields.Float(string="Longitude", digits=(12, 6))
    
    @api.onchange('first_sale_price','sale_price')
    def check_field_warning(self):
        message = ""
        if not self.passport_no:
            message += "Hasta notu, "

class ProjectTaskInherit(models.Model):
    _inherit = 'project.task'

    stage_of_visit = fields.Many2one('stage.app', string="Stage", context="{'order_display': 'sequence asc' }", tracking=True)
    patient_type = fields.Selection([('local','Local'),('foreign','Foreign')],
                                    string="Patient Type", default="foreign", tracking=True)
    patient_note = fields.Char(string="Hasta Notu ", tracking=True)
    patient_medications = fields.Char(string="Hastanın Kullandığı İlaçlar", tracking=True)
    patient_chronic_disease = fields.Char(string="Varsa Kronik Hastalık", tracking=True)
    
    sale_person = fields.Many2one('res.partner', string="Sale Person", tracking=True)
    patient_coach = fields.Many2one('res.partner', string="Patient Coach", tracking=True)
    driver = fields.Many2one('res.partner', string="Driver", tracking=True)
    
    patient_status = fields.Selection([('begin','Gelecek Hasta'),('continue','Devam Eden Hasta'),('finish','Biten Hasta')],
                                    string="Durum Aşaması", default="", tracking=True)
    #refekat edenler
    refakat = fields.Char(string="Refakatçi kişiler", tracking=True)
    source = fields.Many2one('utm.source', string="Source", tracking=True)
    visit = fields.Selection([('1','1.Visit'),('2','2.Visit'),('3','3.Visit'),('4','4.Visit'),('5','5.Visit')],
                                    string="Visit", default="1", tracking=True)
    planned_visit = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5')],
                                    string="Planned Visit", default="1", tracking=True)
    ticket_purchase_date = fields.Date(string="Inbound Ticket Purchase Date", tracking=True)
    fligth_company = fields.Char(string="Inbound Fligth Company", tracking=True)
    fligth_number = fields.Char(string="Inbound Fligth Number", tracking=True)
    ticket_attachments = fields.Many2many('ir.attachment','attachment_rel_1','pro_id_1','attach_id_1', string='Inbound Ticket Attachments', tracking=True)
    arrival_datetime = fields.Datetime(string="Inbound Arrival Date And Time", tracking=True)
    gelen_hasta_status = fields.Boolean("Gelecek Hasta Durumu", tracking=True)
    departure_datetime = fields.Datetime(string="Outbound Departure Date And Time", tracking=True)
    hotel = fields.Char(string="Hotel", tracking=True)
    
    # Giden Uçak Bilgileri
    outgoing_ticket_purchase_date = fields.Date(string="Outbound Ticket Purchase Date", tracking=True)
    outgoing_fligth_company = fields.Char(string="Outbound Fligth Company", tracking=True)
    outgoing_fligth_number = fields.Char(string="Outbound Fligth Number", tracking=True)
    outgoing_ticket_attachments = fields.Many2many('ir.attachment','attachment_rel_1','pro_id_1','attach_id_1', string='Outbound Ticket Attachments', tracking=True)
    outgoing_arrival_datetime = fields.Datetime(string="Outbound Arrival Date And Time", tracking=True)   
    giden_hasta_status = fields.Boolean("Gidecek Hasta Durumu", tracking=True)
    
    
    sistem_atama_status = fields.Boolean("Sistem Atama Durumu", tracking=True)
    
    
    sale_price_currency_id = fields.Many2one('res.currency', string='Sale Currency',default=32, tracking=True)
    sale_price = fields.Monetary(string="Sale Price", currency_field='sale_price_currency_id', tracking=True)
    first_sale_price = fields.Monetary(string="First Sales", currency_field='sale_price_currency_id', tracking=True)
    deposit_price_currency_id = fields.Many2one('res.currency', string='Deposit Currency',default=32, tracking=True)
    deposit_price = fields.Monetary(string="Deposit Price", currency_field='deposit_price_currency_id', tracking=True)
    sale_description = fields.Char(string="Sale Description", tracking=True)
    received_amount_currency_id = fields.Many2one('res.currency', string='Received Amount Currency',default=32, tracking=True)
    received_amount = fields.Monetary(string="Received Amount", currency_field='received_amount_currency_id', tracking=True)
    received_amount_1_currency_id = fields.Many2one('res.currency', string='Received Amount-1 Currency',default=32, tracking=True)
    received_amount_1 = fields.Monetary(string="Received Amount-1", currency_field='received_amount_1_currency_id', tracking=True)
    
    # ALınan tutar lar
    visit1_received_amount = fields.Monetary(string="Visit 1 Received Amount", currency_field='visit1_received_amount_currency_id', tracking=True)
    visit1_received_amount_currency_id = fields.Many2one('res.currency', string='Visit 1 Received Amount Currency',default=32, tracking=True)
    
    visit2_received_amount = fields.Monetary(string="Visit 2 Received Amount", currency_field='visit2_received_amount_currency_id', tracking=True)
    visit2_received_amount_currency_id = fields.Many2one('res.currency', string='Visit 2 Received Amount-1 Currency',default=32, tracking=True)
    
    visit3_received_amount = fields.Monetary(string="Visit 3 Received Amount", currency_field='visit3_received_amount_currency_id', tracking=True)
    visit3_received_amount_currency_id = fields.Many2one('res.currency', string='Visit 3 Received Amount-1 Currency',default=32, tracking=True)
    
    
    remaining_amount_currency_id = fields.Many2one('res.currency', string='Remaining Amount Currency',default=32, tracking=True)
    remaining_amount = fields.Monetary(string="Remaining Amount", currency_field='remaining_amount_currency_id', tracking=True)
    commission_rate = fields.Float(string="Commission Rate", tracking=True)
    commission_amount_currency_id = fields.Many2one('res.currency', string='Commission Currency %',default=32, tracking=True)
    commission_amount = fields.Monetary(string="Commission Amount", currency_field='commission_amount_currency_id', tracking=True)
    appointment_start_time = fields.Datetime(string="Appointment Start Date And Time", tracking=True)
    appointment_finish_time = fields.Datetime(string="Appointment Finish Date And Time", tracking=True)
    patient_coming_status = fields.Boolean("Coming Status", tracking=True)
    doctor = fields.Many2one('res.partner', string="Doctor", tracking=True)
    
    doctors = fields.Many2many('res.partner', string="Doktorlar", tracking=True)
    box = fields.Many2one('box.app', string="Klinic", tracking=True)
    brand = fields.Char(string="İmplant Marka", tracking=True)
    implant_number = fields.Integer(string="Implant Number", tracking=True)
    lab = fields.Char(string="Lab", tracking=True)
    zirkon_number = fields.Integer(string="Zirkon Number", tracking=True)
    other = fields.Char(string="Other", tracking=True)
    treatment_type = fields.Char(string="Treatment Type", tracking=True)
    incorrect_operation = fields.Boolean(string="Incorrect Operation", tracking=True)
    location_live_status = fields.Boolean(string="Location Live Status", tracking=True)
    lat = fields.Float(string="Latitude", digits=(12, 6))
    lng = fields.Float(string="Longitude", digits=(12, 6))
    customer_payment_status = fields.Selection([('not_paid','Not Paid'),('in_payment','In Payment'),('paid','Paid'),('partial','Partial'),('reversed','Reversed'),('invoicing_legacy','Invoicing App Legacy')],
                                    string="Customer Payment Status ", default="not_paid", tracking=True)
    repeat_process = fields.Boolean(string="Repeat Process", tracking=True)
    job_start_datetime = fields.Datetime(string="Job Start Time")
    job_finish_datetime = fields.Datetime(string="Job Finish Time")
    job_minutes = fields.Integer(string="Job Minutes")
    task_id = fields.Many2one('project.task', string="Linked Task")
    token = fields.Char(string="Token")
    
    
    operation_description = fields.Char(string="Operation Details Description", tracking=True)
    incoming_flight_description = fields.Char(string="Incoming Flight Information Description", tracking=True)
    outbound_flight_description = fields.Char(string="Outbound Flight Information Description", tracking=True)
    transfer_description = fields.Char(string="Transfer Description", tracking=True)
    appointment_description = fields.Char(string="Appointment Or Meet Description", tracking=True)
    payments_description = fields.Char(string="Payments Description", tracking=True)
    treatment_description = fields.Char(string="Treatment Description", tracking=True)
    
    @api.model
    def create(self, vals_list):
        records = super(ProjectTaskInherit, self).create(vals_list)
        self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                'type': 'success',
                'title': _("Başarılı"),
                'message': ('İşlemimiz Başarıyla Kaydedildi')
            })
     
        return records
   

  
    def write(self, vals):
        result = super(ProjectTaskInherit, self).write(vals)
        if result:
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'simple_notification', {
                'type': 'success',
                'title': _("Başarılı"),
                'message': ('İşlemimiz Başarıyla Kaydedildi')
            })
        return result 
    

    @api.model
    def generate_unique_id(self):
        characters = string.ascii_letters + string.digits
        unique_id = ''.join(random.choices(characters, k=16))
        return unique_id
    

    @api.onchange('received_amount','received_amount_1','sale_price','deposit_price')
    def payment_calculation(self):
        self["remaining_amount"] = self.sale_price - self.received_amount - self.received_amount_1 - self.deposit_price
        self["commission_amount"] = self.sale_price * self.commission_rate / 100
        if self.sale_price > 0 and self.remaining_amount == 0 and self.received_amount > 0:
            self["customer_payment_status"] = "paid"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount > 0:
            self["customer_payment_status"] = "partial"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.received_amount == 0:
            self["customer_payment_status"] = "not_paid"

    @api.onchange('sale_price_currency_id')
    def sale_currency_changed(self):
        self["deposit_price_currency_id"] = self.sale_price_currency_id.id
        self["received_amount_currency_id"] = self.sale_price_currency_id.id
        self["received_amount_1_currency_id"] = self.sale_price_currency_id.id
        self["remaining_amount_currency_id"] = self.sale_price_currency_id.id
    
    @api.onchange('partner_id','visit')
    def name_changer(self):
        self["name"] = str(self.partner_id.name) + " - " + str(dict(self._fields['visit'].selection).get(self.visit))
        
    def fligth_url_open(self):
        return { 'name': 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target' : 'new',
                'url': ("https://www.flightradar24.com/" + str(self.fligth_number))
               }

    #Muhammet eklediği kısım
    @api.onchange('visit1_received_amount','visit2_received_amount','visit3_received_amount','sale_price','deposit_price')
    def payment_calculation2(self):
        self["remaining_amount"] = self.sale_price - self.visit1_received_amount - self.visit2_received_amount - self.visit3_received_amount - self.deposit_price
        self["commission_amount"] = self.sale_price * self.commission_rate / 100
        if self.sale_price > 0 and self.remaining_amount == 0 and self.visit1_received_amount > 0:
            self["customer_payment_status"] = "paid"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.visit1_received_amount > 0:
            self["customer_payment_status"] = "partial"
        if self.sale_price > 0 and self.remaining_amount > 0 and self.visit1_received_amount == 0:
            self["customer_payment_status"] = "not_paid"

    @api.onchange('sale_price_currency_id')
    def sale_currency_changed2(self):
        self["deposit_price_currency_id"] = self.sale_price_currency_id.id
        self["visit1_received_amount_currency_id"] = self.sale_price_currency_id.id
        self["visit2_received_amount_currency_id"] = self.sale_price_currency_id.id
        self["visit3_received_amount_currency_id"] = self.sale_price_currency_id.id
        self["remaining_amount_currency_id"] = self.sale_price_currency_id.id
    
    @api.onchange('first_sale_price','sale_price')
    def check_field_warning(self):
        message = ""
        
        if not self.partner_id.passport_no:
            message += "Passport No, "

        if not self.patient_note:
            message += "Hasta notu, "

        if not self.patient_medications:
            message += "Hastanın kullandığı ilaçlar, "

        if not self.patient_chronic_disease:
            message += "Var ise kronik hastalık, "
         
        if not self.ticket_purchase_date:
            message += "Gelen Uçağın Bilet Satın Alma Tarihi, "   
         
        if not self.fligth_company:
            message += "Gelen Uçağın Firması, "   
            
        if not self.fligth_number:
            message += "Gelen Uçağın Numarası, " 
        
        if not self.ticket_attachments:
            message += "Gelen Uçağın Dökumanları, "   
                          
        if not self.arrival_datetime:
            message += "Gelen Varış Tarihi ve Saati, "         
 
                                 
        if not self.outgoing_ticket_purchase_date:
            message += "Giden Uçağın Bilet Satın Alma Tarihi, "   
         
        if not self.outgoing_fligth_company:
            message += "Giden Uçağın Firması, "   
            
        if not self.outgoing_fligth_number:
            message += "Giden Uçağın Numarası, " 
        
        if not self.outgoing_ticket_attachments:
            message += "Giden Uçağın Dökumanları, "   
                          
        if not self.departure_datetime:
            message += "Giden Varış Tarihi ve Saati, "  
        
 
        if message:  # Yani boş olan alan varsa
            message = message.rstrip(', ')  # Sonundaki fazladan virgül ve boşluğu kaldır
            message += " alanları boş bıraktınız. Bu bir bilgilendirmedir, kaydı bu mesajı yoksayarak devam edebilirsiniz."
            
        if self.first_sale_price or self.sale_price and message:
                        
            return {
                    'warning': {
                        'title': 'Uyarı',
                        'message': message
                    }
                }
    
    '''
    @api.onchange('patient_note')
    def onchange_patient_note(self):
        # Check if the patient_note field is not empty
        if self.patient_note:
            # Example condition: Trigger warning if the note is too short
            if len(self.patient_note) < 10:
                return {
                    'warning': {
                        'title': 'Error',
                        'message': 'The note is too short. Please provide more details.'
                    }
                }
            # Add other conditions as necessary
               
    '''
  
#discount_percentage = fields.Float("Discount Percentage")

    #gender = fields.Selection([('male','Male'),('female', 'Female'),('other', 'Other'),],string="Gender")
    #type_of_person = fields.Selection([('adult','Adult'),('child', 'Child'),('baby', 'Baby'),('driver', 'Driver')],string="Person Type")
    
    # How to OverRide Create Method Of a Model
    # https://www.youtube.com/watch?v=AS08H3G9x1U&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=26
    
    #@api.model
    #def create(self, vals_list):
    #    res = super(ResPartners, self).create(vals_list)
    #    print("yes working")
    #    # do the custom coding here
    #    return res
    
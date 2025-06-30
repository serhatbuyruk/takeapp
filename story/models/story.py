from odoo import tools, fields, models, api,_
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import json
from datetime import datetime
from base64 import b64encode
cookie = "story"

class storyProfile(models.Model):
    _name = "story.profile"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1)
    visibility = fields.Boolean(string="Visibility", default=True)
    image_type = fields.Selection([('story','Story'),('service','Service'),('notification','Notification')],
                                    string="Image Type ", default="story"
                                    )
    title = fields.Char(string="Title")
    description = fields.Char(string="Description")
    story_image = fields.Binary(string="Image")
    url = fields.Char(string="Url")
    color = fields.Integer(string="Color")
    company_id = fields.Many2one('res.company', string="Company")

    # Muhammet tarafından eklenen fields
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    price = fields.Integer(string="Price")
    paid = fields.Boolean(string="Paid")
    upload_date = fields.Date(string="Upload Date", default=lambda self: fields.Date.today())
    company_name = fields.Char(string="Company Name")
    topic = fields.Char(string="Topic")
    target_group = fields.Char(string="Target Group")

    # services
    rates = fields.Integer(string="Rates")


    
    

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError("Start date cannot be after end date.")
    # def see_profile(self):
    #     if len(self.card_id) > 4:
    #         return { 'name': 'Go to website',
    #                 'res_model': 'ir.actions.act_url',
    #                 'type': 'ir.actions.act_url',
    #                 'target' : 'self',
    #                 'url': ("/nfc/profile/" + str(self.card_id))
    #             }
    #     if len(self.card_id) == 4:
    #         return { 'name': 'Go to website',
    #                 'res_model': 'ir.actions.act_url',
    #                 'type': 'ir.actions.act_url',
    #                 'target' : 'self',
    #                 'url': ("/panel/touch/" + str(self.card_id))
    #             }
    
    # def from_profile(self):
    #     return {
    #         'name':_("Products to Process"),
    #         'view_mode': 'form',
    #         'view_id': False,
    #         'view_type': 'form',
    #         'res_model': 'story.profile',
    #         'res_id': self.id,
    #         'type': 'ir.actions.act_window',
    #         'nodestroy': True,
    #         'target': 'current',
    #         'domain': '[]'
    #     }
        # return { 'name': 'Go to Form Profile',
        #         'res_model': 'ir.actions.act_url',
        #         'type': 'ir.actions.act_url',
        #         'target' : 'self',
        #         'url': ("/web/#id=" + str(119) + "&menu_id=284&action=390&model=story.profile&view_type=form/")
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

    tc = fields.Char(string="TC No")
    code = fields.Char(string="Code")
    lat = fields.Float(string="Latitude", digits=(12, 6))
    lng = fields.Float(string="Longitude", digits=(12, 6))

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
    
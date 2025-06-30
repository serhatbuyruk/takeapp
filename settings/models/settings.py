from odoo import fields, models, api,_
from odoo.exceptions import UserError
import requests
import json
cookie = "settings"

class settingsProfile(models.Model):
    _name = "settings.profile"

    name = fields.Char(string="Name")
    device_id = fields.Many2one('devices.profile', string="Device", required="1")
    settings_image = fields.Binary(string="Image")
    entrance_delay_time = fields.Integer(string="Entrance Delay Time")
    exit_delay_time = fields.Integer(string="Exit Delay Time")
    alarm_time = fields.Integer(string="Alarm Time")
    setting_1_value = fields.Integer(string="Setting 1")
    setting_2_value = fields.Integer(string="Setting 2")
    setting_3_value = fields.Integer(string="Setting 3")
    setting_4_value = fields.Integer(string="Setting 4")
    setting_5_value = fields.Integer(string="Setting 5")
    setting_6_value = fields.Integer(string="Setting 6")
    setting_7_value = fields.Integer(string="Setting 7")
    setting_8_value = fields.Integer(string="Setting 8")
    setting_9_value = fields.Integer(string="Setting 9")
    setting_10_value = fields.Integer(string="Setting 10")
    wireless_loss = fields.Integer(string="Wireless Loss")
    electricity_power_cut = fields.Integer(string="Electricity Cut")
    communication_tset = fields.Integer(string="Communication Tset")
    alarm_set_voice = fields.Boolean(string="Alarm Set Voice")
    alarm_set_report = fields.Boolean(string="Alarm Set Report")
    emergency_start = fields.Boolean(string="Emergency Start")
    door_control = fields.Boolean(string="Door Control")
    wireless_detector_trig = fields.Boolean(string="Wireless Detector Trig")
    alarm_type = fields.Boolean(string="Alarm Type")
    device_data_update_time = fields.Datetime("Uptade Time")
    wifi_name = fields.Char(string="Wifi Name")
    wifi_password = fields.Char(string="Wifi Password")
    host_ip = fields.Char(string="Ahm Ip")
    port = fields.Char(string="Ahm Port")
    subscriber_no = fields.Char(string="Subscriber No")
    test_signal_time = fields.Integer(string="Test Signal Time")
    ahm_test_signal_time = fields.Integer(string="Ahm Test Time")
    last_action_user = fields.Many2one('res.partner', string="Last Action User")
    
    auto_alarmset_start_1 = fields.Datetime("Auto Alarmset Start (1. Day)",help="Bu ayar alarmın otomatik kurulması için gerekli zamanın başlangıcını belirtir.")
    auto_alarmset_finish_1 = fields.Datetime("Auto Alarmset Finish (1. Day)", help="Bu ayar alarmın otomatik kurulması için gerekli zamanın bitişini belirtir.")
    shift_start_1 = fields.Datetime("Shift Start (1. Day)")
    shift_finish_1 = fields.Datetime("Shift Finish (1. Day)")
    auto_alarmset_start_2 = fields.Datetime("Auto Alarmset Start (2. Day)",help="Bu ayar alarmın otomatik kurulması için gerekli zamanın başlangıcını belirtir.")
    auto_alarmset_finish_2 = fields.Datetime("Auto Alarmset Finish (2. Day)", help="Bu ayar alarmın otomatik kurulması için gerekli zamanın bitişini belirtir.")
    shift_start_2 = fields.Datetime("Shift Start (2. Day)")
    shift_finish_2 = fields.Datetime("Shift Finish (2. Day)")
    auto_alarmset_start_3 = fields.Datetime("Auto Alarmset Start (3. Day)",help="Bu ayar alarmın otomatik kurulması için gerekli zamanın başlangıcını belirtir.")
    auto_alarmset_finish_3 = fields.Datetime("Auto Alarmset Finish (3. Day)", help="Bu ayar alarmın otomatik kurulması için gerekli zamanın bitişini belirtir.")
    shift_start_3 = fields.Datetime("Shift Start (3. Day)")
    shift_finish_3 = fields.Datetime("Shift Finish (3. Day)")
    auto_alarmset_start_4 = fields.Datetime("Auto Alarmset Start (4. Day)",help="Bu ayar alarmın otomatik kurulması için gerekli zamanın başlangıcını belirtir.")
    auto_alarmset_finish_4 = fields.Datetime("Auto Alarmset Finish (4. Day)", help="Bu ayar alarmın otomatik kurulması için gerekli zamanın bitişini belirtir.")
    shift_start_4 = fields.Datetime("Shift Start (4. Day)")
    shift_finish_4 = fields.Datetime("Shift Finish (4. Day)")
    auto_alarmset_start_5 = fields.Datetime("Auto Alarmset Start (5. Day)",help="Bu ayar alarmın otomatik kurulması için gerekli zamanın başlangıcını belirtir.")
    auto_alarmset_finish_5 = fields.Datetime("Auto Alarmset Finish (5. Day)", help="Bu ayar alarmın otomatik kurulması için gerekli zamanın bitişini belirtir.")
    shift_start_5 = fields.Datetime("Shift Start (5. Day)")
    shift_finish_5 = fields.Datetime("Shift Finish (5. Day)")
    auto_alarmset_start_6 = fields.Datetime("Auto Alarmset Start (6. Day)",help="Bu ayar alarmın otomatik kurulması için gerekli zamanın başlangıcını belirtir.")
    auto_alarmset_finish_6 = fields.Datetime("Auto Alarmset Finish (6. Day)", help="Bu ayar alarmın otomatik kurulması için gerekli zamanın bitişini belirtir.")
    shift_start_6 = fields.Datetime("Shift Start (6. Day)")
    shift_finish_6 = fields.Datetime("Shift Finish (6. Day)")
    auto_alarmset_start_7 = fields.Datetime("Auto Alarmset Start (7. Day)",help="Bu ayar alarmın otomatik kurulması için gerekli zamanın başlangıcını belirtir.")
    auto_alarmset_finish_7 = fields.Datetime("Auto Alarmset Finish (7. Day)", help="Bu ayar alarmın otomatik kurulması için gerekli zamanın bitişini belirtir.")
    shift_start_7 = fields.Datetime("Shift Start (7. Day)")
    shift_finish_7 = fields.Datetime("Shift Finish (7. Day)")
    ahm_work_mode = fields.Char(string="Ahm Work Mode")

    zone_1a_sensor_type = fields.Selection([('130_motion_sensor','Motion Sensor'),('137_motion_sensor_tamper','Motion Sensor Tamper'),('130_door_window_sensor', 'Door Window Sensor'),('115_fire_sensor', 'Fire Sensor'),('153_temp_sensor', 'Temperature Sensor'),('151_gas_sensor', 'Gas Sensor')],
    string="Zone 1A Type",
    )
    zone_1b_sensor_type = fields.Selection([('130_motion_sensor','Motion Sensor'),('137_motion_sensor_tamper','Motion Sensor Tamper'),('130_door_window_sensor', 'Door Window Sensor'),('115_fire_sensor', 'Fire Sensor'),('153_temp_sensor', 'Temperature Sensor'),('151_gas_sensor', 'Gas Sensor')],
    string="Zone 1B Type",
    )
    default_settings_1 = fields.Boolean(string="Default Settings", help="Bu ayar Aktif edildiğinde yukarıdaki varsayılan ayarlar bu bölge için kurulur.")
    zone_status_1 = fields.Boolean(string="Zone Status", help="Bu ayar aktif edildiğinde bu bölge için sensör aktif edilir.")
    first_level_delay_zone_1 = fields.Boolean(string="1. Level Delay Zone")
    second_level_delay_zone_1 = fields.Boolean(string="2. Level Delay Zone")
    always_on_1 = fields.Boolean(string="Always On")
    sudden_alarm_1 = fields.Boolean(string="Sudden Alarm", help="Bu ayar aktif edildiğinde bölge aktif olduğunda siren ani olarak devreye girer.")
    panic_zone_1 = fields.Boolean(string="Panic Zone")

    
    zone_2a_sensor_type = fields.Selection([('130_motion_sensor','Motion Sensor'),('137_motion_sensor_tamper','Motion Sensor Tamper'),('130_door_window_sensor', 'Door Window Sensor'),('115_fire_sensor', 'Fire Sensor'),('153_temp_sensor', 'Temperature Sensor'),('151_gas_sensor', 'Gas Sensor')],
    string="Zone 2A Type",
    )
    zone_2b_sensor_type = fields.Selection([('130_motion_sensor','Motion Sensor'),('137_motion_sensor_tamper','Motion Sensor Tamper'),('130_door_window_sensor', 'Door Window Sensor'),('115_fire_sensor', 'Fire Sensor'),('153_temp_sensor', 'Temperature Sensor'),('151_gas_sensor', 'Gas Sensor')],
    string="Zone 2B Type",
    )
    default_settings_2 = fields.Boolean(string="Default Settings", help="Bu ayar Aktif edildiğinde yukarıdaki varsayılan ayarlar bu bölge için kurulur.")
    zone_status_2 = fields.Boolean(string="Zone Status", help="Bu ayar aktif edildiğinde bu bölge için sensör aktif edilir.")
    first_level_delay_zone_2 = fields.Boolean(string="1. Level Delay Zone")
    second_level_delay_zone_2 = fields.Boolean(string="2. Level Delay Zone")
    always_on_2 = fields.Boolean(string="Always On")
    sudden_alarm_2 = fields.Boolean(string="Sudden Alarm", help="Bu ayar aktif edildiğinde bölge aktif olduğunda siren ani olarak devreye girer.")
    panic_zone_2 = fields.Boolean(string="Panic Zone")

    
    zone_3a_sensor_type = fields.Selection([('130_motion_sensor','Motion Sensor'),('137_motion_sensor_tamper','Motion Sensor Tamper'),('130_door_window_sensor', 'Door Window Sensor'),('115_fire_sensor', 'Fire Sensor'),('153_temp_sensor', 'Temperature Sensor'),('151_gas_sensor', 'Gas Sensor')],
    string="Zone 3A Type", 
    )
    zone_3b_sensor_type = fields.Selection([('130_motion_sensor','Motion Sensor'),('137_motion_sensor_tamper','Motion Sensor Tamper'),('130_door_window_sensor', 'Door Window Sensor'),('115_fire_sensor', 'Fire Sensor'),('153_temp_sensor', 'Temperature Sensor'),('151_gas_sensor', 'Gas Sensor')],
    string="Zone 3B Type",
    )
    default_settings_3 = fields.Boolean(string="Default Settings")
    zone_status_3 = fields.Boolean(string="Zone Status", help="Bu ayar aktif edildiğinde bu bölge için sensör aktif edilir.")
    first_level_delay_zone_3 = fields.Boolean(string="1. Level Delay Zone")
    second_level_delay_zone_3 = fields.Boolean(string="2. Level Delay Zone")
    always_on_3 = fields.Boolean(string="Always On")
    sudden_alarm_3 = fields.Boolean(string="Sudden Alarm", help="Bu ayar aktif edildiğinde bölge aktif olduğunda siren ani olarak devreye girer.")
    panic_zone_3 = fields.Boolean(string="Panic Zone")

    
    zone_4a_sensor_type = fields.Selection([('130_motion_sensor','Motion Sensor'),('137_motion_sensor_tamper','Motion Sensor Tamper'),('130_door_window_sensor', 'Door Window Sensor'),('115_fire_sensor', 'Fire Sensor'),('153_temp_sensor', 'Temperature Sensor'),('151_gas_sensor', 'Gas Sensor')],
    string="Zone 4A Type",
    )
    zone_4b_sensor_type = fields.Selection([('130_motion_sensor','Motion Sensor'),('137_motion_sensor_tamper','Motion Sensor Tamper'),('130_door_window_sensor', 'Door Window Sensor'),('115_fire_sensor', 'Fire Sensor'),('153_temp_sensor', 'Temperature Sensor'),('151_gas_sensor', 'Gas Sensor')],
    string="Zone 4B Type",
    )
    default_settings_4 = fields.Boolean(string="Default Settings")
    zone_status_4 = fields.Boolean(string="Zone Status", help="Bu ayar aktif edildiğinde bu bölge için sensör aktif edilir.")
    first_level_delay_zone_4 = fields.Boolean(string="1. Level Delay Zone")
    second_level_delay_zone_4 = fields.Boolean(string="2. Level Delay Zone")
    always_on_4 = fields.Boolean(string="Always On")
    sudden_alarm_4 = fields.Boolean(string="Sudden Alarm", help="Bu ayar aktif edildiğinde bölge aktif olduğunda siren ani olarak devreye girer.")
    panic_zone_4 = fields.Boolean(string="Panic Zone")


    @api.onchange('device_id')
    def onchange_ab(self):
        if self.device_id: 
            self.name = str(self.device_id.name)
    
    @api.onchange('entrance_delay_time','exit_delay_time','alarm_time','wifi_name','wifi_password')
    def _get_partner(self):
        partner = self.env['res.users'].browse(self.env.uid).partner_id
        for rec in self: 
            rec.last_action_user = partner.id
    
                              
class ResPartnersInherit(models.Model):
    _inherit = 'res.partner'

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
    
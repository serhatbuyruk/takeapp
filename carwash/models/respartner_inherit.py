from odoo import models, fields


class ResPartnersInherit(models.Model):
    _inherit = 'res.partner'

    tc = fields.Char(string="TC No")
    passport_no = fields.Char(string="Passport No")
    passport_attachment = fields.Many2many(
        'ir.attachment',
        'attachment_rel_2',
        'pro_id_2',
        'attach_id_2',
        string='Passport Attachments',
    )
    id_card_attachment = fields.Many2many(
        'ir.attachment',
        'attachment_rel_idcard',
        'pro_id_idcard',
        'attach_id_idcard',
        string='Id Card Attachments',
    )
    driver_licence_attachment = fields.Many2many(
        'ir.attachment',
        'attachment_rel_drivelicence',
        'pro_id_drivelicence',
        'attach_id_drivelicence',
        string='Driver Licence Attachments',
    )
    lat = fields.Float(string="Latitude", digits=(12, 6))
    lng = fields.Float(string="Longitude", digits=(12, 6))
    code = fields.Char(string="Code")
    lat = fields.Float(string="Latitude", digits=(12, 6))
    lng = fields.Float(string="Longitude", digits=(12, 6))

    license_plate = fields.Char(string="License Plate")
    car_model = fields.Char(string="Car Model")
    car_brand = fields.Char(string="Car Brand")
    discount = fields.Integer(string="Discount")

    def open_qr_link(self):
        return {
            'name': 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': ("/company-qr?card_id=" + str(self.id)),
        }

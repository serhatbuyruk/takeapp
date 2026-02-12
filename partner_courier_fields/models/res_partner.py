from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    courier_id = fields.Char(string="Kurye ID")
    courier_first_name = fields.Char(string="Kurye Adı")
    courier_last_name = fields.Char(string="Kurye Soyadı")

    invoice_person = fields.Char(string="Fatura Kesecek Kişi Adı Soyadı")
    invoice_person_tc = fields.Char(string="Fatura Kesecek Kişi T.C. No", tracking=True)

    payment_person = fields.Char(string="Para Yatacak Kişi Adı Soyadı")
    payment_person_tc = fields.Char(string="Para Yatacak Kişi T.C. No")

    iban = fields.Char(string="IBAN Bilgisi")
    bank_branch = fields.Char(string="Şube Kodu")
    bank_account_no = fields.Char(string="Hesap No")
    bank_name = fields.Char(string="Banka Adı")

    area = fields.Char(string="Çalıştığı Bölge")
    city = fields.Char(string="Çalıştığı Şehir")

    kullanici_adi = fields.Char(string="Kullanıcı Adı")
    sifre = fields.Char(string="Şifre")

    invoice_type = fields.Char(string="Fatura Şekli")
    manager_name = fields.Char(string="Yöneticisi")

    # ✔ Monetary TRY alanı
    debt_info = fields.Monetary(string="Güncel Borç Bilgisi", currency_field="currency_id", tracking=True)
    borc_aciklamasi = fields.Char(string="Borç Açıklaması", tracking=True)

    # ✔ TRY seçili olacak şekilde currency_id
    currency_id = fields.Many2one(
        'res.currency',
        string="Para Birimi",
        default=lambda self: self.env.ref('base.TRY').id,
        required=True
    )

    archive_note = fields.Char(string="Arşivleme Sebebi")

    p1_yetki_attachment = fields.Many2many('ir.attachment','attachment_rel_p1_yetki_attachment','pro_id_p1_yetki_attachment','attach_id_p1_yetki_attachment', string='P1 Yetki Belgeleri',) 
    ehliyet_attachment = fields.Many2many('ir.attachment','attachment_rel_ehliyet_attachment','pro_id_ehliyet_attachment','attach_id_ehliyet_attachment', string='Ehliyet Belgeleri',)
    ruhsat_ve_muayene_attachment = fields.Many2many('ir.attachment','attachment_rel_ruhsat_ve_muayene_attachment','pro_id_ruhsat_ve_muayene_attachment','attach_id_ruhsat_ve_muayene_attachment', string='Ruhsat ve Muayene Belgeleri',)
    zorunlu_trafik_sigortasi_attachment = fields.Many2many('ir.attachment','attachment_rel_zorunlu_trafik_sigortasi_attachment','pro_id_zorunlu_trafik_sigortasi_attachment','attach_id_zorunlu_trafik_sigortasi_attachment', string='Zorunlu Trafik Sigortası Belgeleri',)
    isg_attachment = fields.Many2many('ir.attachment','attachment_rel_isg_attachment','pro_id_isg_attachment','attach_id_isg_attachment', string='İSG Belgeleri',)
    vergi_levhasi = fields.Many2many('ir.attachment','attachment_rel_vergi_levhasi_attachment','pro_id_vergi_levhasi_attachment','attach_id_vergi_levhasi_attachment', string='Vergi Levhası',)
    sgk_belgesi = fields.Many2many('ir.attachment','attachment_rel_sgk_belgesi_attachment','pro_id_sgk_belgesi_attachment','attach_id_sgk_belgesi_attachment', string='SGK Belgeleri',)
    kask = fields.Boolean(string="Kask")
    mont = fields.Boolean(string="Mont")
    eldiven = fields.Boolean(string="Eldiven")
    reflektor = fields.Boolean(string="Reflektör")

    @api.onchange('courier_first_name', 'courier_last_name')
    def _onchange_courier_names(self):
        first = self.courier_first_name or ""
        last = self.courier_last_name or ""

        full_name = (first + " " + last).strip()

        if full_name:
            self.name = full_name

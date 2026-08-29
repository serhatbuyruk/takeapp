from odoo import fields, models


class PartnerCourierAccountingLine(models.Model):
    _name = 'partner.courier.accounting.line'
    _description = 'Partner Courier Accounting Line'
    _order = 'date_start desc, date_end desc, id desc'

    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        required=True,
        ondelete='cascade',
        index=True,
    )
    imported_at = fields.Datetime(string='Import Tarihi', default=fields.Datetime.now, readonly=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Para Birimi',
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )
    date_start = fields.Date(string='Hafta Başlangıç')
    date_end = fields.Date(string='Hafta Bitiş')
    payment_date = fields.Date(string='Ödemenin Yapılacağı Tarih')
    area = fields.Char(string='Bölge')
    city = fields.Char(string='Şehir')
    pickup_count = fields.Integer(string='Pick up')
    dropoff_count = fields.Integer(string='Drop off')
    google_distance_pickup_amount = fields.Monetary(string='Google Distance Pick Up')
    google_distance_dropoff_amount = fields.Monetary(string='Google Distance Drop Off')
    pickup_amount = fields.Monetary(string='Pick up Tutar')
    dropoff_amount = fields.Monetary(string='Drop off Tutar')
    distance_amount = fields.Monetary(string='Kilometre Başı Mesafe Tutarı')
    guarantee_region_amount = fields.Monetary(string='Garanti Bölge Tutarı')
    night_shift_amount = fields.Monetary(string='Gece Mesaisi Tutarı')
    region_campaign_amount = fields.Monetary(string='Bölge Kampanya Tutarı')
    weekly_extra_package_amount = fields.Monetary(string='Haftalık Ek Paket Tutarı')
    daily_bonus_amount = fields.Monetary(string='Günlük Bonus')
    tip_amount_tax_included = fields.Monetary(string='Bahşiş Tutar (KDV Dahil)')
    tip_amount_tax_excluded = fields.Monetary(string='Bahşiş Tutar (KDV Hariç)')
    earning_amount_tax_excluded = fields.Monetary(string='Hak Ediş Tutarı (KDV Hariç)')
    total_payment_tax_excluded = fields.Monetary(string='Toplam Ödeme (KDV Hariç)')
    kuryetec_bonus_tax_excluded = fields.Monetary(string="Kuryetec Bonus'u (KDV Hariç)")
    bonus_included_total_payment_tax_excluded = fields.Monetary(string='Bonus Dahil Toplam Ödeme (KDV Hariç)')
    bonus_included_earning_tax_included = fields.Monetary(string='Bonus Dahil Hak Ediş (KDV Dahil)')
    cash_deduction_tax_included = fields.Monetary(string='Cash Kesinti Tutarı (KDV Dahil)')
    softpos_deduction_tax_included = fields.Monetary(string='SoftPos Kesinti Tutarı (KDV Dahil)')
    insurance_deduction_amount = fields.Monetary(string='Sigorta Kesintisi')
    field_deduction_order_amount = fields.Monetary(string='Saha Kesintisi (Sipariş)')
    ixopay_cash_deposit_amount = fields.Monetary(string='İXOPAY (Nakit Yatırılan Tutar)')
    final_deduction_yemeksepeti_amount = fields.Monetary(string='Son Kesinti (Yemek Sepeti)')
    one_week_previous_negative_balance_amount = fields.Monetary(string='Bir Hafta Önce Eksi Bakiye')
    previous_balance_amount = fields.Monetary(string='Önceden Kalan Borç / Bakiye')
    equipment_purchase_amount = fields.Monetary(string='Ekipman Alımı')
    total_deduction_amount = fields.Monetary(string='Toplam Kesinti')
    one_week_previous_payment_deduction_amount = fields.Monetary(string='Bir Hafta Önce Ödemesinden Düşülen')
    two_week_previous_payment_deduction_amount = fields.Monetary(string='İki Hafta Önce Ödemesinden Düşülen')
    withholding_tax_amount = fields.Monetary(string='Tevkifat Vergisi Tutarı')
    advance_amount = fields.Monetary(string='Avans')
    deposited_payment_amount = fields.Monetary(string='Yatırılan Ödeme')
    isg_payment_amount = fields.Monetary(string='İSG Ödeme')
    sgk_amount = fields.Monetary(string='Sigorta')
    net_payable_amount = fields.Monetary(string='Toplam Ödenecek Net Tutar (Kesintiler Düşürülmüştür)')
    invoice_type = fields.Char(string='Fatura Tipi')
    note = fields.Char(string='NOT')
    manager_name = fields.Char(string='Yönetici')

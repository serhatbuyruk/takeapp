from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    courier_field_manager_id = fields.Many2one(
        'res.users',
        string='Eski Saha Yöneticisi Kullanıcısı',
        domain=[('active', '=', True), ('share', '=', False)],
        ondelete='set null',
        help='Önceki sürümden kalan teknik alan.',
    )
    courier_field_manager_partner_id = fields.Many2one(
        'res.partner',
        string='Kendi Saha Yöneticisi',
        domain="[('active', '=', True), ('id', '!=', id), '|', ('courier_id', '!=', False), ('user_ids', '!=', False)]",
        ondelete='set null',
        help='Kurye portalından aranabilecek yönetici contactı. Başka bir kurye de yönetici olabilir.',
    )
    courier_manager_portal_user_id = fields.Many2one(
        'res.users',
        string='Yönetici Hesabı',
        domain=[('active', '=', True), ('share', '=', True)],
        ondelete='set null',
        help='Saha yöneticisinin portal kullanıcı hesabı.',
    )
    courier_call_support_member = fields.Boolean(
        string='Kuryetec Destek Ekibi Üyesi',
        help='Kurye destek çağrılarında seçilebilecek kişidir.',
    )
    courier_call_support_available = fields.Boolean(
        string='Destek Çağrılarına Müsait',
        help='Açıksa ve geçerli cihaz bildirimi varsa destek çağrısı alabilir.',
    )
    courier_call_support_last_call_at = fields.Datetime(
        string='Son Destek Çağrısı',
        readonly=True,
        copy=False,
    )

    @api.onchange('courier_manager_portal_user_id')
    def _onchange_courier_manager_portal_user_id(self):
        for partner in self.filtered('courier_manager_portal_user_id'):
            partner.courier_field_manager_partner_id = partner.courier_manager_portal_user_id.partner_id

    @api.constrains('courier_field_manager_partner_id')
    def _check_courier_field_manager_partner_id(self):
        for partner in self.filtered('courier_field_manager_partner_id'):
            manager = partner.courier_field_manager_partner_id
            if manager == partner:
                raise ValidationError(_('Bir kurye kendi saha yöneticisi olamaz.'))
            if not manager.active:
                raise ValidationError(_('Saha yöneticisi aktif bir contact olmalıdır.'))

    @api.constrains('courier_field_manager_partner_id', 'courier_manager_portal_user_id')
    def _check_manager_portal_user(self):
        for partner in self.filtered('courier_manager_portal_user_id'):
            manager = partner.courier_field_manager_partner_id
            if manager and partner.courier_manager_portal_user_id.partner_id != manager:
                raise ValidationError(_('Yönetici hesabı, seçilen saha yöneticisi contactına ait olmalıdır.'))

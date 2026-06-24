from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    courier_accounting_line_ids = fields.One2many(
        'partner.courier.accounting.line',
        'partner_id',
        string='Hakediş',
    )

    player_id = fields.Char(string='Player ID')

    is_duplicate_courier = fields.Boolean(
        string="Çift Kurye ID'li",
        compute="_compute_is_duplicate_courier",
        search="_search_is_duplicate_courier",
    )

    has_attachments = fields.Boolean(
        string="Belgeleri Var mı?",
        compute="_compute_has_attachments",
    )

    @api.constrains('courier_id')
    def _check_unique_courier_id(self):
        for partner in self:
            if not partner.courier_id:
                continue
            duplicate = self.with_context(active_test=False).search([
                ('courier_id', '=', partner.courier_id),
                ('id', '!=', partner.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(_(
                    "Bu Kurye ID (%s) zaten başka bir contact (%s) üzerinde tanımlı!"
                ) % (partner.courier_id, duplicate.display_name))

    def _compute_is_duplicate_courier(self):
        self.env.cr.execute("""
            SELECT courier_id 
            FROM res_partner 
            WHERE active = True AND courier_id IS NOT NULL AND courier_id != ''
            GROUP BY courier_id 
            HAVING COUNT(*) > 1
        """)
        duplicate_ids = [r[0] for r in self.env.cr.fetchall()]
        for partner in self:
            partner.is_duplicate_courier = partner.courier_id in duplicate_ids

    def _search_is_duplicate_courier(self, operator, value):
        self.env.cr.execute("""
            SELECT courier_id 
            FROM res_partner 
            WHERE active = True AND courier_id IS NOT NULL AND courier_id != ''
            GROUP BY courier_id 
            HAVING COUNT(*) > 1
        """)
        duplicate_ids = [r[0] for r in self.env.cr.fetchall()]
        if operator == '=':
            if value:
                return [('courier_id', 'in', duplicate_ids), ('active', '=', True)]
            else:
                return ['|', ('courier_id', 'not in', duplicate_ids), ('courier_id', '=', False)]
        elif operator == '!=':
            if value:
                return ['|', ('courier_id', 'not in', duplicate_ids), ('courier_id', '=', False)]
            else:
                return [('courier_id', 'in', duplicate_ids), ('active', '=', True)]
        return []

    def _compute_has_attachments(self):
        m2m_fields = [
            'adli_sicil_attachment', 'src_attachment', 'p1_yetki_attachment',
            'ehliyet_attachment', 'ruhsat_ve_muayene_attachment',
            'zorunlu_trafik_sigortasi_attachment', 'isg_attachment',
            'vergi_levhasi', 'sgk_belgesi'
        ]
        
        for partner in self:
            has_m2m = False
            for field_name in m2m_fields:
                try:
                    if partner[field_name]:
                        has_m2m = True
                        break
                except KeyError:
                    pass
            partner.has_attachments = has_m2m

        remaining_partners = self.filtered(lambda p: not p.has_attachments)
        if remaining_partners:
            attachment_res_ids = self.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'res.partner'),
                ('res_id', 'in', remaining_partners.ids)
            ]).mapped('res_id')
            partners_with_db_attachments = set(attachment_res_ids)
            for partner in remaining_partners:
                if partner.id in partners_with_db_attachments:
                    partner.has_attachments = True

    def action_show_attachments(self):
        self.ensure_one()
        attachment_ids = []
        m2m_fields = [
            'adli_sicil_attachment', 'src_attachment', 'p1_yetki_attachment',
            'ehliyet_attachment', 'ruhsat_ve_muayene_attachment',
            'zorunlu_trafik_sigortasi_attachment', 'isg_attachment',
            'vergi_levhasi', 'sgk_belgesi'
        ]
        for field in m2m_fields:
            try:
                if self[field]:
                    attachment_ids.extend(self[field].ids)
            except KeyError:
                pass
        
        db_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', self.id),
        ])
        attachment_ids.extend(db_attachments.ids)
        attachment_ids = list(set(attachment_ids))

        return {
            'name': _('Belgeler / Eklentiler'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', attachment_ids)],
            'context': {'default_res_model': 'res.partner', 'default_res_id': self.id},
            'target': 'current',
        }

    adli_sicil_attachment = fields.Many2many(
        'ir.attachment',
        'attachment_rel_adli_sicil_attachment',
        'pro_id_adli_sicil_attachment',
        'attach_id_adli_sicil_attachment',
        string='Adli Sicil',
    )

    src_attachment = fields.Many2many(
        'ir.attachment',
        'attachment_rel_src_attachment',
        'pro_id_src_attachment',
        'attach_id_src_attachment',
        string='SRC Belgeleri',
    )

    def action_open_courier_accounting_home(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/kurye-muhasebe/admin/%s' % self.id,
            'target': 'new',
        }

    def _has_missing_documents(self):
        self.ensure_one()
        # The 5 required documents:
        # 1. ehliyet_attachment
        # 2. adli_sicil_attachment
        # 3. p1_yetki_attachment
        # 4. vergi_levhasi
        # 5. src_attachment
        return not (
            self.ehliyet_attachment and
            self.adli_sicil_attachment and
            self.p1_yetki_attachment and
            self.vergi_levhasi and
            self.src_attachment
        )

    def action_show_same_courier_id_contacts(self):
        courier_ids = [p.courier_id for p in self if p.courier_id]
        if not courier_ids:
            duplicate_courier_ids = []
        else:
            self.env.cr.execute("""
                SELECT courier_id
                FROM res_partner
                WHERE active = True AND courier_id IN %s
                GROUP BY courier_id
                HAVING COUNT(*) >= 2
            """, (tuple(courier_ids),))
            duplicate_courier_ids = [r[0] for r in self.env.cr.fetchall()]

        return {
            'name': _('Aynı Kurye ID\'li Kişiler'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'domain': [('courier_id', 'in', duplicate_courier_ids)],
            'context': {'group_by': 'courier_id'},
            'target': 'current',
        }


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def is_deletable_by_courier(self):
        self.ensure_one()
        if not self.create_date:
            return False
        # 5 minutes = 300 seconds
        return (fields.Datetime.now() - self.create_date).total_seconds() < 300

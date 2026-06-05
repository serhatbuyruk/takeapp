from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    courier_accounting_line_ids = fields.One2many(
        'partner.courier.accounting.line',
        'partner_id',
        string='Hakediş',
    )

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


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def is_deletable_by_courier(self):
        self.ensure_one()
        if not self.create_date:
            return False
        # 5 minutes = 300 seconds
        return (fields.Datetime.now() - self.create_date).total_seconds() < 300


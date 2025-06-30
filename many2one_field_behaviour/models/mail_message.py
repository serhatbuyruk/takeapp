from odoo import api, fields, models, _


class MailMessage(models.Model):
    _inherit = "mail.message"

    def message_format(self, format_reply=True):
        vals_list = super(MailMessage, self).message_format(format_reply=format_reply)

        many2one_field_behaviour = self.env['ir.config_parameter'].sudo().get_param(
            'many2one_field_behaviour.many2one_field_behaviour')

        for val in vals_list:
            val['new_tab'] = False
            val['show_popup'] = False

            if many2one_field_behaviour == '1':
                val['new_tab'] = True
            elif many2one_field_behaviour == '2':
                val['show_popup'] = True

        return vals_list



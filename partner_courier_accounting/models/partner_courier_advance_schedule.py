from odoo import api, fields, models


class PartnerCourierAdvanceSchedule(models.Model):
    _name = 'partner.courier.advance.schedule'
    _description = 'Courier Advance Request Schedule'
    _rec_name = 'name'

    name = fields.Char(default='Avans Talep Günleri', required=True, readonly=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company, readonly=True,
    )
    monday = fields.Boolean(string='Pazartesi')
    tuesday = fields.Boolean(string='Salı')
    wednesday = fields.Boolean(string='Çarşamba')
    thursday = fields.Boolean(string='Perşembe', default=True)
    friday = fields.Boolean(string='Cuma', default=True)
    saturday = fields.Boolean(string='Cumartesi')
    sunday = fields.Boolean(string='Pazar')

    _sql_constraints = [
        ('company_unique', 'unique(company_id)', 'Her şirket için yalnızca bir avans talep takvimi olabilir.'),
    ]

    @api.model
    def action_open_current(self):
        schedule = self.search([('company_id', '=', self.env.company.id)], limit=1)
        if not schedule:
            schedule = self.create({})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Avans Talep Günleri',
            'res_model': self._name,
            'res_id': schedule.id,
            'view_mode': 'form',
            'view_id': self.env.ref(
                'partner_courier_accounting.view_partner_courier_advance_schedule_form'
            ).id,
            'target': 'current',
        }

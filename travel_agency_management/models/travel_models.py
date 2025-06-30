from odoo import models, fields

class TravelServiceType(models.Model):
    _name = 'travel.service.type'
    _description = 'Travel Service Type'

    name = fields.Char(string="Service Name", required=True, translate=True)

class TravelAirport(models.Model):
    _name = 'travel.airport'
    _description = 'Airport'
    _order = 'name'

    name = fields.Char(string="Airport Name", required=True)
    code = fields.Char(string="IATA Code", required=True)
    country_id = fields.Many2one('res.country', string="Country", required=True)

    def name_get(self):
        result = []
        for record in self:
            name = f'[{record.code}] {record.name}'
            result.append((record.id, name))
        return result

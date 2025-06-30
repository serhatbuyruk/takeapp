from odoo import api, models

from lxml import etree
import ast


class Model(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_views(self, views, options=None):
        result = super(Model, self).get_views(views, options)

        result = self._user_many2one_field_restriction(views, result)

        return result

    def _user_many2one_field_restriction(self, views, list_view):

        many2one_field_behaviour = self.env['ir.config_parameter'].sudo().get_param('many2one_field_behaviour.many2one_field_behaviour')

        for view in views:
            view_name = view[1]
            if view_name in list_view['views']:
                viewObj = list_view['views'][view_name]
                tree = etree.fromstring(viewObj['arch'])

                nodes = tree.xpath('//field')
                for node in nodes:
                    if many2one_field_behaviour == '1':
                        self._update_many2one_options(node, 'new_tab', True)
                    elif many2one_field_behaviour == '2':
                        self._update_many2one_options(node, 'show_popup', True)

                viewObj['arch'] = etree.tostring(tree, encoding="unicode").replace('\t', '')

        return list_view

    def _update_many2one_options(self, node, attribute_name, value):
        options = node.get('options')

        if options:
            options = options.replace("true", "True")
            options = options.replace("false", "False")

            options = ast.literal_eval(options)

            if 'new_tab' not in options and 'show_popup' not in options:
                options.update({
                    attribute_name: value
                })
                node.set('options', repr(options))
        else:
            options = {
                attribute_name: value
            }
            node.set('options', repr(options))
        return node

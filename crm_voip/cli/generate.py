# -*- coding: UTF-8 -*-
import signal
import trace

from odoo.cli.command import Command
import odoo
import os
import csv

from odoo.cli.shell import raise_keyboard_interrupt
from odoo.tools import config, traceback


class Generate(Command):
    """Generate ir_access.csv"""

    env = None

    def generate_access_csv(self):
        models = self.env['ir.model'].search([('model', 'ilike', 'crm_voip.%')], order='model asc')
        groups = self.env['ir.model.data'].search([('model', '=', 'res.groups'), ('module', '=', 'crm_voip')],
                                                  order='model asc')
        print(models)
        print(groups)

        id_prefix = 'access_'
        ignore_prefix = 'ignore_access_'
        ignored_rules = []
        new_rules = []
        exist_group_rules = {}

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, 'security/ir.model.access.csv')
        with open(csv_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count > 0:
                    if row[3] not in exist_group_rules:
                        exist_group_rules.update({row[3]: {}})
                    if str(row[0]).startswith(ignore_prefix):
                        ignored_rules.append(row)
                    else:
                        exist_group_rules[row[3]].update({row[0]: row})
                line_count += 1

        for model in models:
            if model.model not in self.env:
                continue
            model_id = 'model_' + model.model.replace('.', '_')
            access_id = '%s%s' % (id_prefix, model_id)
            new_rules.append([access_id, model.model, model_id, '', 0, 0, 0, 0])

        new_group_rules = []
        for group in groups:
            for new_rule in new_rules:
                rule = new_rule.copy()
                rule[0] = '%s_%s' % (rule[0], group.name)
                group_id = '%s.%s' % (group.module, group.name)
                rule[3] = group_id
                if group_id in exist_group_rules and rule[0] in exist_group_rules[group_id]:
                    rule[4] = exist_group_rules[group_id][rule[0]][4]
                    rule[5] = exist_group_rules[group_id][rule[0]][5]
                    rule[6] = exist_group_rules[group_id][rule[0]][6]
                    rule[7] = exist_group_rules[group_id][rule[0]][7]
                if group_id == 'crm_voip.crm_voip_manager':
                    rule[4] = 1
                    rule[5] = 1
                    rule[6] = 1
                    rule[7] = 1
                new_group_rules.append(rule)
        new_group_rules += ignored_rules
        try:
            with open(csv_path, mode='w') as csv_path:
                csv_writer = csv.writer(csv_path, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(
                    ['id', 'name', 'model_id:id', 'group_id:id', 'perm_read', 'perm_write', 'perm_create',
                     'perm_unlink'])
                for new_group_rule in new_group_rules:
                    csv_writer.writerow(new_group_rule)
        except Exception as e:
            traceback.print_exc()

    def run(self, args):
        config.parse_config(args)
        odoo.cli.server.report_configuration()
        odoo.service.server.start(preload=[], stop=True)
        signal.signal(signal.SIGINT, raise_keyboard_interrupt)
        with odoo.api.Environment.manage():
            if config['db_name']:
                registry = odoo.registry(config['db_name'])
                with registry.cursor() as cr:
                    uid = odoo.SUPERUSER_ID
                    ctx = odoo.api.Environment(cr, uid, {})['res.users'].context_get()
                    self.env = odoo.api.Environment(cr, uid, ctx)
                    self.generate_access_csv()
                    print("\n" * 5)
                    print("ok")
                    print("\n" * 5)

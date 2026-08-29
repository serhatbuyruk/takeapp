"""Rename the generated shift display suffix without changing technical keys."""


def migrate(cr, version):
    cr.execute(
        """
        UPDATE slots_profile
           SET name = LEFT(name, LENGTH(name) - LENGTH(' Slotu'))
                      || ' Vardiyası',
               write_date = NOW()
         WHERE name LIKE %s
        """,
        ('% Slotu',),
    )
    cr.execute(
        """
        UPDATE ir_module_category
           SET name = jsonb_set(
               COALESCE(name, '{}'::jsonb),
               '{en_US}',
               to_jsonb('Vardiyalar'::text),
               true
           )
         WHERE id = (
             SELECT res_id
               FROM ir_model_data
              WHERE module = 'slots'
                AND name = 'slots_security_groups'
                AND model = 'ir.module.category'
         )
        """
    )

"""Adopt manually created security records before loading module data."""


def migrate(cr, version):
    cr.execute("SELECT 1 FROM ir_model_access WHERE id = 1907")
    if not cr.fetchone():
        return
    cr.execute(
        """
        INSERT INTO ir_model_data
                    (module, name, model, res_id, noupdate,
                     create_uid, write_uid, create_date, write_date)
             VALUES ('notifier', 'access_portal_notifier_profile',
                     'ir.model.access', 1907, FALSE, 1, 1, NOW(), NOW())
        ON CONFLICT (module, name) DO UPDATE
                SET model = EXCLUDED.model,
                    res_id = EXCLUDED.res_id,
                    noupdate = FALSE,
                    write_uid = 1,
                    write_date = NOW()
        """
    )

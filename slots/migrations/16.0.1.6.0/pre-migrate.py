"""Adopt manually created security records before loading module data."""


def migrate(cr, version):
    rows = [
        ("ir.rule", 340, "rule_portal_slots_profile", "ir_rule"),
        ("ir.rule", 342, "rule_portal_skurye_lines", "ir_rule"),
        ("ir.rule", 348, "rule_dealer_res_partner", "ir_rule"),
        ("ir.model.access", 1676, "access_portal_slots_profile", "ir_model_access"),
        ("ir.model.access", 1711, "access_full_slots_profile", "ir_model_access"),
    ]
    for model, res_id, name, table in rows:
        cr.execute(f"SELECT 1 FROM {table} WHERE id = %s", (res_id,))
        if not cr.fetchone():
            continue
        cr.execute(
            """
            INSERT INTO ir_model_data
                        (module, name, model, res_id, noupdate,
                         create_uid, write_uid, create_date, write_date)
                 VALUES ('slots', %s, %s, %s, FALSE, 1, 1, NOW(), NOW())
            ON CONFLICT (module, name) DO UPDATE
                    SET model = EXCLUDED.model,
                        res_id = EXCLUDED.res_id,
                        noupdate = FALSE,
                        write_uid = 1,
                        write_date = NOW()
            """,
            (name, model, res_id),
        )

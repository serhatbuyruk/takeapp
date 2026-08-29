"""Adopt manually created security records before loading module data."""


def migrate(cr, version):
    rows = [
        ("ir.rule", 339, "rule_portal_corders_profile", "ir_rule"),
        ("ir.rule", 341, "rule_portal_res_partner", "ir_rule"),
        ("ir.rule", 346, "rule_manager_res_partner", "ir_rule"),
        ("ir.rule", 349, "rule_admin_res_partner", "ir_rule"),
        ("ir.model.access", 1675, "access_portal_corders_profile", "ir_model_access"),
        ("ir.model.access", 1677, "access_portal_res_partner", "ir_model_access"),
        ("ir.model.access", 1678, "access_portal_order_profile_lines", "ir_model_access"),
        ("ir.model.access", 1706, "access_manager_corders_profile", "ir_model_access"),
        ("ir.model.access", 1708, "access_dealer_res_partner", "ir_model_access"),
        ("ir.model.access", 1709, "access_admin_res_partner", "ir_model_access"),
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
                 VALUES ('corders', %s, %s, %s, FALSE, 1, 1, NOW(), NOW())
            ON CONFLICT (module, name) DO UPDATE
                    SET model = EXCLUDED.model,
                        res_id = EXCLUDED.res_id,
                        noupdate = FALSE,
                        write_uid = 1,
                        write_date = NOW()
            """,
            (name, model, res_id),
        )

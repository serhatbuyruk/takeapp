"""Adopt technical actions that were originally created in the UI."""


def migrate(cr, version):
    module = "notifier"
    source_tables = {
        "base.automation": "base_automation",
        "ir.actions.server": "ir_act_server",
        "ir.cron": "ir_cron",
    }
    rows = [
        ("base.automation", 26, "automation_26"),
        ("ir.actions.server", 1297, "automation_server_action_26"),
        ("ir.cron", 45, "cron_45"),
        ("ir.actions.server", 954, "cron_server_action_45"),
        ("ir.cron", 60, "cron_60"),
        ("ir.actions.server", 1158, "cron_server_action_60"),
        ("ir.cron", 71, "cron_71"),
        ("ir.actions.server", 1292, "cron_server_action_71"),
    ]
    for model, res_id, name in rows:
        cr.execute(
            f"SELECT 1 FROM {source_tables[model]} WHERE id = %s",
            (res_id,),
        )
        if not cr.fetchone():
            continue
        cr.execute(
            """
            INSERT INTO ir_model_data (module, name, model, res_id, noupdate,
                                       create_uid, write_uid, create_date, write_date)
            SELECT %s, %s, %s, %s, FALSE, 1, 1, NOW(), NOW()
             WHERE EXISTS (
                       SELECT 1
                         FROM ir_model_data
                        WHERE model = %s
                          AND res_id = %s
                    ) IS FALSE
            ON CONFLICT (module, name) DO UPDATE
                    SET model = EXCLUDED.model,
                        res_id = EXCLUDED.res_id,
                        noupdate = FALSE,
                        write_uid = 1,
                        write_date = NOW()
            """,
            (module, name, model, res_id, model, res_id),
        )

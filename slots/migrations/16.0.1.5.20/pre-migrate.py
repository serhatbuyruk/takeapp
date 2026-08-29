"""Adopt technical actions that were originally created in the UI."""


def migrate(cr, version):
    module = "slots"
    source_tables = {
        "base.automation": "base_automation",
        "ir.actions.server": "ir_act_server",
        "ir.cron": "ir_cron",
    }
    rows = [
        ("base.automation", 10, "automation_10"),
        ("ir.actions.server", 1101, "automation_server_action_10"),
        ("base.automation", 11, "automation_11"),
        ("ir.actions.server", 1108, "automation_server_action_11"),
        ("base.automation", 18, "automation_18"),
        ("ir.actions.server", 1129, "automation_server_action_18"),
        ("base.automation", 20, "automation_20"),
        ("ir.actions.server", 1136, "automation_server_action_20"),
        ("base.automation", 27, "automation_27"),
        ("ir.actions.server", 1298, "automation_server_action_27"),
        ("base.automation", 28, "automation_28"),
        ("ir.actions.server", 1299, "automation_server_action_28"),
        ("ir.cron", 57, "cron_57"),
        ("ir.actions.server", 1128, "cron_server_action_57"),
        ("ir.cron", 62, "cron_62"),
        ("ir.actions.server", 1160, "cron_server_action_62"),
        ("ir.cron", 70, "cron_70"),
        ("ir.actions.server", 1291, "cron_server_action_70"),
        ("ir.actions.server", 1113, "server_action_1113"),
        ("ir.actions.server", 1116, "server_action_1116"),
        ("ir.actions.server", 1133, "server_action_1133"),
        ("ir.actions.server", 1135, "server_action_1135"),
        ("ir.actions.server", 1310, "server_action_1310"),
        ("ir.actions.server", 1311, "server_action_1311"),
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

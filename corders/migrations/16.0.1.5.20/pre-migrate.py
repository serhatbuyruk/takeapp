"""Adopt technical actions that were originally created in the UI."""


def migrate(cr, version):
    module = "corders"
    source_tables = {
        "base.automation": "base_automation",
        "ir.actions.server": "ir_act_server",
        "ir.cron": "ir_cron",
    }
    rows = [
        ("base.automation", 13, "automation_13"),
        ("ir.actions.server", 1110, "automation_server_action_13"),
        ("base.automation", 14, "automation_14"),
        ("ir.actions.server", 1112, "automation_server_action_14"),
        ("base.automation", 15, "automation_15"),
        ("ir.actions.server", 1114, "automation_server_action_15"),
        ("base.automation", 16, "automation_16"),
        ("ir.actions.server", 1119, "automation_server_action_16"),
        ("base.automation", 17, "automation_17"),
        ("ir.actions.server", 1122, "automation_server_action_17"),
        ("base.automation", 19, "automation_19"),
        ("ir.actions.server", 1134, "automation_server_action_19"),
        ("base.automation", 21, "automation_21"),
        ("ir.actions.server", 1137, "automation_server_action_21"),
        ("base.automation", 22, "automation_22"),
        ("ir.actions.server", 1138, "automation_server_action_22"),
        ("base.automation", 23, "automation_23"),
        ("ir.actions.server", 1144, "automation_server_action_23"),
        ("base.automation", 24, "automation_24"),
        ("ir.actions.server", 1145, "automation_server_action_24"),
        ("base.automation", 25, "automation_25"),
        ("ir.actions.server", 1290, "automation_server_action_25"),
        ("base.automation", 29, "automation_29"),
        ("ir.actions.server", 1301, "automation_server_action_29"),
        ("ir.cron", 54, "cron_54"),
        ("ir.actions.server", 1118, "cron_server_action_54"),
        ("ir.cron", 56, "cron_56"),
        ("ir.actions.server", 1121, "cron_server_action_56"),
        ("ir.cron", 61, "cron_61"),
        ("ir.actions.server", 1159, "cron_server_action_61"),
        ("ir.cron", 63, "cron_63"),
        ("ir.actions.server", 1161, "cron_server_action_63"),
        ("ir.cron", 64, "cron_64"),
        ("ir.actions.server", 1163, "cron_server_action_64"),
        ("ir.cron", 69, "cron_69"),
        ("ir.actions.server", 1285, "cron_server_action_69"),
        ("ir.actions.server", 1164, "server_action_1164"),
        ("ir.actions.server", 1281, "server_action_1281"),
        ("ir.actions.server", 1282, "server_action_1282"),
        ("ir.actions.server", 1283, "server_action_1283"),
        ("ir.actions.server", 1284, "server_action_1284"),
        ("ir.actions.server", 1286, "server_action_1286"),
        ("ir.actions.server", 1287, "server_action_1287"),
        ("ir.actions.server", 1288, "server_action_1288"),
        ("ir.actions.server", 1289, "server_action_1289"),
        ("ir.actions.server", 1296, "server_action_1296"),
        ("ir.actions.server", 1300, "server_action_1300"),
        ("ir.actions.server", 1302, "server_action_1302"),
        ("ir.actions.server", 1303, "server_action_1303"),
        ("ir.actions.server", 1304, "server_action_1304"),
        ("ir.actions.server", 1305, "server_action_1305"),
        ("ir.actions.server", 1306, "server_action_1306"),
        ("ir.actions.server", 1307, "server_action_1307"),
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

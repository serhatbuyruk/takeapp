"""Adopt website menus, redirect, and theme access created in the UI."""


def migrate(cr, version):
    rows = [
        ("website.menu", 4, "menu_root", "website_menu"),
        ("website.menu", 181, "menu_courier_home", "website_menu"),
        ("website.menu", 192, "menu_history", "website_menu"),
        ("website.menu", 182, "menu_available_hours", "website_menu"),
        ("website.menu", 196, "menu_payments", "website_menu"),
        ("website.menu", 199, "menu_break", "website_menu"),
        ("website.menu", 183, "menu_support", "website_menu"),
        ("website.menu", 200, "menu_authorized_company", "website_menu"),
        ("website.menu", 203, "menu_announcements", "website_menu"),
        ("website.menu", 204, "menu_notifications", "website_menu"),
        ("website.menu", 186, "menu_profile", "website_menu"),
        ("website.menu", 188, "menu_privacy", "website_menu"),
        ("website.menu", 202, "menu_explicit_consent", "website_menu"),
        ("website.rewrite", 2, "rewrite_home_to_root", "website_rewrite"),
        ("ir.model.access", 1518, "access_theme_ir_attachment", "ir_model_access"),
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
                 VALUES ('kuryetec_website', %s, %s, %s,
                         FALSE, 1, 1, NOW(), NOW())
            ON CONFLICT (module, name) DO UPDATE
                    SET model = EXCLUDED.model,
                        res_id = EXCLUDED.res_id,
                        noupdate = FALSE,
                        write_uid = 1,
                        write_date = NOW()
            """,
            (name, model, res_id),
        )

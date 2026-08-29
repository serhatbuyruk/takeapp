"""Installation hooks for adopting Website Editor pages."""


def pre_init_hook(cr):
    module = "kuryetec_website"
    source_tables = {
        "ir.ui.view": "ir_ui_view",
        "website.page": "website_page",
    }
    rows = [
        ("ir.ui.view", 488, "website_view_488"),
        ("website.page", 4, "website_page_4"),
        ("ir.ui.view", 2149, "website_view_2149"),
        ("website.page", 40, "website_page_40"),
        ("ir.ui.view", 2169, "website_view_2169"),
        ("website.page", 48, "website_page_48"),
        ("ir.ui.view", 2180, "website_view_2180"),
        ("website.page", 50, "website_page_50"),
        ("ir.ui.view", 2524, "website_view_2524"),
        ("website.page", 55, "website_page_55"),
        ("ir.ui.view", 3061, "website_view_3061"),
        ("website.page", 59, "website_page_59"),
        ("ir.ui.view", 3363, "website_view_3363"),
        ("website.page", 60, "website_page_60"),
        ("ir.ui.view", 3648, "website_view_3648"),
        ("website.page", 61, "website_page_61"),
        ("ir.ui.view", 4389, "website_view_4389"),
        ("website.page", 97, "website_page_97"),
        ("ir.ui.view", 4390, "website_view_4390"),
        ("website.page", 98, "website_page_98"),
        ("ir.ui.view", 4440, "website_view_4440"),
        ("website.page", 99, "website_page_99"),
        ("ir.ui.view", 4441, "website_view_4441"),
        ("website.page", 100, "website_page_100"),
        ("ir.ui.view", 4442, "website_view_4442"),
        ("website.page", 101, "website_page_101"),
        ("ir.ui.view", 4444, "website_view_4444"),
        ("website.page", 103, "website_page_103"),
        ("ir.ui.view", 4456, "website_view_4456"),
        ("website.page", 104, "website_page_104"),
        ("ir.ui.view", 4457, "website_view_4457"),
        ("website.page", 105, "website_page_105"),
        ("ir.ui.view", 4459, "website_view_4459"),
        ("website.page", 107, "website_page_107"),
        ("ir.ui.view", 4464, "website_view_4464"),
        ("website.page", 108, "website_page_108"),
        ("ir.ui.view", 4466, "website_view_4466"),
        ("website.page", 109, "website_page_109"),
        ("ir.ui.view", 4467, "website_view_4467"),
        ("website.page", 110, "website_page_110"),
        ("ir.ui.view", 4472, "website_view_4472"),
        ("website.page", 111, "website_page_111"),
        ("ir.ui.view", 4473, "website_view_4473"),
        ("website.page", 112, "website_page_112"),
        ("ir.ui.view", 4474, "website_view_4474"),
        ("website.page", 113, "website_page_113"),
        ("ir.ui.view", 4475, "website_view_4475"),
        ("website.page", 114, "website_page_114"),
        ("ir.ui.view", 4519, "website_view_4519"),
        ("website.page", 115, "website_page_115"),
        ("ir.ui.view", 4520, "website_view_4520"),
        ("website.page", 116, "website_page_116"),
        ("ir.ui.view", 4521, "website_view_4521"),
        ("website.page", 117, "website_page_117"),
        ("ir.ui.view", 4523, "website_view_4523"),
        ("website.page", 118, "website_page_118"),
        ("ir.ui.view", 5111, "website_view_5111"),
        ("website.page", 119, "website_page_119"),
        ("ir.ui.view", 5112, "website_view_5112"),
        ("website.page", 120, "website_page_120"),
        ("ir.ui.view", 5113, "website_view_5113"),
        ("website.page", 121, "website_page_121"),
        ("ir.ui.view", 5114, "website_view_5114"),
        ("website.page", 122, "website_page_122"),
        ("ir.ui.view", 5118, "website_view_5118"),
        ("website.page", 123, "website_page_123"),
        ("ir.ui.view", 5119, "website_view_5119"),
        ("website.page", 124, "website_page_124"),
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
            VALUES (%s, %s, %s, %s, FALSE, 1, 1, NOW(), NOW())
            ON CONFLICT (module, name) DO UPDATE
                    SET model = EXCLUDED.model,
                        res_id = EXCLUDED.res_id,
                        noupdate = FALSE,
                        write_uid = 1,
                        write_date = NOW()
            """,
            (module, name, model, res_id),
        )

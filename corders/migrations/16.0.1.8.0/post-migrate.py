"""Spread minute-based jobs to avoid a synchronized database load spike."""


def migrate(cr, version):
    offsets = {
        "cron_54": 0,
        "cron_56": 10,
        "cron_61": 20,
        "cron_63": 45,
        "cron_64": 55,
    }
    for xmlid, seconds in offsets.items():
        cr.execute(
            """
            UPDATE ir_cron
               SET nextcall = date_trunc(
                                  'minute',
                                  GREATEST(nextcall, timezone('UTC', now()))
                              )
                              + interval '1 minute'
                              + make_interval(secs => %s)
             WHERE id = (
                 SELECT res_id
                   FROM ir_model_data
                  WHERE module = 'corders'
                    AND name = %s
                    AND model = 'ir.cron'
             )
            """,
            (seconds, xmlid),
        )

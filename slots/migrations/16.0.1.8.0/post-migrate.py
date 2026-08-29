"""Spread minute-based jobs to avoid a synchronized database load spike."""


def migrate(cr, version):
    offsets = {
        "cron_57": 30,
        "cron_62": 40,
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
                  WHERE module = 'slots'
                    AND name = %s
                    AND model = 'ir.cron'
             )
            """,
            (seconds, xmlid),
        )

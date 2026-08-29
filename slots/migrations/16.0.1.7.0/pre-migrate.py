"""Create indexes used by the active-slot scheduled actions."""


def migrate(cr, version):
    cr.execute(
        """
        CREATE INDEX IF NOT EXISTS slots_profile_active_dates_idx
            ON slots_profile (active_status, start_date, end_date)
        """
    )

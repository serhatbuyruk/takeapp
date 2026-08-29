"""Create indexes used by courier assignment and integration lookups."""


def migrate(cr, version):
    statements = [
        """
        CREATE INDEX IF NOT EXISTS corders_profile_kurye_status_idx
            ON corders_profile (kurye, siparis_durumu)
        """,
        """
        CREATE INDEX IF NOT EXISTS corders_profile_kurye_delivery_date_idx
            ON corders_profile
               (kurye, kurye_siparis_durumu, siparis_tarihi)
        """,
        """
        CREATE INDEX IF NOT EXISTS corders_profile_store_date_idx
            ON corders_profile (magaza, siparis_tarihi)
        """,
        """
        CREATE INDEX IF NOT EXISTS corders_profile_alert_lookup_idx
            ON corders_profile
               (siparis_tarihi, kurye_siparis_durumu, siparis_durumu)
        """,
        """
        CREATE INDEX IF NOT EXISTS corders_profile_sepettakip_order_idx
            ON corders_profile (sepettakip_order_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS corders_profile_yeppos_order_idx
            ON corders_profile (yeppos_order_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS corders_profile_adisyo_order_idx
            ON corders_profile (adisyo_integration_order_id)
        """,
        """
        CREATE INDEX IF NOT EXISTS res_partner_courier_location_idx
            ON res_partner (user_role, konum_online, son_konum_zamani)
        """,
    ]
    for statement in statements:
        cr.execute(statement)

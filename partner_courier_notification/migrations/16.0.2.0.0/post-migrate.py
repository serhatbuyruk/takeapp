def migrate(cr, version):
    """Keep historical OneSignal deliveries readable after the provider split."""
    cr.execute("""
        UPDATE partner_courier_notification
           SET provider = 'onesignal'
         WHERE provider IS NULL
    """)
    cr.execute("""
        UPDATE partner_courier_notification_recipient
           SET provider = 'onesignal',
               device_token = player_id
         WHERE provider IS NULL
            OR device_token IS NULL
    """)

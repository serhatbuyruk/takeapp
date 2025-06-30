{
    "name": "IMAP Mail Fetcher Full",
    "version": "1.0",
    "depends": ["base", "iap_mail"],
    "author": "Your Name",
    "category": "Tools",
    "description": "IMAP mailleri elle ya da scheduled action ile çeker.",
    "data": [
        "security/ir.model.access.csv",
        "views/imap_fetcher_views.xml",
        "data/ir_cron.xml"
    ],
    "installable": True
}

# Process Management & Upgrade Rule

- **Automatic Service Restart & Module Upgrade**:
  After completing work on a module, automatically perform service restart and module upgrade based on the active database configuration.
- **Dynamic Config & DB Detection**:
  Detect active database and config file (e.g., `/etc/odoo16-<dbname>.conf`), read `http_port` and `gevent_port`, and execute:
  1. Service restart: `systemctl restart <service_name>`
  2. Module upgrade: `sudo -u odoo /odoo/odoo16/odoo-venv/bin/python3 /var/lib/odoo/odoo-bin -c <conf_path> -d <dbname> -u <module_name> --stop-after-init --http-port=<http_port> --gevent-port=<gevent_port>`

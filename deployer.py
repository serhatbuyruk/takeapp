#!/bin/python

import subprocess
from time import sleep

DB_NAME = ""
DOMAIN = ""
HTTP_PORT = ""
GEVENT_PORT = ""

ODOO_VERSION = "odoo16"

conf_content = """
[options]
proxy_mode = True
addons_path = /var/lib/odoo/odoo/addons, /var/lib/odoo/addons, /odoo/odoo16/odoo-custom-addons
admin_passwd = lkkw-ctg7-ffff
db_host = False
db_port = False
db_user = odoo
db_password = False
db_maxconn = 80
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 240
limit_time_real = 480
limit_time_real_cron = 120
workers = 2

"""


def create_conf():
    global conf_content
    conf_content = (
        conf_content
        + f"dbfilter = {DB_NAME}\n"
        + f"http_port = {HTTP_PORT}\n"
        + f"gevent_port = {GEVENT_PORT}\n"
        + f"logfile = /var/log/odoo/{ODOO_VERSION}-{DB_NAME}.log"
    )

    with open(f'/etc/{ODOO_VERSION}-{DB_NAME}.conf', 'w') as f:
        f.write(conf_content)


def create_service():
    service_content = f"""
[Unit]
Description={ODOO_VERSION}-{DB_NAME}
Requires=postgresql.service
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo-{DB_NAME}
PermissionsStartOnly=true
User=odoo
Group=odoo
ExecStart=/odoo/odoo16/odoo-venv/bin/python3 /var/lib/odoo/odoo-bin -c /etc/{ODOO_VERSION}-{DB_NAME}.conf
StandardOutput=journal+console
        
[Install]
WantedBy=multi-user.target
"""
    with open(f"/etc/systemd/system/{ODOO_VERSION}-{DB_NAME}.service", 'w') as f:
        f.write(service_content)

    subprocess.run(['sudo', 'systemctl', 'enable', '--now', f'{ODOO_VERSION}-{DB_NAME}'])


def create_nginx():
    first_setup = f"""
server {{
    listen 80;
    server_name {DOMAIN};
    include snippets/letsencrypt.conf;
}}
"""

    with open(f"/etc/nginx/sites-available/{DOMAIN}", 'w') as f:
        f.write(first_setup)

    subprocess.run(['sudo', 'ln', '-s', f'/etc/nginx/sites-available/{DOMAIN}', '/etc/nginx/sites-enabled/'])
    subprocess.run(['nginx', '-t'])
    subprocess.run(['sudo', 'systemctl', 'restart', 'nginx'])
    subprocess.run(
        [
            'sudo',
            'certbot',
            '--nginx',
            '--agree-tos',
            '--email',
            'info@autoronics.com',
            '--redirect',
            '--hsts',
            '-d',
            f'{DOMAIN}',
        ]
    )

    if "www" not in DOMAIN:
        nginx_conf = f"""
upstream odooserver{DB_NAME}{{
    server 127.0.0.1:{HTTP_PORT};
}}

upstream odoochat{DB_NAME}{{
    server 127.0.0.1:{GEVENT_PORT};
}}

map $http_upgrade $connection_upgrade {{
  default upgrade;
  ''      close;
}}

# http -> https
server {{
  listen 80;
  server_name {DOMAIN};
  rewrite ^(.*) https://$host$1 permanent;
}}


server {{
listen 443 ssl http2;
server_name {DOMAIN};

proxy_read_timeout 720s;
proxy_connect_timeout 720s;
proxy_send_timeout 720s;

# Proxy Headers
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
add_header Content-Security-Policy upgrade-insecure-requests;

#SSL CERTICATION
ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem; # managed by Certbot
ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem; # managed by Certbot
ssl_trusted_certificate /etc/letsencrypt/live/{DOMAIN}/chain.pem;
include snippets/ssl.conf;
include snippets/letsencrypt.conf;

# Specifies the maximum accepted body size of a client request,
# as indicated by the request header Content-Length.
client_max_body_size 200m;

# increase proxy buffer to handle some odoo web requests
proxy_buffers 16 64k;
proxy_buffer_size 128k;


# log files
access_log /var/log/nginx/odoo.access.log;
error_log /var/log/nginx/odoo.error.log;


# Redirect websocket requests to odoo gevent port
  location /websocket {{
    proxy_http_version 1.1;
    proxy_pass http://odoochat{DB_NAME};
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Connection $connection_upgrade;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
  }}
 
  # Redirect requests to odoo backend server
  location / {{
    # Add Headers for odoo proxy mode
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade; 
    proxy_set_header Connection "upgrade";
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_redirect off;
    proxy_pass http://odooserver{DB_NAME};
  }}
 
  # common gzip
  gzip_types text/css text/scss text/plain text/xml application/xml application/json application/javascript;
  gzip on;
}}

"""
    else:
        domain_woutw = DOMAIN.lstrip("www.")
        subprocess.run(
          [
              'sudo',
              'certbot',
              '--nginx',
              '--agree-tos',
              '--email',
              'info@autoronics.com',
              '--redirect',
              '--hsts',
              '-d',
              f'{domain_woutw}',
          ]
        )
        nginx_conf = f"""
upstream odooserver{DB_NAME}{{
    server 127.0.0.1:{HTTP_PORT};
}}

upstream odoochat{DB_NAME}{{
    server 127.0.0.1:{GEVENT_PORT};
}}

map $http_upgrade $connection_upgrade {{
  default upgrade;
  ''      close;
}}

#HTTP -> HTTPS
server {{
    listen 80;
    server_name {domain_woutw} {DOMAIN};
    rewrite ^(.*) https://$host$1 permanent;
}}

server {{
listen 443 ssl http2;
server_name {domain_woutw};

proxy_read_timeout 720s;
proxy_connect_timeout 720s;
proxy_send_timeout 720s;

# Proxy Headers
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
add_header Content-Security-Policy upgrade-insecure-requests;

#SSL CERTICATION
ssl_certificate /etc/letsencrypt/live/{domain_woutw}/fullchain.pem; # managed by Certbot
ssl_certificate_key /etc/letsencrypt/live/{domain_woutw}/privkey.pem; # managed by Certbot
ssl_trusted_certificate /etc/letsencrypt/live/{domain_woutw}/chain.pem;
include snippets/ssl.conf;
include snippets/letsencrypt.conf;

# Specifies the maximum accepted body size of a client request,
# as indicated by the request header Content-Length.
client_max_body_size 200m;

# increase proxy buffer to handle some odoo web requests
proxy_buffers 16 64k;
proxy_buffer_size 128k;


# log files
access_log /var/log/nginx/odoo.access.log;
error_log /var/log/nginx/odoo.error.log;


# Redirect websocket requests to odoo gevent port
  location /websocket {{
    proxy_http_version 1.1;
    proxy_pass http://odoochat{DB_NAME};
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Connection $connection_upgrade;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
  }}
 
  # Redirect requests to odoo backend server
  location / {{
    # Add Headers for odoo proxy mode
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade; 
    proxy_set_header Connection "upgrade";
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_redirect off;
    proxy_pass http://odooserver{DB_NAME};
  }}
 
  # common gzip
  gzip_types text/css text/scss text/plain text/xml application/xml application/json application/javascript;
  gzip on;
}}

server {{
listen 443 ssl http2;
server_name {DOMAIN};

proxy_read_timeout 720s;
proxy_connect_timeout 720s;
proxy_send_timeout 720s;

# Proxy Headers
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
add_header Content-Security-Policy upgrade-insecure-requests;

#SSL CERTICATION
ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem; # managed by Certbot
ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem; # managed by Certbot
ssl_trusted_certificate /etc/letsencrypt/live/{DOMAIN}/chain.pem;
include snippets/ssl.conf;
include snippets/letsencrypt.conf;

# Specifies the maximum accepted body size of a client request,
# as indicated by the request header Content-Length.
client_max_body_size 200m;

# increase proxy buffer to handle some odoo web requests
proxy_buffers 16 64k;
proxy_buffer_size 128k;


# log files
access_log /var/log/nginx/odoo.access.log;
error_log /var/log/nginx/odoo.error.log;


# Redirect websocket requests to odoo gevent port
  location /websocket {{
    proxy_http_version 1.1;
    proxy_pass http://odoochat{DB_NAME};
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Connection $connection_upgrade;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
  }}
 
  # Redirect requests to odoo backend server
  location / {{
    # Add Headers for odoo proxy mode
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade; 
    proxy_set_header Connection "upgrade";
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_redirect off;
    proxy_pass http://odooserver{DB_NAME};
  }}
 
  # common gzip
  gzip_types text/css text/scss text/plain text/xml application/xml application/json application/javascript;
  gzip on;
}}

"""

    with open(f"/etc/nginx/sites-available/{DOMAIN}", 'w') as f:
        f.write(nginx_conf)

    subprocess.run(['sudo', 'systemctl', 'restart', f'{ODOO_VERSION}-{DB_NAME}'])
    subprocess.run(['nginx', '-t'])
    sleep(5)
    subprocess.run(['sudo', 'systemctl', 'restart', 'nginx'])


if __name__ == "__main__":
    DB_NAME = input("Enter db name: ")
    HTTP_PORT = input("Enter Http Port: ")
    GEVENT_PORT = input("Enter Gevent Port: ")
    DOMAIN = input("Enter domain: ")

    create_conf()
    create_service()
    create_nginx()

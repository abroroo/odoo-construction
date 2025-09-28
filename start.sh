#!/bin/bash

# Create dynamic Odoo configuration
cat > /etc/odoo/odoo.conf << EOF
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
data_dir = /var/lib/odoo
db_host = ${HOST}
db_port = ${DB_PORT}
db_user = ${USER}
db_password = ${PASSWORD}
admin_passwd = ${ADMIN_PASSWORD:-admin123}
proxy_mode = True
workers = 1
max_cron_threads = 1
limit_memory_hard = 1073741824
limit_memory_soft = 805306368
list_db = False
without_demo = True
log_level = info
EOF

# Start Odoo
exec odoo
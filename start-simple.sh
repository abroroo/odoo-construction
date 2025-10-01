#!/bin/bash
set -e

echo "=== Odoo 16 Startup for Railway ==="

# Railway PostgreSQL configuration
DB_HOST="${PGHOST:-postgres.railway.internal}"
DB_PORT="${PGPORT:-5432}"
DB_USER="${PGUSER:-postgres}"
DB_PASSWORD="${PGPASSWORD:-REPLACE_WITH_YOUR_PASSWORD}"
DB_NAME="${PGDATABASE:-railway}"
HTTP_PORT="${PORT:-8080}"

echo "Starting Odoo..."
echo "DB_HOST: $DB_HOST"
echo "DB_NAME: $DB_NAME"
echo "HTTP_PORT: $HTTP_PORT"

# Create config file
cat > /tmp/odoo.conf << EOF
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
data_dir = /var/lib/odoo
db_host = $DB_HOST
db_port = $DB_PORT
db_user = $DB_USER
db_password = $DB_PASSWORD
database = $DB_NAME
dbfilter = .*
list_db = False
proxy_mode = True
workers = 2
max_cron_threads = 1
without_demo = all
http_port = $HTTP_PORT
xmlrpc_port = $HTTP_PORT
log_level = info
EOF

echo "Starting Odoo 16 (which allows postgres user)..."

# For Odoo 16, we can use command line parameters directly
exec odoo \
    --db_host=$DB_HOST \
    --db_port=$DB_PORT \
    --db_user=$DB_USER \
    --db_password=$DB_PASSWORD \
    --database=$DB_NAME \
    --http-port=$HTTP_PORT \
    --proxy-mode \
    --without-demo=all \
    --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
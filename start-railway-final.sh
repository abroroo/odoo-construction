#!/bin/bash
set -e

echo "=== Railway Odoo Startup ==="
echo "Waiting for database variables..."
sleep 2

# Railway provides these variables automatically
DB_HOST="${PGHOST:-postgres.railway.internal}"
DB_PORT="${PGPORT:-5432}"
DB_USER="${PGUSER:-postgres}"
DB_PASSWORD="${PGPASSWORD}"
DB_NAME="${PGDATABASE:-railway}"
HTTP_PORT="${PORT:-8080}"

# Check if we have the required variables
if [ -z "$DB_PASSWORD" ]; then
    echo "ERROR: Database password not found!"
    echo "Available environment variables:"
    env | sort
    exit 1
fi

echo "Starting Odoo with Railway database..."
echo "DB_HOST: $DB_HOST"
echo "DB_NAME: $DB_NAME"
echo "HTTP_PORT: $HTTP_PORT"

# Create a simple config file
cat > /tmp/odoo-railway.conf << EOF
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
data_dir = /var/lib/odoo
db_host = $DB_HOST
db_port = $DB_PORT
db_user = $DB_USER
db_password = $DB_PASSWORD
database = $DB_NAME
db_name = $DB_NAME
dbfilter = ^${DB_NAME}\$
list_db = False
proxy_mode = True
workers = 2
max_cron_threads = 1
without_demo = all
http_port = $HTTP_PORT
xmlrpc_port = $HTTP_PORT
log_level = info
limit_time_real = 120
limit_time_cpu = 60
EOF

echo "Configuration file created, starting Odoo..."

# Start Odoo with the config file
exec odoo -c /tmp/odoo-railway.conf
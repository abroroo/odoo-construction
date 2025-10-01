#!/bin/bash
set -e

echo "=== Railway Odoo 16 Deployment ==="
echo "Odoo 16 allows postgres user, so we can proceed..."

# Use Railway's PostgreSQL environment variables
DB_HOST="${PGHOST:-localhost}"
DB_PORT="${PGPORT:-5432}"
DB_USER="${PGUSER:-postgres}"
DB_PASSWORD="${PGPASSWORD}"
DB_NAME="${PGDATABASE:-railway}"
HTTP_PORT="${PORT:-8080}"

echo "Configuration:"
echo "  DB_HOST: $DB_HOST"
echo "  DB_PORT: $DB_PORT"
echo "  DB_USER: $DB_USER"
echo "  DB_NAME: $DB_NAME"
echo "  HTTP_PORT: $HTTP_PORT"

# Start Odoo with the configuration
exec odoo \
    --db_host="$DB_HOST" \
    --db_port="$DB_PORT" \
    --db_user="$DB_USER" \
    --db_password="$DB_PASSWORD" \
    --database="$DB_NAME" \
    --http-port="$HTTP_PORT" \
    --proxy-mode \
    --without-demo=all \
    --workers=2 \
    --max-cron-threads=1 \
    --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
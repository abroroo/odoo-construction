#!/bin/bash

# Railway-specific startup script with debug logging
echo "=== Railway Environment Debug ==="
echo "DATABASE_URL: ${DATABASE_URL}"
echo "PGDATABASE: ${PGDATABASE}"
echo "PGHOST: ${PGHOST}"
echo "PGPASSWORD: ${PGPASSWORD}"
echo "PGPORT: ${PGPORT}"
echo "PGUSER: ${PGUSER}"
echo "PORT: ${PORT}"
echo "RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT}"
echo "============================="

# Railway provides these PostgreSQL variables automatically
# Use them directly without quotes in variable names
DB_HOST=${PGHOST:-postgres.railway.internal}
DB_PORT=${PGPORT:-5432}
DB_USER=${PGUSER:-postgres}
DB_PASSWORD=${PGPASSWORD}
DB_NAME=${PGDATABASE:-railway}
HTTP_PORT=${PORT:-8069}

echo "=== Resolved Database Config ==="
echo "DB_HOST: $DB_HOST"
echo "DB_PORT: $DB_PORT"
echo "DB_USER: $DB_USER"
echo "DB_NAME: $DB_NAME"
echo "HTTP_PORT: $HTTP_PORT"
echo "DB_PASSWORD length: ${#DB_PASSWORD}"
echo "============================="

# Check if password exists
if [ -z "$DB_PASSWORD" ]; then
    echo "ERROR: Database password not found!"
    echo "Checking alternative variables..."
    echo "PASSWORD var: ${PASSWORD}"
    echo "HOST var: ${HOST}"
    echo "USER var: ${USER}"
    # Try alternative variable names
    DB_PASSWORD=${PASSWORD}
    DB_HOST=${HOST:-$DB_HOST}
    DB_USER=${USER:-$DB_USER}
fi

# Start Odoo with the resolved configuration
odoo \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons \
  --data-dir=/var/lib/odoo \
  --db_host="$DB_HOST" \
  --db_port="$DB_PORT" \
  --db_user="$DB_USER" \
  --db_password="$DB_PASSWORD" \
  --db_name="$DB_NAME" \
  --admin-passwd="admin123" \
  --proxy-mode \
  --workers=1 \
  --max-cron-threads=1 \
  --without-demo=all \
  --http-port="$HTTP_PORT" \
  --log-level=info
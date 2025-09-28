#!/bin/bash

# Debug: Print environment variables
echo "=== Environment Variables ==="
echo "HOST: $HOST"
echo "DB_PORT: $DB_PORT"
echo "USER: $USER"
echo "DB_NAME: $DB_NAME"
echo "============================="

# Start Odoo with proper environment variable expansion
odoo \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons \
  --data-dir=/var/lib/odoo \
  --db_host="$HOST" \
  --db_port="$DB_PORT" \
  --db_user="$USER" \
  --db_password="$PASSWORD" \
  --admin-passwd=admin123 \
  --proxy-mode \
  --workers=1 \
  --max-cron-threads=1 \
  --without-demo \
  --log-level=info
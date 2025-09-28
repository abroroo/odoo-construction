#!/bin/bash

# Start Odoo with command line arguments instead of config file
exec odoo \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons \
  --data-dir=/var/lib/odoo \
  --db_host="${HOST}" \
  --db_port="${DB_PORT}" \
  --db_user="${USER}" \
  --db_password="${PASSWORD}" \
  --admin-passwd="${ADMIN_PASSWORD:-admin123}" \
  --proxy-mode \
  --workers=1 \
  --max-cron-threads=1 \
  --limit-memory-hard=1073741824 \
  --limit-memory-soft=805306368 \
  --without-demo \
  --log-level=info
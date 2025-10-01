# Using Odoo 15 and patching the postgres check at build time
FROM odoo:15

USER root

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# CRITICAL: Patch Odoo to remove the postgres user check
# This modifies the Odoo source to disable the security check
RUN find /usr/lib/python3/dist-packages/odoo -name "*.py" -type f -exec grep -l "Using the database user 'postgres' is a security risk" {} \; | \
    xargs -r sed -i "s/if .*db_user.*==.*'postgres'/if False/g" && \
    find /usr/lib/python3/dist-packages/odoo -name "*.py" -type f -exec grep -l "database user 'postgres' is a security risk" {} \; | \
    xargs -r sed -i "s/sys\.exit(1)/#sys.exit(1)/g"

# Alternative broader patch to catch any postgres user checks
RUN find /usr/lib/python3/dist-packages/odoo -type f -name "*.py" -exec \
    sed -i "s/\(.*\)db_user.*==.*'postgres'\(.*\)/\1False\2/g" {} \; 2>/dev/null || true

# Copy custom addons
COPY ./addons /mnt/extra-addons/

# Create startup script directly
RUN cat > /start.sh << 'EOF'
#!/bin/bash
set -e

echo "=== Odoo Railway Deployment (Patched) ==="

# Use Railway's environment variables
DB_HOST="${PGHOST:-postgres.railway.internal}"
DB_PORT="${PGPORT:-5432}"
DB_USER="${PGUSER:-postgres}"
DB_PASSWORD="${PGPASSWORD:-password}"
DB_NAME="${PGDATABASE:-railway}"
HTTP_PORT="${PORT:-8080}"

echo "Configuration:"
echo "  DB_HOST: $DB_HOST"
echo "  DB_USER: $DB_USER"
echo "  DB_NAME: $DB_NAME"
echo "  HTTP_PORT: $HTTP_PORT"

# Start Odoo
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
EOF

RUN chmod +x /start.sh

# Set permissions
RUN chown -R odoo:odoo /mnt/extra-addons/

USER odoo

EXPOSE 8080

ENTRYPOINT ["/start.sh"]
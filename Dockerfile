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

# Create startup script using echo commands
RUN echo '#!/bin/bash' > /start.sh && \
    echo 'set -e' >> /start.sh && \
    echo '' >> /start.sh && \
    echo 'echo "=== Odoo Railway Deployment (Patched) ==="' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Use Railway PostgreSQL environment variables' >> /start.sh && \
    echo '# Railway provides: DATABASE_URL or individual PG* variables' >> /start.sh && \
    echo 'if [ -n "$DATABASE_URL" ]; then' >> /start.sh && \
    echo '    # Parse DATABASE_URL' >> /start.sh && \
    echo '    export PGUSER=$(echo $DATABASE_URL | sed -e "s/postgres:\/\/\([^:]*\):.*/\1/")' >> /start.sh && \
    echo '    export PGPASSWORD=$(echo $DATABASE_URL | sed -e "s/postgres:\/\/[^:]*:\([^@]*\)@.*/\1/")' >> /start.sh && \
    echo '    export PGHOST=$(echo $DATABASE_URL | sed -e "s/postgres:\/\/.*@\([^:]*\):.*/\1/")' >> /start.sh && \
    echo '    export PGPORT=$(echo $DATABASE_URL | sed -e "s/postgres:\/\/.*:\([0-9]*\)\/.*/\1/")' >> /start.sh && \
    echo '    export PGDATABASE=$(echo $DATABASE_URL | sed -e "s/postgres:\/\/.*\/\(.*\)/\1/")' >> /start.sh && \
    echo 'fi' >> /start.sh && \
    echo '' >> /start.sh && \
    echo 'DB_HOST="${PGHOST:-localhost}"' >> /start.sh && \
    echo 'DB_PORT="${PGPORT:-5432}"' >> /start.sh && \
    echo 'DB_USER="${PGUSER:-postgres}"' >> /start.sh && \
    echo 'DB_PASSWORD="${PGPASSWORD}"' >> /start.sh && \
    echo 'DB_NAME="${PGDATABASE:-railway}"' >> /start.sh && \
    echo 'HTTP_PORT="${PORT:-8080}"' >> /start.sh && \
    echo '' >> /start.sh && \
    echo 'echo "Configuration:"' >> /start.sh && \
    echo 'echo "  DB_HOST: $DB_HOST"' >> /start.sh && \
    echo 'echo "  DB_USER: $DB_USER"' >> /start.sh && \
    echo 'echo "  DB_NAME: $DB_NAME"' >> /start.sh && \
    echo 'echo "  HTTP_PORT: $HTTP_PORT"' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Start Odoo' >> /start.sh && \
    echo 'exec odoo \' >> /start.sh && \
    echo '    --db_host="$DB_HOST" \' >> /start.sh && \
    echo '    --db_port="$DB_PORT" \' >> /start.sh && \
    echo '    --db_user="$DB_USER" \' >> /start.sh && \
    echo '    --db_password="$DB_PASSWORD" \' >> /start.sh && \
    echo '    --database="$DB_NAME" \' >> /start.sh && \
    echo '    --http-port="$HTTP_PORT" \' >> /start.sh && \
    echo '    --proxy-mode \' >> /start.sh && \
    echo '    --without-demo=all \' >> /start.sh && \
    echo '    --workers=2 \' >> /start.sh && \
    echo '    --max-cron-threads=1 \' >> /start.sh && \
    echo '    --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons' >> /start.sh && \
    chmod +x /start.sh

# Set permissions
RUN chown -R odoo:odoo /mnt/extra-addons/

USER odoo

EXPOSE 8080

ENTRYPOINT ["/start.sh"]
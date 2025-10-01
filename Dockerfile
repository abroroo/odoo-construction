# IMPORTANT: Using Odoo 15 to avoid postgres user security check
# Odoo 16 and 17 both have this restriction on some versions
FROM odoo:15

USER root

# Force rebuild by adding timestamp
RUN echo "Build timestamp: $(date)" > /tmp/build_time.txt

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy custom addons
COPY ./addons /mnt/extra-addons/

# Create a simple startup script
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'set -e' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo 'echo "=== Odoo 15 Railway Deployment ==="' >> /entrypoint.sh && \
    echo 'echo "Odoo version:"' >> /entrypoint.sh && \
    echo 'odoo --version' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo '# Railway PostgreSQL configuration' >> /entrypoint.sh && \
    echo 'DB_HOST="${PGHOST:-postgres.railway.internal}"' >> /entrypoint.sh && \
    echo 'DB_PORT="${PGPORT:-5432}"' >> /entrypoint.sh && \
    echo 'DB_USER="${PGUSER:-postgres}"' >> /entrypoint.sh && \
    echo 'DB_PASSWORD="${PGPASSWORD}"' >> /entrypoint.sh && \
    echo 'DB_NAME="${PGDATABASE:-railway}"' >> /entrypoint.sh && \
    echo 'HTTP_PORT="${PORT:-8080}"' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo 'echo "Configuration:"' >> /entrypoint.sh && \
    echo 'echo "  DB_HOST: $DB_HOST"' >> /entrypoint.sh && \
    echo 'echo "  DB_USER: $DB_USER"' >> /entrypoint.sh && \
    echo 'echo "  HTTP_PORT: $HTTP_PORT"' >> /entrypoint.sh && \
    echo '' >> /entrypoint.sh && \
    echo 'exec odoo \' >> /entrypoint.sh && \
    echo '    --db_host="$DB_HOST" \' >> /entrypoint.sh && \
    echo '    --db_port="$DB_PORT" \' >> /entrypoint.sh && \
    echo '    --db_user="$DB_USER" \' >> /entrypoint.sh && \
    echo '    --db_password="$DB_PASSWORD" \' >> /entrypoint.sh && \
    echo '    --database="$DB_NAME" \' >> /entrypoint.sh && \
    echo '    --http-port="$HTTP_PORT" \' >> /entrypoint.sh && \
    echo '    --proxy-mode \' >> /entrypoint.sh && \
    echo '    --without-demo=all \' >> /entrypoint.sh && \
    echo '    --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Set permissions
RUN chown -R odoo:odoo /mnt/extra-addons/

USER odoo

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
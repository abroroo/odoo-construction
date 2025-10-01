FROM odoo:17

# Set the user to root to install packages and patch
USER root

# Install additional dependencies if needed
RUN apt-get update && apt-get install -y \
    git \
    sed \
    && rm -rf /var/lib/apt/lists/*

# Patch Odoo to allow postgres user (required for Railway)
RUN sed -i "s/if params\['db_user'\] == 'postgres'/if False/" /usr/lib/python3/dist-packages/odoo/cli/server.py || true

# Copy custom addons
COPY ./addons /mnt/extra-addons/

# Copy startup scripts
COPY ./docker-entrypoint-override.sh /usr/local/bin/docker-entrypoint-override.sh
COPY ./start-railway-final.sh /usr/local/bin/start-railway-final.sh
COPY ./start.sh /usr/local/bin/start.sh

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons/
RUN chmod +x /usr/local/bin/docker-entrypoint-override.sh
RUN chmod +x /usr/local/bin/start-railway-final.sh
RUN chmod +x /usr/local/bin/start.sh

# Switch back to odoo user
USER odoo

# Expose Railway's expected port
EXPOSE 8080

# Use the final Railway startup script
ENTRYPOINT ["/usr/local/bin/docker-entrypoint-override.sh"]
CMD ["/usr/local/bin/start-railway-final.sh"]
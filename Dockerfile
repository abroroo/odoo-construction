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

# Copy startup scripts and bypass script
COPY ./start-simple.sh /usr/local/bin/start-simple.sh
COPY ./bypass-postgres-check.py /usr/local/bin/bypass-postgres-check.py

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons/
RUN chmod +x /usr/local/bin/start-simple.sh
RUN chmod +x /usr/local/bin/bypass-postgres-check.py

# Switch back to odoo user
USER odoo

# Expose Railway's expected port
EXPOSE 8080

# Use the simple startup script
CMD ["/usr/local/bin/start-simple.sh"]
FROM odoo:17

# Set the user to root to install packages
USER root

# Install additional dependencies if needed
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy custom addons
COPY ./addons /mnt/extra-addons/

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons/

# Switch back to odoo user
USER odoo

# Expose port
EXPOSE 8069

# Use entrypoint to pass environment variables directly to odoo
ENTRYPOINT ["odoo"]
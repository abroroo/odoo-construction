FROM odoo:16

# Set the user to root to install packages
USER root

# Install additional dependencies if needed
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy custom addons
COPY ./addons /mnt/extra-addons/

# Copy startup script
COPY ./start-simple.sh /usr/local/bin/start-simple.sh

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons/
RUN chmod +x /usr/local/bin/start-simple.sh

# Switch back to odoo user
USER odoo

# Expose Railway's expected port
EXPOSE 8080

# Use the simple startup script
CMD ["/usr/local/bin/start-simple.sh"]
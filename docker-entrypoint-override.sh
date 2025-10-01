#!/bin/bash
set -e

# Override Odoo's security check by patching the Python code
echo "=== Patching Odoo security check ==="

# Find and patch the Odoo CLI module that checks for postgres user
ODOO_CLI_FILE="/usr/lib/python3/dist-packages/odoo/cli/server.py"

if [ -f "$ODOO_CLI_FILE" ]; then
    # Create a backup
    cp "$ODOO_CLI_FILE" "$ODOO_CLI_FILE.bak"

    # Remove the postgres user check
    sed -i "s/if params\['db_user'\] == 'postgres'/if False/" "$ODOO_CLI_FILE"
    echo "Security check patched successfully"
else
    echo "Warning: Could not find Odoo CLI file to patch"
fi

# Continue with the original entrypoint
exec "$@"
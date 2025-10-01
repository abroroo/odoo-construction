#!/bin/bash
set -e

echo "=== Starting Odoo with Railway configuration ==="

# The patching is already done in the Dockerfile during build
# No need to patch again at runtime

# Continue with the startup script
exec "$@"
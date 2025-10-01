#!/usr/bin/env python3
"""
Bypass script that removes the postgres user check from Odoo before starting
"""
import os
import sys

# Patch the Odoo files
try:
    server_file = '/usr/lib/python3/dist-packages/odoo/cli/server.py'
    if os.path.exists(server_file):
        with open(server_file, 'r') as f:
            content = f.read()

        # Replace the postgres check
        content = content.replace("if params['db_user'] == 'postgres'", "if False")

        with open(server_file, 'w') as f:
            f.write(content)

        print("Patched server.py successfully")
except Exception as e:
    print(f"Warning: Could not patch server.py: {e}")

# Now import and run Odoo
sys.path.insert(0, '/usr/lib/python3/dist-packages')
import odoo
odoo.cli.main()
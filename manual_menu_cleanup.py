#!/usr/bin/env python3
"""
Manual Menu Cleanup Script
Run this script to clean up Odoo menus manually
and assign the current user to the construction admin group.
"""

import xmlrpc.client

# Odoo connection details
url = 'http://localhost:8069'
db = 'postgres'
username = 'admin'
password = 'admin'

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("Failed to authenticate. Check your credentials.")
    exit(1)

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print(f"Connected as user ID: {uid}")

# List of menu items to hide
menus_to_hide = [
    'mail.mail_channel_menu_root_chat',  # Discuss
    'calendar.mail_menu_calendar',  # Calendar
    'board.menu_board_root',  # Dashboards
    'sale.sale_menu_root',  # Sales
    'purchase.menu_purchase_root',  # Purchase
    'stock.menu_stock_root',  # Inventory
    'account.menu_finance',  # Invoicing
    'hr.menu_hr_root',  # Employees
    'contacts.menu_contacts',  # Contacts
    'mass_mailing.mass_mailing_menu_root',  # Email Marketing
    'survey.menu_surveys',  # Surveys
    'documents.menu_root',  # Documents
    'website.menu_website_configuration',  # Website
    'im_livechat.menu_livechat_root',  # Live Chat
    'link_tracker.link_tracker_menu_root',  # Link Tracker
    'project_todo.menu_project_todo_root',  # To-do
]

# Find and hide menus
hidden_count = 0
for menu_xml_id in menus_to_hide:
    try:
        # Try to find the menu by XML ID
        menu_data = models.execute_kw(db, uid, password, 'ir.model.data', 'search_read',
                                      [[['name', '=', menu_xml_id.split('.')[1]],
                                        ['module', '=', menu_xml_id.split('.')[0]],
                                        ['model', '=', 'ir.ui.menu']]],
                                      {'fields': ['res_id']})

        if menu_data:
            menu_id = menu_data[0]['res_id']
            # Hide the menu by setting active = False
            models.execute_kw(db, uid, password, 'ir.ui.menu', 'write',
                              [menu_id], {'active': False})
            print(f"✓ Hidden menu: {menu_xml_id}")
            hidden_count += 1
        else:
            print(f"⚠ Menu not found: {menu_xml_id}")

    except Exception as e:
        print(f"✗ Error hiding menu {menu_xml_id}: {e}")

print(f"\nMenu cleanup completed! Hidden {hidden_count} menus.")
print("\nRefresh your browser to see the changes.")

# Also try to assign current user to construction admin group
try:
    admin_group_data = models.execute_kw(db, uid, password, 'ir.model.data', 'search_read',
                                         [[['name', '=', 'group_construction_admin'],
                                           ['module', '=', 'construction_menu_config']]],
                                         {'fields': ['res_id']})

    if admin_group_data:
        group_id = admin_group_data[0]['res_id']
        # Add admin user to the group
        models.execute_kw(db, uid, password, 'res.users', 'write',
                          [uid], {'groups_id': [(4, group_id)]})
        print(f"✓ Added admin user to Construction Administrator group")
    else:
        print("⚠ Construction admin group not found")

except Exception as e:
    print(f"✗ Error assigning user to group: {e}")
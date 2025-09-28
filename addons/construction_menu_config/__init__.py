# -*- coding: utf-8 -*-

from . import models

def post_init_hook(env):
    """Hide unnecessary menu items after module installation"""

    # List of menu items to hide (make them invisible)
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
    ]

    hidden_group_id = env.ref('construction_menu_config.group_hidden_menus').id

    for menu_xml_id in menus_to_hide:
        try:
            menu = env.ref(menu_xml_id, raise_if_not_found=False)
            if menu:
                # Hide the menu by setting it to our hidden group only
                menu.write({'groups_id': [(6, 0, [hidden_group_id])]})
                print(f"Hidden menu: {menu_xml_id}")
        except Exception as e:
            # Menu doesn't exist in this Odoo installation, skip
            print(f"Menu {menu_xml_id} not found, skipping: {e}")
            continue

    # Set up role-based menu access
    setup_role_based_menus(env)

    # Assign admin user to construction admin group
    assign_admin_user(env)


def setup_role_based_menus(env):
    """Configure menu visibility based on user roles"""
    try:
        # Get construction groups
        site_manager_group = env.ref('construction_menu_config.group_construction_site_manager', raise_if_not_found=False)
        project_manager_group = env.ref('construction_menu_config.group_construction_project_manager', raise_if_not_found=False)
        admin_group = env.ref('construction_menu_config.group_construction_admin', raise_if_not_found=False)

        if not all([site_manager_group, project_manager_group, admin_group]):
            print("Construction groups not found, skipping role-based menu setup")
            return

        # Configure essential menu access
        menu_configs = [
            # Mobile Construction - Site Managers and above
            ('construction_mobile_manager.menu_mobile_construction_root', [site_manager_group.id]),

            # Construction Budget - Project Managers and above
            ('construction_budget.menu_project_budget_root', [project_manager_group.id]),

            # Project - All construction users
            ('project.menu_main_pm', [site_manager_group.id]),

            # Expenses - All construction users
            ('hr_expense.menu_hr_expense_root', [site_manager_group.id]),

            # Settings - Administrators only
            ('base.menu_administration', [admin_group.id]),

            # Apps - Administrators only
            ('base.menu_management', [admin_group.id]),
        ]

        for menu_xml_id, group_ids in menu_configs:
            try:
                menu = env.ref(menu_xml_id, raise_if_not_found=False)
                if menu:
                    menu.write({'groups_id': [(6, 0, group_ids)]})
                    print(f"Configured menu access: {menu_xml_id}")
            except Exception as e:
                print(f"Failed to configure menu {menu_xml_id}: {e}")

    except Exception as e:
        print(f"Error setting up role-based menus: {e}")


def assign_admin_user(env):
    """Assign the admin user to construction admin group"""
    try:
        admin_user = env.ref('base.user_admin', raise_if_not_found=False)
        admin_group = env.ref('construction_menu_config.group_construction_admin', raise_if_not_found=False)

        if admin_user and admin_group:
            admin_user.write({'groups_id': [(4, admin_group.id)]})
            print(f"Added admin user to Construction Administrator group")
        else:
            print("Admin user or construction admin group not found")

    except Exception as e:
        print(f"Error assigning admin user: {e}")
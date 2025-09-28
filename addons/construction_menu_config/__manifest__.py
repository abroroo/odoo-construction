# -*- coding: utf-8 -*-
{
    'name': 'Construction Menu Configuration',
    'version': '1.0.0',
    'category': 'Administration',
    'summary': 'Clean menu configuration for construction business workflow',
    'description': """
Construction Menu Configuration
==============================

Streamlines the Odoo main menu to show only essential items for construction business workflow.

**Essential Menus Kept:**
* Mobile Construction - Site manager mobile interface
* Construction Budget - Budget tracking and task creation
* Project - Project management and tasks
* Expenses - Expense entry and approval
* Settings - System administration
* Apps - Module management

**Removed Unnecessary Menus:**
* Discuss (not needed for construction workflow)
* To-do (redundant with project tasks)
* Sales (not part of internal construction management)
* Dashboards (we have custom dashboards)
* Invoicing (not needed for internal project management)
* Purchase (not part of current workflow)
* Inventory (using mock inventory in expenses)
* Employees (basic user management in Settings is sufficient)
* Link Tracker (not needed)

**Role-Based Menu Visibility:**
* Site Managers: Mobile Construction + Expenses
* Project Managers: Construction Budget + Project + Expenses
* Administrators: All menus + Settings + Apps

This creates a clean, focused interface that matches your construction user stories.
    """,
    'author': 'Construction System',
    'website': '',
    'depends': [
        'base',
        'project',
        'hr_expense',
        'construction_budget',
        'construction_mobile_manager',
    ],
    'data': [
        'data/menu_cleanup_data.xml',
        'security/construction_groups.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': 'post_init_hook',
}
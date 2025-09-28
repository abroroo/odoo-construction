{
    'name': 'Construction Budget Management',
    'version': '17.0.1.0.0',
    'category': 'Project',
    'summary': 'Budget tracking for construction projects without Enterprise accounting',
    'description': """
Construction Budget Management
==============================

This module provides comprehensive budget tracking for construction projects
specifically designed for Odoo Community Edition.

Features:
---------
* Project budget management with categories
* Budget vs actual spending tracking
* Integration with Expenses and Purchase modules
* Budget alerts and reporting
* Dashboard with budget overview
* Construction-specific budget categories
* Automatic budget calculations

Budget Categories:
------------------
* Materials (Concrete, Steel, Lumber, etc.)
* Labor (Site workers, contractors)
* Equipment (Rental, machinery)
* Overhead (Management, utilities)
* Permits & Fees

This module works entirely with Community Edition and does not require
the Enterprise Accounting module.
    """,
    'author': 'Construction Management System',
    'website': '',
    'depends': [
        'base',
        'mail',
        'project',
        'hr_expense',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/budget_categories.xml',
        'views/project_budget_views.xml',
        'views/project_views.xml',
        'views/budget_category_views.xml',
        'views/expense_views.xml',
        'views/purchase_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
        'reports/budget_reports.xml',
    ],
    'demo': [
        'demo/demo_budgets.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
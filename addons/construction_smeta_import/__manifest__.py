{
    'name': 'Construction Smeta Import',
    'version': '17.0.1.0.0',
    'category': 'Project',
    'summary': 'Import Excel smeta (budget estimates) files into construction budgets',
    'description': """
Construction Smeta Import
=========================

This module provides functionality to import Excel smeta (budget estimate) files
directly into Odoo construction project budgets.

Features:
---------
* Excel file upload with column mapping
* Support for Russian text and various Excel formats
* Automatic budget line creation
* Project selection and linking
* Data preview before import
* Error handling and validation
* Template generation for standardized imports

Supported Excel columns:
------------------------
* Category - Budget category (Materials, Labor, etc.)
* Item - Description of the budget item
* Quantity - Quantity of items
* Unit Price - Price per unit
* Total - Total amount (calculated if not provided)
* Unit of Measure - Optional unit specification

Integration:
------------
* Works with Construction Budget Management module
* Creates budget lines linked to specific projects
* Supports existing budget categories or creates new ones
* Maintains data integrity and validation

This module is specifically designed for construction companies using
smeta (budget estimate) Excel files in their project planning workflow.
    """,
    'author': 'Construction Management System',
    'website': '',
    'depends': [
        'base',
        'mail',
        'project',
        'construction_budget',
        'web',
    ],
    'external_dependencies': {
        'python': ['xlrd', 'openpyxl'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/smeta_template.xml',
        'wizard/smeta_import_wizard_views.xml',
        'views/smeta_import_views.xml',
        'views/smeta_import_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
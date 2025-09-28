# -*- coding: utf-8 -*-
{
    'name': 'Construction Batch Task Creation',
    'version': '1.0.0',
    'category': 'Project',
    'summary': 'Simple bulk task creation with copy-paste interface',
    'description': """
Construction Batch Task Creation
===============================

Replace complex Excel imports with a simple, fast batch task creation system.

Key Features:
* Simple copy-paste interface for bulk task creation
* Text format: Number|Task Name|Unit|Quantity (pipe-separated)
* Automatic task hierarchy detection (main tasks → sub-tasks)
* Dual creation: Project tasks + Budget lines
* Built-in validation and preview
* No file uploads or format matching required

Usage:
1. Navigate to Project → Batch Create Tasks
2. Select your project
3. Paste tasks in format: 1|Task Name|Unit|Quantity
4. Click Parse & Preview to validate
5. Click Create Tasks to generate everything

Example Format:
1|CONCRETE FOUNDATION WORK|M3|25.5
1.1|EXCAVATION WORK|M3|30.0
1.2|CONCRETE POURING|M3|25.5
2|STEEL REINFORCEMENT|KG|1250.0
2.1|REBAR CUTTING|KG|1250.0
2.2|REBAR INSTALLATION|KG|1250.0

Benefits:
* 10x faster than Excel imports
* No file format issues
* Instant validation and preview
* Copy directly from any source
* Clean, maintainable code
    """,
    'author': 'Construction System',
    'website': '',
    'depends': [
        'base',
        'project',
        'construction_budget',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/batch_task_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
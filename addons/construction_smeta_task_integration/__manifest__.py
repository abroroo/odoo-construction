# -*- coding: utf-8 -*-
{
    'name': 'Construction Smeta Task Integration',
    'version': '1.0.0',
    'category': 'Project',
    'summary': 'Create project tasks alongside budget lines from smeta imports',
    'description': """
Construction Smeta Task Integration
==================================

This module extends the Russian smeta import functionality to create project tasks
alongside budget lines, providing both financial tracking and project management:

Features:
* Automatically creates project.task records from smeta import
* Maintains hierarchical structure (main tasks → sub-tasks)
* Links budget lines with corresponding project tasks
* Preserves all existing budget functionality
* Enables full project management workflow

Task Creation:
* Main tasks (1, 2, 3...) become parent project tasks
* Sub-tasks (1.1, 1.2, 2.1...) become child project tasks
* Task names from "НАИМЕНОВАНИЕ РАБОТ И РЕСУРСОВ" column
* Initial status set to "To Do"
* Proper project assignment and sequencing

Integration:
* Budget lines retain expense tracking functionality
* Project tasks enable work assignment and progress tracking
* Cross-references between budget and task management
* Unified reporting across financial and operational views
    """,
    'author': 'Construction System',
    'website': '',
    'depends': [
        'base',
        'project',
        'construction_budget',
        'construction_smeta_import',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
        'views/project_budget_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
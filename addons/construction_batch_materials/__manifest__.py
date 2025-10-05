# -*- coding: utf-8 -*-
{
    'name': 'Construction Batch Materials Import',
    'version': '17.0.1.0.0',
    'category': 'Construction',
    'summary': 'Batch import construction materials from Excel/text format',
    'description': """
Construction Batch Materials Import
====================================
Import construction materials in batch from Excel format:
- Parse material data (Code|Name|Unit|Price)
- Create materials in bulk
- Support Russian smeta format
- Quick setup for demos and new projects
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': [
        'base',
        'construction_warehouse',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/batch_material_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

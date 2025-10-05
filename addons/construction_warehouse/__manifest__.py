# -*- coding: utf-8 -*-
{
    'name': 'Construction Warehouse Management',
    'version': '1.0.3',
    'category': 'Inventory',
    'summary': 'Physical warehouse inventory management for construction projects',
    'description': """
Construction Warehouse Management
================================

Physical inventory management system for construction projects with real warehouse operations.

**Core Features:**
* Project-based warehouses (each project has physical storage)
* Supplier interface for adding goods to project warehouses
* Real-time physical stock tracking (in/out/current levels)
* Site manager material consumption from warehouse
* Physical goods management (not financial tracking)

**User Workflows:**
* Suppliers: Add delivered materials to project warehouses
* Site Managers: Consume materials from warehouse for tasks
* Project Managers: Monitor warehouse stock levels across projects
* Warehouse Staff: Manage physical inventory and locations

**Key Models:**
* Project Warehouse: Physical storage locations per project
* Warehouse Stock: Current inventory levels of materials
* Material Receipt: Supplier deliveries to warehouse
* Material Consumption: Site manager usage from warehouse
* Stock Movement: All in/out transactions

Perfect for construction companies that need to track physical materials
flowing through project warehouses from suppliers to consumption.
    """,
    'author': 'Construction System',
    'website': '',
    'depends': [
        'base',
        'project',
        'stock',
        'product',
        'mail',
    ],
    'data': [
        'security/warehouse_security.xml',
        'security/ir.model.access.csv',
        'data/warehouse_data.xml',
        'views/construction_material_views.xml',
        'views/project_warehouse_views.xml',
        'views/warehouse_stock_views.xml',
        'views/material_receipt_views.xml',
        'views/material_consumption_views.xml',
        'views/quick_task_wizard_views.xml',
        'views/supplier_portal_views.xml',
        'views/phase1_simplified_views.xml',
        'views/warehouse_menus.xml',
    ],
    'demo': [
        'demo/warehouse_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
}
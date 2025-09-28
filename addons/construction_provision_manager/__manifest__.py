# -*- coding: utf-8 -*-
{
    'name': 'Construction Provision Manager',
    'version': '1.0.0',
    'category': 'Project',
    'summary': 'Materials provisioning and inventory management for construction projects',
    'description': """
Construction Provision Manager
=============================

Complete materials management system for construction projects with mobile-first design.

**Material Entry Features:**
* Project-based material assignment
* Material categories: Construction Materials, Tools, Equipment
* Pre-defined material suggestions (Cement, Steel bars, Lumber, etc.)
* Quantity and unit management
* Automatic cost calculations
* Supplier information tracking

**Project Inventory Management:**
* Real-time materials tracking per project
* Search and filter capabilities
* Quantity and price editing
* Material usage monitoring

**Quick Add Templates:**
* Pre-defined material buttons for common items
* Quick quantity increment buttons (+10, +50, +100)
* Recent materials list for fast re-ordering
* Smart suggestions based on project type

**Material History & Reporting:**
* Complete delivery log with timestamps
* Cost tracking and analysis
* Export capabilities for accounting
* Date range and material type filtering

**Mobile-First Design:**
* Large input fields for field use
* Touch-friendly number pad interface
* Barcode scanner ready (future integration)
* Offline capability indicators
* Responsive design for tablets and phones

**Integration:**
* Seamless integration with site manager expense system
* Materials become available in expense dropdowns
* Budget tracking integration
* Project cost monitoring

Perfect for provision managers who need to track materials delivery and availability
across multiple construction sites with easy mobile access.
    """,
    'author': 'Construction System',
    'website': '',
    'depends': [
        'base',
        'web',
        'project',
        'mail',
        'construction_budget',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/material_categories.xml',
        'data/common_materials.xml',
        'views/material_category_views.xml',
        'views/common_material_views.xml',
        'views/material_delivery_views.xml',
        'views/project_material_views.xml',
        'views/wizard_views.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'construction_provision_manager/static/src/css/provision_manager.css',
            'construction_provision_manager/static/src/js/material_entry.js',
            'construction_provision_manager/static/src/js/quick_add.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
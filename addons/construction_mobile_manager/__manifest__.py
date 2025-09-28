# -*- coding: utf-8 -*-
{
    'name': 'Construction Mobile Site Manager',
    'version': '1.0.0',
    'category': 'Project',
    'summary': 'Mobile-optimized interface for construction site managers',
    'description': """
Construction Mobile Site Manager
===============================

Mobile-first interface designed specifically for construction site managers working in the field.

Key Features:
* **Mobile-First Design**: Touch-friendly interface optimized for smartphones and tablets
* **Site Manager Dashboard**: Clean overview of assigned tasks and quick stats
* **Task Management**: Simple status updates (To Do → In Progress → Done)
* **Mobile Expense Entry**: Quick expense recording with photo upload
* **Responsive Design**: Works on mobile, tablet, and desktop
* **Offline-Ready**: Designed for field conditions with poor connectivity

Dashboard Features:
* My assigned tasks with status indicators
* Quick task status toggles
* Progress statistics and summaries
* Large touch buttons for easy use

Expense Management:
* Select from assigned tasks
* Material dropdown with common construction materials
* Photo upload for receipts and documentation
* One-tap expense submission

Task Details:
* Task information and progress tracking
* Budget vs actual spending overview
* Recent expense history
* Status update buttons

Navigation:
* Bottom navigation bar for mobile
* Hamburger menu for secondary functions
* Breadcrumb navigation for desktop

Target Users:
* Site managers working in the field
* Foremen tracking task progress
* Workers recording material usage
* Project supervisors monitoring progress

Benefits:
* Faster task status updates
* Real-time expense tracking
* Photo documentation for accountability
* Mobile-optimized for field conditions
* Reduced data entry time
* Better project visibility
    """,
    'author': 'Construction System',
    'website': '',
    'depends': [
        'base',
        'web',
        'project',
        'hr_expense',
        'construction_budget',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mobile_dashboard_views.xml',
        'views/mobile_expense_views.xml',
        'views/mobile_task_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'construction_mobile_manager/static/src/css/mobile_styles.css',
            'construction_mobile_manager/static/src/js/mobile_task_kanban.js',
        ],
        'web.assets_frontend': [
            'construction_mobile_manager/static/src/css/mobile_styles.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
# -*- coding: utf-8 -*-
{
    'name': 'Construction Project Manager Dashboard',
    'version': '1.0.0',
    'category': 'Project',
    'summary': 'Comprehensive dashboard for construction project managers',
    'description': """
Construction Project Manager Dashboard
=====================================

Comprehensive dashboard designed specifically for construction project managers with responsive design for both desktop and mobile use.

**Project Overview Cards:**
* Project selection dropdown for quick switching
* Visual task progress bars and completion counts
* Budget status with spent vs allocated percentages
* Real-time team activity feed with recent updates

**Task Management Board:**
* Responsive Kanban board: To Do | In Progress | Done
* Drag-and-drop functionality on desktop
* Tap-to-update interface on mobile devices
* Task cards with assigned worker and budget indicators
* Advanced filtering: by worker, date range, task category

**Budget Monitoring:**
* Category breakdown: Materials, Labor, Equipment spending
* Recent expenses list with one-click approval buttons
* Budget alerts for over-spending tasks and categories
* Export capabilities for financial reports

**Team Management:**
* Active workers overview with current task assignments
* Expense approval queue with batch processing
* Quick task assignment interface
* Worker productivity metrics

**Responsive Design:**
* Desktop: Multi-column layout with informative sidebars
* Mobile: Stacked card interface with collapsible sections
* Touch-friendly controls optimized for field use
* Information density adjusted per screen size

**Key Benefits:**
* Single-screen project oversight
* Mobile-first design for on-site management
* Real-time budget and progress tracking
* Streamlined team coordination
* Quick decision-making tools

Perfect for construction project managers who need comprehensive project oversight whether in the office or on-site.
    """,
    'author': 'Construction System',
    'website': '',
    'depends': [
        'base',
        'web',
        'project',
        'hr_expense',
        'construction_budget',
        'construction_mobile_manager',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pm_dashboard_views.xml',
        'views/pm_dashboard_kanban.xml',
        'data/dashboard_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'construction_pm_dashboard/static/src/css/pm_dashboard.css',
            'construction_pm_dashboard/static/src/css/pm_dashboard_enhanced.css',
        ],
        'web.assets_frontend': [
            'construction_pm_dashboard/static/src/css/pm_dashboard.css',
            'construction_pm_dashboard/static/src/css/pm_dashboard_enhanced.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
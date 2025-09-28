# -*- coding: utf-8 -*-
{
    'name': 'Construction Custom Branding',
    'version': '1.0.0',
    'category': 'Theme',
    'summary': 'Custom branding with blue color scheme and Onest font',
    'description': """
Construction Custom Branding
===========================

Custom branding for the construction management system with:
- Primary color: #0064FF (R0 G100 B255, C100 M60 Y0 K0, PANTONE 2175 C)
- Font family: Onest (Google Fonts)
- Clean, modern interface design
- Consistent color scheme throughout the application

This module overrides Odoo's default styling to provide a cohesive brand experience.
    """,
    'author': 'Construction System',
    'website': '',
    'depends': [
        'base',
        'web',
    ],
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'construction_custom_branding/static/src/css/simple_primary_color.css',
        ],
        'web.assets_frontend': [
            'construction_custom_branding/static/src/css/simple_primary_color.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
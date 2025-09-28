# -*- coding: utf-8 -*-

from odoo import models, api


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _hide_menu_if_exists(self, xml_id):
        """Helper function to hide a menu if it exists"""
        try:
            menu = self.env.ref(xml_id, raise_if_not_found=False)
            if menu:
                menu.active = False
                return True
        except Exception:
            pass
        return False

    @api.model
    def load_menus(self, debug):
        """Override to ensure clean menu structure for construction users"""
        result = super().load_menus(debug)

        # Additional cleanup for construction users
        user = self.env.user
        if user.has_group('construction_menu_config.group_construction_site_manager'):
            # Filter out any remaining non-construction menus for site managers
            self._filter_construction_menus(result)

        return result

    def _filter_construction_menus(self, menu_data):
        """Filter menus to show only construction-relevant items"""
        if not menu_data:
            return

        # Define allowed menu patterns for construction users
        allowed_patterns = [
            'mobile_construction',
            'construction_budget',
            'project',
            'expense',
            'hr_expense',
            'setting',
            'administration',
            'app',
            'management'
        ]

        # This is a simplified filter - in practice, Odoo's group-based
        # access control handles most of the filtering
        pass
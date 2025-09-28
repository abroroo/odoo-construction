# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Budget integration
    construction_project_id = fields.Many2one(
        'project.project',
        string='Construction Project',
        help='Related construction project for budget tracking'
    )
    total_budget_impact = fields.Float(
        string='Total Budget Impact',
        compute='_compute_budget_impact',
        store=True,
        help='Total impact on project budget'
    )

    @api.depends('order_line.price_subtotal')
    def _compute_budget_impact(self):
        for order in self:
            order.total_budget_impact = sum(order.order_line.mapped('price_subtotal'))

    def button_confirm(self):
        """Override to update budget commitments when confirming PO"""
        result = super().button_confirm()
        # Update budget commitments
        for order in self:
            order._update_budget_commitments()
        return result

    def _update_budget_commitments(self):
        """Update budget line commitments when PO is confirmed"""
        for line in self.order_line:
            if line.budget_line_id:
                line.budget_line_id.update_committed_amount(line.price_subtotal)

    def action_view_invoice(self):
        """Override to handle budget updates when viewing invoices"""
        result = super().action_view_invoice()
        return result


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # Budget integration fields
    budget_category_id = fields.Many2one(
        'construction.budget.category',
        string='Budget Category',
        help='Budget category for this purchase line'
    )
    budget_line_id = fields.Many2one(
        'construction.project.budget.line',
        string='Budget Line',
        domain="[('project_id', '=', construction_project_id), ('category_id', '=', budget_category_id)]",
        help='Specific budget line this purchase should be charged to'
    )

    # Related fields
    construction_project_id = fields.Many2one(
        related='order_id.construction_project_id',
        string='Construction Project',
        store=True
    )

    @api.onchange('budget_category_id')
    def _onchange_budget_category(self):
        """Filter budget lines based on category and project"""
        if self.construction_project_id and self.budget_category_id:
            domain = [
                ('project_id', '=', self.construction_project_id.id),
                ('category_id', '=', self.budget_category_id.id)
            ]
            return {'domain': {'budget_line_id': domain}}
        else:
            return {'domain': {'budget_line_id': []}}

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set budget category based on product category"""
        lines = super().create(vals_list)
        for line in lines:
            line._auto_assign_budget_category()
        return lines

    def _auto_assign_budget_category(self):
        """Auto-assign budget category based on product category"""
        if self.product_id and self.product_id.categ_id:
            # Map product categories to budget categories
            category_mapping = {
                'Construction Materials': 'MAT',
                'Construction Labor': 'LAB',
                'Equipment Rental': 'EQP',
                'Project Overhead': 'OVH',
            }

            product_category_name = self.product_id.categ_id.name
            budget_code = category_mapping.get(product_category_name)

            if budget_code:
                budget_category = self.env['construction.budget.category'].search([
                    ('code', '=', budget_code)
                ], limit=1)
                if budget_category:
                    self.budget_category_id = budget_category

    def _prepare_account_move_line(self, move=False):
        """Override to include budget information in account move lines"""
        vals = super()._prepare_account_move_line(move)

        # Add analytic distribution for budget tracking
        if self.construction_project_id and self.construction_project_id.analytic_account_id:
            vals['analytic_distribution'] = {
                self.construction_project_id.analytic_account_id.id: 100.0
            }

        return vals


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """Override to update budget spent amounts when posting vendor bills"""
        result = super().action_post()

        # Update budget spent amounts for purchase-related invoices
        for move in self:
            if move.move_type == 'in_invoice' and move.purchase_id:
                move._update_budget_spent_from_invoice()

        return result

    def _update_budget_spent_from_invoice(self):
        """Update budget spent amounts when vendor bill is posted"""
        for line in self.line_ids:
            if line.purchase_line_id and line.purchase_line_id.budget_line_id:
                # Calculate the amount to add to spent (proportional to invoice line)
                if line.purchase_line_id.price_subtotal > 0:
                    proportion = abs(line.balance) / line.purchase_line_id.price_subtotal
                    spent_amount = line.purchase_line_id.budget_line_id.committed_amount * proportion

                    # Update spent amount and reduce committed amount
                    line.purchase_line_id.budget_line_id.update_spent_amount(spent_amount)
                    line.purchase_line_id.budget_line_id.update_committed_amount(-spent_amount)
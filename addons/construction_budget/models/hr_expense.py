# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    # Budget integration fields
    budget_category_id = fields.Many2one(
        'construction.budget.category',
        string='Budget Category',
        help='Budget category for this expense'
    )
    project_budget_line_id = fields.Many2one(
        'construction.project.budget.line',
        string='Budget Line',
        domain="[('project_id', '=', analytic_distribution_search)]",
        help='Specific budget line this expense should be charged to'
    )

    # Enhanced project tracking
    construction_project_id = fields.Many2one(
        'project.project',
        string='Construction Project',
        compute='_compute_construction_project',
        store=True,
        help='Related construction project'
    )

    @api.depends('analytic_distribution')
    def _compute_construction_project(self):
        """Compute construction project from analytic distribution"""
        for expense in self:
            project = False
            if expense.analytic_distribution:
                # Find project from analytic account in distribution
                analytic_accounts = self.env['account.analytic.account'].browse(
                    list(expense.analytic_distribution.keys())
                )
                projects = self.env['project.project'].search([
                    ('analytic_account_id', 'in', analytic_accounts.ids)
                ], limit=1)
                if projects:
                    project = projects[0]
            expense.construction_project_id = project

    @api.onchange('construction_project_id')
    def _onchange_construction_project_id(self):
        """Update analytic distribution when project changes"""
        if self.construction_project_id and self.construction_project_id.analytic_account_id:
            self.analytic_distribution = {
                self.construction_project_id.analytic_account_id.id: 100.0
            }

    @api.onchange('budget_category_id', 'construction_project_id')
    def _onchange_budget_category(self):
        """Filter budget lines based on category and project"""
        if self.construction_project_id and self.budget_category_id:
            domain = [
                ('project_id', '=', self.construction_project_id.id),
                ('category_id', '=', self.budget_category_id.id)
            ]
            return {'domain': {'project_budget_line_id': domain}}
        else:
            return {'domain': {'project_budget_line_id': []}}

    def _update_budget_on_approval(self):
        """Update budget line when expense is approved"""
        for expense in self:
            if expense.project_budget_line_id and expense.state == 'done':
                # Update spent amount on budget line
                expense.project_budget_line_id.update_spent_amount(expense.total_amount)

    def action_submit_expenses(self):
        """Override to update budget when submitting"""
        result = super().action_submit_expenses()
        return result

    def approve_expense_sheets(self):
        """Override to update budget when approving"""
        result = super().approve_expense_sheets()
        # Update budget after approval
        for expense in self:
            expense._update_budget_on_approval()
        return result


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    # Budget summary for the expense sheet
    construction_project_id = fields.Many2one(
        'project.project',
        string='Construction Project',
        compute='_compute_construction_project',
        store=True
    )
    total_budget_impact = fields.Float(
        string='Total Budget Impact',
        compute='_compute_budget_impact',
        help='Total impact on project budget'
    )

    @api.depends('expense_line_ids.construction_project_id')
    def _compute_construction_project(self):
        """Get main construction project from expense lines"""
        for sheet in self:
            projects = sheet.expense_line_ids.mapped('construction_project_id')
            sheet.construction_project_id = projects[0] if len(projects) == 1 else False

    @api.depends('expense_line_ids.total_amount')
    def _compute_budget_impact(self):
        """Calculate total budget impact"""
        for sheet in self:
            sheet.total_budget_impact = sum(sheet.expense_line_ids.mapped('total_amount'))

    def action_sheet_move_create(self):
        """Override to update budgets when creating accounting entries"""
        result = super().action_sheet_move_create()
        # Update budgets for all approved expenses
        for expense in self.expense_line_ids:
            expense._update_budget_on_approval()
        return result
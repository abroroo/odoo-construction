# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProjectBudget(models.Model):
    _name = 'construction.project.budget'
    _description = 'Construction Project Budget'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'project_id, create_date desc'

    name = fields.Char(
        string='Budget Name',
        required=True,
        default='Project Budget'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        ondelete='cascade'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ], string='Status', default='draft', required=True)

    # Budget totals
    total_budget = fields.Float(
        string='Total Budget',
        compute='_compute_budget_totals',
        store=True,
        help='Total budgeted amount for this project'
    )
    total_spent = fields.Float(
        string='Total Spent',
        compute='_compute_budget_totals',
        store=True,
        help='Total amount spent on this project'
    )
    total_committed = fields.Float(
        string='Total Committed',
        compute='_compute_budget_totals',
        store=True,
        help='Total committed amount (purchase orders, etc.)'
    )
    remaining_budget = fields.Float(
        string='Remaining Budget',
        compute='_compute_budget_totals',
        store=True,
        help='Remaining budget available'
    )
    budget_utilization = fields.Float(
        string='Budget Utilization (%)',
        compute='_compute_budget_totals',
        store=True,
        help='Percentage of budget utilized'
    )

    # Budget lines
    budget_line_ids = fields.One2many(
        'construction.project.budget.line',
        'budget_id',
        string='Budget Lines'
    )

    # Dates
    start_date = fields.Date(
        string='Budget Start Date',
        default=fields.Date.context_today
    )
    end_date = fields.Date(
        string='Budget End Date'
    )

    # Alert settings
    alert_threshold = fields.Float(
        string='Alert Threshold (%)',
        default=90.0,
        help='Alert when budget utilization reaches this percentage'
    )
    is_over_budget = fields.Boolean(
        string='Over Budget',
        compute='_compute_alerts',
        store=True
    )
    is_near_budget_limit = fields.Boolean(
        string='Near Budget Limit',
        compute='_compute_alerts',
        store=True
    )

    # Notes
    notes = fields.Text(
        string='Budget Notes'
    )

    @api.depends('budget_line_ids.budget_amount', 'budget_line_ids.spent_amount', 'budget_line_ids.committed_amount')
    def _compute_budget_totals(self):
        for budget in self:
            budget.total_budget = sum(budget.budget_line_ids.mapped('budget_amount'))
            budget.total_spent = sum(budget.budget_line_ids.mapped('spent_amount'))
            budget.total_committed = sum(budget.budget_line_ids.mapped('committed_amount'))
            budget.remaining_budget = budget.total_budget - budget.total_spent - budget.total_committed

            if budget.total_budget > 0:
                budget.budget_utilization = (budget.total_spent / budget.total_budget) * 100
            else:
                budget.budget_utilization = 0.0

    @api.depends('budget_utilization', 'alert_threshold', 'remaining_budget')
    def _compute_alerts(self):
        for budget in self:
            budget.is_over_budget = budget.remaining_budget < 0
            budget.is_near_budget_limit = budget.budget_utilization >= budget.alert_threshold

    def action_approve(self):
        self.state = 'approved'

    def action_activate(self):
        self.state = 'active'

    def action_close(self):
        self.state = 'closed'

    def action_reset_to_draft(self):
        self.state = 'draft'

    def action_view_budget_analysis(self):
        """View budget analysis for this specific budget"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Budget Analysis',
            'res_model': 'construction.project.budget.line',
            'view_mode': 'graph,pivot',
            'domain': [('budget_id', '=', self.id)],
            'context': {
                'group_by': ['category_id']
            }
        }


class ProjectBudgetLine(models.Model):
    _name = 'construction.project.budget.line'
    _description = 'Construction Project Budget Line'
    _order = 'budget_id, category_id, sequence, name'

    name = fields.Char(
        string='Description',
        required=True,
        help='Budget line description'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    budget_id = fields.Many2one(
        'construction.project.budget',
        string='Budget',
        required=True,
        ondelete='cascade'
    )
    category_id = fields.Many2one(
        'construction.budget.category',
        string='Budget Category',
        required=True
    )

    # Quantities and rates
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        help='Planned quantity'
    )
    unit_price = fields.Float(
        string='Unit Price',
        help='Price per unit'
    )
    budget_amount = fields.Float(
        string='Budget Amount',
        compute='_compute_budget_amount',
        store=True,
        help='Total budgeted amount (quantity * unit_price)'
    )

    # Actual amounts
    spent_amount = fields.Float(
        string='Spent Amount',
        help='Amount actually spent'
    )
    committed_amount = fields.Float(
        string='Committed Amount',
        help='Amount committed through purchase orders'
    )
    remaining_amount = fields.Float(
        string='Remaining Amount',
        compute='_compute_remaining_amount',
        store=True,
        help='Remaining budget amount'
    )

    # Progress tracking
    progress_percentage = fields.Float(
        string='Progress (%)',
        compute='_compute_progress',
        store=True,
        help='Progress percentage based on spending'
    )

    # Related fields
    project_id = fields.Many2one(
        related='budget_id.project_id',
        string='Project',
        store=True
    )

    # UOM
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        help='Unit of measure for quantity'
    )

    # Notes
    notes = fields.Text(
        string='Notes'
    )

    @api.depends('quantity', 'unit_price')
    def _compute_budget_amount(self):
        for line in self:
            line.budget_amount = line.quantity * line.unit_price

    @api.depends('budget_amount', 'spent_amount', 'committed_amount')
    def _compute_remaining_amount(self):
        for line in self:
            line.remaining_amount = line.budget_amount - line.spent_amount - line.committed_amount

    @api.depends('budget_amount', 'spent_amount')
    def _compute_progress(self):
        for line in self:
            if line.budget_amount > 0:
                line.progress_percentage = (line.spent_amount / line.budget_amount) * 100
            else:
                line.progress_percentage = 0.0

    @api.constrains('quantity', 'unit_price')
    def _check_positive_values(self):
        for line in self:
            if line.quantity < 0:
                raise ValidationError("Quantity cannot be negative.")
            if line.unit_price < 0:
                raise ValidationError("Unit price cannot be negative.")

    def update_spent_amount(self, additional_amount):
        """Update spent amount with additional spending"""
        self.spent_amount += additional_amount

    def update_committed_amount(self, additional_amount):
        """Update committed amount with additional commitments"""
        self.committed_amount += additional_amount
# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Budget management
    budget_ids = fields.One2many(
        'construction.project.budget',
        'project_id',
        string='Project Budgets'
    )
    active_budget_id = fields.Many2one(
        'construction.project.budget',
        string='Active Budget',
        domain="[('project_id', '=', id), ('state', '=', 'active')]",
        help='Currently active budget for this project'
    )

    # Quick budget summary fields
    total_budget = fields.Float(
        string='Total Budget',
        compute='_compute_budget_summary',
        store=True,
        help='Total project budget amount'
    )
    total_spent = fields.Float(
        string='Total Spent',
        compute='_compute_budget_summary',
        store=True,
        help='Total amount spent on project'
    )
    total_committed = fields.Float(
        string='Total Committed',
        compute='_compute_budget_summary',
        store=True,
        help='Total committed amount (POs, etc.)'
    )
    remaining_budget = fields.Float(
        string='Remaining Budget',
        compute='_compute_budget_summary',
        store=True,
        help='Remaining budget available'
    )
    budget_utilization = fields.Float(
        string='Budget Utilization (%)',
        compute='_compute_budget_summary',
        store=True,
        help='Percentage of budget used'
    )

    # Budget status indicators
    is_over_budget = fields.Boolean(
        string='Over Budget',
        compute='_compute_budget_status',
        store=True
    )
    is_near_budget_limit = fields.Boolean(
        string='Near Budget Limit',
        compute='_compute_budget_status',
        store=True
    )
    budget_status = fields.Selection([
        ('good', 'On Track'),
        ('warning', 'Near Limit'),
        ('danger', 'Over Budget'),
        ('no_budget', 'No Budget')
    ], string='Budget Status', compute='_compute_budget_status', store=True)

    # Budget tracking preferences
    budget_alert_threshold = fields.Float(
        string='Budget Alert Threshold (%)',
        default=90.0,
        help='Alert when budget utilization reaches this percentage'
    )

    @api.depends('active_budget_id.total_budget', 'active_budget_id.total_spent',
                 'active_budget_id.total_committed', 'active_budget_id.remaining_budget',
                 'active_budget_id.budget_utilization')
    def _compute_budget_summary(self):
        for project in self:
            if project.active_budget_id:
                project.total_budget = project.active_budget_id.total_budget
                project.total_spent = project.active_budget_id.total_spent
                project.total_committed = project.active_budget_id.total_committed
                project.remaining_budget = project.active_budget_id.remaining_budget
                project.budget_utilization = project.active_budget_id.budget_utilization
            else:
                project.total_budget = 0.0
                project.total_spent = 0.0
                project.total_committed = 0.0
                project.remaining_budget = 0.0
                project.budget_utilization = 0.0

    @api.depends('remaining_budget', 'budget_utilization', 'budget_alert_threshold', 'total_budget')
    def _compute_budget_status(self):
        for project in self:
            if project.total_budget <= 0:
                project.budget_status = 'no_budget'
                project.is_over_budget = False
                project.is_near_budget_limit = False
            elif project.remaining_budget < 0:
                project.budget_status = 'danger'
                project.is_over_budget = True
                project.is_near_budget_limit = False
            elif project.budget_utilization >= project.budget_alert_threshold:
                project.budget_status = 'warning'
                project.is_over_budget = False
                project.is_near_budget_limit = True
            else:
                project.budget_status = 'good'
                project.is_over_budget = False
                project.is_near_budget_limit = False

    def action_create_budget(self):
        """Create a new budget for this project"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Budget',
            'res_model': 'construction.project.budget',
            'view_mode': 'form',
            'context': {
                'default_project_id': self.id,
                'default_name': f'{self.name} Budget'
            },
            'target': 'new'
        }

    def action_view_budgets(self):
        """View all budgets for this project"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Project Budgets',
            'res_model': 'construction.project.budget',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id
            }
        }

    def action_view_budget_analysis(self):
        """View budget analysis dashboard"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Budget Analysis',
            'res_model': 'construction.budget.analysis',
            'view_mode': 'graph,pivot',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'group_by': ['category_id']
            }
        }

    @api.model
    def get_budget_dashboard_data(self):
        """Get data for budget dashboard"""
        projects = self.search([])
        data = {
            'total_projects': len(projects),
            'total_budget': sum(projects.mapped('total_budget')),
            'total_spent': sum(projects.mapped('total_spent')),
            'projects_over_budget': len(projects.filtered('is_over_budget')),
            'projects_near_limit': len(projects.filtered('is_near_budget_limit')),
        }

        # Category breakdown
        budget_lines = self.env['construction.project.budget.line'].search([
            ('project_id', 'in', projects.ids)
        ])

        categories = {}
        for line in budget_lines:
            cat_name = line.category_id.name
            if cat_name not in categories:
                categories[cat_name] = {
                    'budget': 0.0,
                    'spent': 0.0
                }
            categories[cat_name]['budget'] += line.budget_amount
            categories[cat_name]['spent'] += line.spent_amount

        data['categories'] = categories
        return data
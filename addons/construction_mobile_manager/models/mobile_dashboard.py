# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class MobileDashboard(models.Model):
    _name = 'construction.mobile.dashboard'
    _description = 'Mobile Dashboard for Site Managers'

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    name = fields.Char(string='Dashboard Name', compute='_compute_name')

    @api.depends('user_id')
    def _compute_name(self):
        for record in self:
            record.name = f"Dashboard - {record.user_id.name}"

    def get_dashboard_data(self):
        """Get dashboard data for the current user"""
        user = self.env.user

        # Get user's assigned tasks
        assigned_tasks = self.env['project.task'].search([
            ('user_ids', 'in', [user.id])
        ])

        # Calculate task statistics
        total_tasks = len(assigned_tasks)
        todo_tasks = assigned_tasks.filtered(lambda t: t.stage_id.name.lower() in ['to do', 'new', 'draft'])
        in_progress_tasks = assigned_tasks.filtered(lambda t: 'progress' in t.stage_id.name.lower() or 'doing' in t.stage_id.name.lower())
        done_tasks = assigned_tasks.filtered(lambda t: t.stage_id.name.lower() in ['done', 'complete', 'closed'])

        # Get recent expenses
        recent_expenses = self.env['hr.expense'].search([
            ('employee_id.user_id', '=', user.id),
            ('construction_project_id', '!=', False)
        ], limit=5, order='create_date desc')

        # Calculate expense totals
        this_week_expenses = self.env['hr.expense'].search([
            ('employee_id.user_id', '=', user.id),
            ('create_date', '>=', fields.Datetime.now().replace(hour=0, minute=0, second=0) - fields.timedelta(days=7))
        ])

        return {
            'user_name': user.name,
            'total_tasks': total_tasks,
            'todo_tasks': len(todo_tasks),
            'in_progress_tasks': len(in_progress_tasks),
            'done_tasks': len(done_tasks),
            'recent_tasks': [{
                'id': task.id,
                'name': task.name,
                'stage': task.stage_id.name,
                'project': task.project_id.name,
                'priority': task.priority,
            } for task in assigned_tasks[:5]],
            'recent_expenses': [{
                'id': expense.id,
                'name': expense.name,
                'amount': expense.total_amount,
                'date': expense.date,
                'project': expense.construction_project_id.name if expense.construction_project_id else '',
            } for expense in recent_expenses],
            'week_expense_total': sum(this_week_expenses.mapped('total_amount')),
            'week_expense_count': len(this_week_expenses),
        }


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def mobile_update_stage(self, stage_name):
        """Update task stage from mobile interface"""
        # Find stage by name within the project
        stage = self.project_id.type_ids.filtered(lambda s: s.name.lower() == stage_name.lower())
        if not stage:
            # Create stage if it doesn't exist
            stage = self.env['project.task.type'].create({
                'name': stage_name,
                'project_ids': [(6, 0, [self.project_id.id])],
            })

        self.stage_id = stage[0] if stage else False
        return True

    def get_mobile_task_data(self):
        """Get task data optimized for mobile display"""
        # Get budget information if available
        budget_info = {}
        if hasattr(self, 'budget_line_id') and self.budget_line_id:
            budget_info = {
                'budget_amount': self.budget_line_id.budget_amount,
                'spent_amount': self.budget_line_id.spent_amount,
                'remaining_amount': self.budget_line_id.remaining_amount,
                'progress_percentage': self.budget_line_id.progress_percentage,
            }

        # Get recent expenses for this task
        recent_expenses = []
        if hasattr(self, 'budget_line_id') and self.budget_line_id:
            expenses = self.env['hr.expense'].search([
                ('project_budget_line_id', '=', self.budget_line_id.id)
            ], limit=5, order='create_date desc')
            recent_expenses = [{
                'id': exp.id,
                'name': exp.name,
                'amount': exp.total_amount,
                'date': exp.date,
                'state': exp.state,
            } for exp in expenses]

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stage': self.stage_id.name if self.stage_id else 'No Stage',
            'project': self.project_id.name,
            'priority': self.priority,
            'deadline': self.date_deadline,
            'assignees': [user.name for user in self.user_ids],
            'budget_info': budget_info,
            'recent_expenses': recent_expenses,
        }
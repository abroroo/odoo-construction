# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class PMBudgetMonitor(models.Model):
    _name = 'construction.pm.budget.monitor'
    _description = 'Project Manager Budget Monitor'

    name = fields.Char(string='Monitor Name', default='Budget Monitor')
    project_id = fields.Many2one('project.project', string='Project', required=True)
    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user)

    @api.model
    def get_budget_analytics(self, project_id, period='week'):
        """Get comprehensive budget analytics"""
        if not project_id:
            return {}

        project = self.env['project.project'].browse(project_id)
        if not project.exists():
            return {}

        return {
            'overview': self._get_budget_overview(project),
            'category_breakdown': self._get_category_breakdown(project),
            'spending_trends': self._get_spending_trends(project, period),
            'recent_expenses': self._get_recent_expenses(project),
            'budget_alerts': self._get_budget_alerts(project),
            'approval_queue': self._get_approval_queue(project),
            'export_data': self._get_export_data(project),
        }

    def _get_budget_overview(self, project):
        """Get overall budget overview"""
        budget_lines = self.env['project.budget.line'].search([
            ('project_id', '=', project.id)
        ])

        total_allocated = sum(budget_lines.mapped('budget_amount'))
        total_spent = sum(budget_lines.mapped('spent_amount'))
        total_remaining = total_allocated - total_spent
        percentage_used = (total_spent / total_allocated * 100) if total_allocated > 0 else 0

        # Calculate variance
        variance = total_remaining
        variance_percentage = (variance / total_allocated * 100) if total_allocated > 0 else 0

        # Get monthly spending
        current_month_spending = self._get_current_month_spending(project)
        last_month_spending = self._get_last_month_spending(project)
        spending_trend = self._calculate_spending_trend(current_month_spending, last_month_spending)

        return {
            'total_allocated': total_allocated,
            'total_spent': total_spent,
            'total_remaining': total_remaining,
            'percentage_used': percentage_used,
            'is_over_budget': total_spent > total_allocated,
            'variance': variance,
            'variance_percentage': variance_percentage,
            'current_month_spending': current_month_spending,
            'last_month_spending': last_month_spending,
            'spending_trend': spending_trend,
            'budget_lines_count': len(budget_lines),
        }

    def _get_category_breakdown(self, project):
        """Get budget breakdown by category"""
        budget_lines = self.env['project.budget.line'].search([
            ('project_id', '=', project.id)
        ])

        categories = {}
        for line in budget_lines:
            cat_name = line.category_id.name if line.category_id else 'Uncategorized'
            cat_id = line.category_id.id if line.category_id else 0

            if cat_name not in categories:
                categories[cat_name] = {
                    'id': cat_id,
                    'name': cat_name,
                    'allocated': 0,
                    'spent': 0,
                    'remaining': 0,
                    'percentage': 0,
                    'line_count': 0,
                    'over_budget': False,
                    'recent_expenses': []
                }

            cat_data = categories[cat_name]
            cat_data['allocated'] += line.budget_amount
            cat_data['spent'] += line.spent_amount
            cat_data['remaining'] = cat_data['allocated'] - cat_data['spent']
            cat_data['percentage'] = (cat_data['spent'] / cat_data['allocated'] * 100) if cat_data['allocated'] > 0 else 0
            cat_data['line_count'] += 1
            cat_data['over_budget'] = cat_data['spent'] > cat_data['allocated']

            # Get recent expenses for this category
            if line.category_id:
                recent_expenses = self.env['hr.expense'].search([
                    ('budget_category_id', '=', line.category_id.id),
                    ('construction_project_id', '=', project.id),
                    ('create_date', '>=', fields.Datetime.now() - timedelta(days=30))
                ], limit=5, order='create_date desc')

                cat_data['recent_expenses'] = [{
                    'id': exp.id,
                    'name': exp.name,
                    'amount': exp.total_amount,
                    'date': exp.date.strftime('%Y-%m-%d') if exp.date else '',
                    'employee': exp.employee_id.name,
                    'state': exp.state,
                } for exp in recent_expenses]

        # Convert to list and sort by spending percentage
        category_list = list(categories.values())
        category_list.sort(key=lambda x: x['percentage'], reverse=True)

        return category_list

    def _get_spending_trends(self, project, period='week'):
        """Get spending trends over time"""
        if period == 'week':
            date_from = fields.Datetime.now() - timedelta(weeks=12)  # 12 weeks
            date_grouping = 'week'
        elif period == 'month':
            date_from = fields.Datetime.now() - timedelta(days=365)  # 12 months
            date_grouping = 'month'
        else:
            date_from = fields.Datetime.now() - timedelta(days=30)  # 30 days
            date_grouping = 'day'

        # Get expenses grouped by time period
        expenses = self.env['hr.expense'].search([
            ('construction_project_id', '=', project.id),
            ('date', '>=', date_from.date()),
            ('state', 'in', ['done', 'approved'])
        ])

        # Group expenses by period
        trends = {}
        for expense in expenses:
            if not expense.date:
                continue

            if date_grouping == 'week':
                # Get week start (Monday)
                week_start = expense.date - timedelta(days=expense.date.weekday())
                period_key = week_start.strftime('%Y-W%U')
                period_label = week_start.strftime('%b %d')
            elif date_grouping == 'month':
                period_key = expense.date.strftime('%Y-%m')
                period_label = expense.date.strftime('%b %Y')
            else:
                period_key = expense.date.strftime('%Y-%m-%d')
                period_label = expense.date.strftime('%b %d')

            if period_key not in trends:
                trends[period_key] = {
                    'period': period_key,
                    'label': period_label,
                    'amount': 0,
                    'count': 0,
                    'date': expense.date
                }

            trends[period_key]['amount'] += expense.total_amount
            trends[period_key]['count'] += 1

        # Convert to sorted list
        trend_list = list(trends.values())
        trend_list.sort(key=lambda x: x['date'])

        return trend_list

    def _get_recent_expenses(self, project):
        """Get recent expenses with detailed information"""
        expenses = self.env['hr.expense'].search([
            ('construction_project_id', '=', project.id)
        ], order='create_date desc', limit=20)

        expense_data = []
        for expense in expenses:
            # Get budget line if linked
            budget_line = None
            if hasattr(expense, 'project_budget_line_id') and expense.project_budget_line_id:
                budget_line = expense.project_budget_line_id

            expense_data.append({
                'id': expense.id,
                'name': expense.name,
                'amount': expense.total_amount,
                'date': expense.date.strftime('%Y-%m-%d') if expense.date else '',
                'state': expense.state,
                'state_label': dict(expense._fields['state'].selection).get(expense.state, expense.state),
                'employee': expense.employee_id.name,
                'category': expense.budget_category_id.name if hasattr(expense, 'budget_category_id') and expense.budget_category_id else 'General',
                'budget_line': budget_line.name if budget_line else None,
                'task': budget_line.task_id.name if budget_line and hasattr(budget_line, 'task_id') and budget_line.task_id else None,
                'receipt_count': len(expense.attachment_ids) if hasattr(expense, 'attachment_ids') else 0,
                'can_approve': expense.state == 'reported' and self.env.user.has_group('hr_expense.group_hr_expense_manager'),
                'days_old': (fields.Date.today() - expense.date).days if expense.date else 0,
            })

        return expense_data

    def _get_budget_alerts(self, project):
        """Get budget alerts and warnings"""
        alerts = []

        # Check category overruns
        category_breakdown = self._get_category_breakdown(project)
        for category in category_breakdown:
            if category['over_budget']:
                alerts.append({
                    'type': 'danger',
                    'icon': 'fa-exclamation-circle',
                    'title': f'{category["name"]} Over Budget',
                    'message': f'Spent ${category["spent"]:.2f} of ${category["allocated"]:.2f} ({category["percentage"]:.1f}%)',
                    'action': 'review_category',
                    'category_id': category['id'],
                })
            elif category['percentage'] > 90:
                alerts.append({
                    'type': 'warning',
                    'icon': 'fa-exclamation-triangle',
                    'title': f'{category["name"]} Nearly Exhausted',
                    'message': f'Used {category["percentage"]:.1f}% of budget',
                    'action': 'review_category',
                    'category_id': category['id'],
                })

        # Check for high pending expenses
        pending_expenses = self.env['hr.expense'].search([
            ('construction_project_id', '=', project.id),
            ('state', '=', 'reported')
        ])
        pending_amount = sum(pending_expenses.mapped('total_amount'))

        if pending_amount > 5000:  # Configurable threshold
            alerts.append({
                'type': 'info',
                'icon': 'fa-clock',
                'title': 'High Pending Expenses',
                'message': f'${pending_amount:.2f} in expenses awaiting approval',
                'action': 'review_expenses',
                'count': len(pending_expenses),
            })

        # Check for old expenses
        old_expenses = self.env['hr.expense'].search([
            ('construction_project_id', '=', project.id),
            ('state', '=', 'reported'),
            ('create_date', '<', fields.Datetime.now() - timedelta(days=7))
        ])

        if old_expenses:
            alerts.append({
                'type': 'warning',
                'icon': 'fa-history',
                'title': 'Old Pending Expenses',
                'message': f'{len(old_expenses)} expenses pending for over a week',
                'action': 'review_old_expenses',
                'count': len(old_expenses),
            })

        return alerts

    def _get_approval_queue(self, project):
        """Get expenses waiting for approval"""
        pending_expenses = self.env['hr.expense'].search([
            ('construction_project_id', '=', project.id),
            ('state', '=', 'reported')
        ], order='create_date asc')

        queue_data = []
        for expense in pending_expenses:
            queue_data.append({
                'id': expense.id,
                'name': expense.name,
                'amount': expense.total_amount,
                'employee': expense.employee_id.name,
                'date': expense.date.strftime('%Y-%m-%d') if expense.date else '',
                'category': expense.budget_category_id.name if hasattr(expense, 'budget_category_id') and expense.budget_category_id else 'General',
                'days_pending': (fields.Date.today() - expense.create_date.date()).days,
                'receipt_count': len(expense.attachment_ids) if hasattr(expense, 'attachment_ids') else 0,
                'priority': 'high' if (fields.Date.today() - expense.create_date.date()).days > 7 else 'normal',
            })

        return {
            'total_count': len(queue_data),
            'total_amount': sum(e['amount'] for e in queue_data),
            'high_priority_count': len([e for e in queue_data if e['priority'] == 'high']),
            'expenses': queue_data,
        }

    def _get_export_data(self, project):
        """Get data for export/reporting"""
        budget_lines = self.env['project.budget.line'].search([
            ('project_id', '=', project.id)
        ])

        export_data = []
        for line in budget_lines:
            export_data.append({
                'category': line.category_id.name if line.category_id else 'Uncategorized',
                'item': line.name,
                'budget_amount': line.budget_amount,
                'spent_amount': line.spent_amount,
                'remaining_amount': line.remaining_amount,
                'percentage_used': (line.spent_amount / line.budget_amount * 100) if line.budget_amount > 0 else 0,
                'task': line.task_id.name if hasattr(line, 'task_id') and line.task_id else '',
            })

        return export_data

    # Helper methods
    def _get_current_month_spending(self, project):
        """Get current month spending"""
        start_of_month = fields.Date.today().replace(day=1)
        expenses = self.env['hr.expense'].search([
            ('construction_project_id', '=', project.id),
            ('date', '>=', start_of_month),
            ('state', 'in', ['done', 'approved'])
        ])
        return sum(expenses.mapped('total_amount'))

    def _get_last_month_spending(self, project):
        """Get last month spending"""
        today = fields.Date.today()
        start_of_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        end_of_last_month = today.replace(day=1) - timedelta(days=1)

        expenses = self.env['hr.expense'].search([
            ('construction_project_id', '=', project.id),
            ('date', '>=', start_of_last_month),
            ('date', '<=', end_of_last_month),
            ('state', 'in', ['done', 'approved'])
        ])
        return sum(expenses.mapped('total_amount'))

    def _calculate_spending_trend(self, current, last):
        """Calculate spending trend"""
        if last == 0:
            return {'direction': 'up', 'percentage': 100} if current > 0 else {'direction': 'stable', 'percentage': 0}

        percentage_change = ((current - last) / last) * 100

        if abs(percentage_change) < 5:
            return {'direction': 'stable', 'percentage': abs(percentage_change)}
        elif percentage_change > 0:
            return {'direction': 'up', 'percentage': percentage_change}
        else:
            return {'direction': 'down', 'percentage': abs(percentage_change)}

    @api.model
    def approve_expense(self, expense_id):
        """Approve an expense"""
        try:
            expense = self.env['hr.expense'].browse(expense_id)
            if not expense.exists():
                return {'success': False, 'message': 'Expense not found'}

            if expense.state != 'reported':
                return {'success': False, 'message': 'Expense is not in the correct state for approval'}

            # Use Odoo's built-in approval method
            expense.approve_expense_sheets()

            return {
                'success': True,
                'message': f'Expense "{expense.name}" approved successfully'
            }

        except Exception as e:
            _logger.error(f"Error approving expense {expense_id}: {str(e)}")
            return {'success': False, 'message': 'Failed to approve expense'}

    @api.model
    def batch_approve_expenses(self, expense_ids):
        """Batch approve multiple expenses"""
        try:
            expenses = self.env['hr.expense'].browse(expense_ids)
            reportable_expenses = expenses.filtered(lambda e: e.state == 'reported')

            if not reportable_expenses:
                return {'success': False, 'message': 'No expenses available for approval'}

            reportable_expenses.approve_expense_sheets()

            return {
                'success': True,
                'message': f'Successfully approved {len(reportable_expenses)} expenses',
                'approved_count': len(reportable_expenses)
            }

        except Exception as e:
            _logger.error(f"Error batch approving expenses: {str(e)}")
            return {'success': False, 'message': 'Failed to approve expenses'}
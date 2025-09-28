# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class MobileTaskManager(models.Model):
    _name = 'construction.mobile.task.manager'
    _description = 'Mobile Task Management Interface'

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    @api.model
    def get_my_tasks(self, stage_filter=None):
        """Get current user's assigned tasks with mobile-optimized data"""
        user = self.env.user

        domain = [('user_ids', 'in', [user.id])]

        # Add stage filter if provided
        if stage_filter:
            if stage_filter == 'todo':
                domain.append(('stage_id.name', 'ilike', 'to do'))
            elif stage_filter == 'progress':
                domain.extend(['|', ('stage_id.name', 'ilike', 'progress'), ('stage_id.name', 'ilike', 'doing')])
            elif stage_filter == 'done':
                domain.extend(['|', '|', ('stage_id.name', 'ilike', 'done'), ('stage_id.name', 'ilike', 'complete'), ('stage_id.name', 'ilike', 'closed')])

        tasks = self.env['project.task'].search(domain, order='priority desc, date_deadline asc, name')

        task_data = []
        for task in tasks:
            # Get budget info if available
            budget_allocated = 0
            budget_spent = 0
            budget_remaining = 0

            if hasattr(task, 'budget_line_id') and task.budget_line_id:
                budget_allocated = task.budget_line_id.budget_amount
                budget_spent = task.budget_line_id.spent_amount
                budget_remaining = task.budget_line_id.remaining_amount

            # Determine status color
            status_color = self._get_status_color(task.stage_id.name if task.stage_id else '')

            task_data.append({
                'id': task.id,
                'name': task.name,
                'description': task.description or '',
                'project_name': task.project_id.name,
                'stage': task.stage_id.name if task.stage_id else 'No Stage',
                'stage_color': status_color,
                'priority': task.priority,
                'deadline': task.date_deadline.strftime('%Y-%m-%d') if task.date_deadline else None,
                'budget_allocated': budget_allocated,
                'budget_spent': budget_spent,
                'budget_remaining': budget_remaining,
                'budget_percentage': (budget_spent / budget_allocated * 100) if budget_allocated > 0 else 0,
                'has_budget': budget_allocated > 0,
                'assignees': [user.name for user in task.user_ids],
                'parent_task': task.parent_id.name if task.parent_id else None,
            })

        return task_data

    def _get_status_color(self, stage_name):
        """Get color code for task status"""
        stage_lower = stage_name.lower()
        if any(word in stage_lower for word in ['done', 'complete', 'closed', 'finished']):
            return 'success'  # Green
        elif any(word in stage_lower for word in ['progress', 'doing', 'working', 'started']):
            return 'warning'  # Orange
        elif any(word in stage_lower for word in ['blocked', 'waiting', 'hold']):
            return 'danger'   # Red
        else:
            return 'secondary'  # Gray (To Do, New, etc.)

    @api.model
    def update_task_status(self, task_id, new_status):
        """Update task status from mobile interface"""
        task = self.env['project.task'].browse(task_id)
        if not task.exists():
            return {'success': False, 'message': 'Task not found'}

        # Check if user is assigned to task
        if self.env.user not in task.user_ids:
            return {'success': False, 'message': 'You are not assigned to this task'}

        try:
            # Find or create stage
            stage = task.project_id.type_ids.filtered(lambda s: s.name.lower() == new_status.lower())

            if not stage:
                # Create common stages if they don't exist
                stage_name = new_status.title()
                if new_status.lower() == 'todo':
                    stage_name = 'To Do'
                elif new_status.lower() == 'progress':
                    stage_name = 'In Progress'
                elif new_status.lower() == 'done':
                    stage_name = 'Done'

                stage = self.env['project.task.type'].create({
                    'name': stage_name,
                    'project_ids': [(6, 0, [task.project_id.id])],
                })

            # Update task stage
            task.stage_id = stage[0] if isinstance(stage, list) else stage

            return {
                'success': True,
                'message': f'Task status updated to {stage.name}',
                'new_stage': stage.name,
                'color': self._get_status_color(stage.name)
            }

        except Exception as e:
            _logger.error(f"Error updating task status: {str(e)}")
            return {'success': False, 'message': 'Failed to update task status'}

    @api.model
    def get_task_details(self, task_id):
        """Get detailed task information for mobile view"""
        task = self.env['project.task'].browse(task_id)
        if not task.exists():
            return None

        # Get budget information
        budget_info = {
            'allocated': 0,
            'spent': 0,
            'remaining': 0,
            'percentage_used': 0,
            'has_budget': False,
        }

        if hasattr(task, 'budget_line_id') and task.budget_line_id:
            budget_info.update({
                'allocated': task.budget_line_id.budget_amount,
                'spent': task.budget_line_id.spent_amount,
                'remaining': task.budget_line_id.remaining_amount,
                'percentage_used': (task.budget_line_id.spent_amount / task.budget_line_id.budget_amount * 100) if task.budget_line_id.budget_amount > 0 else 0,
                'has_budget': True,
                'category': task.budget_line_id.category_id.name,
            })

        # Get recent expenses
        recent_expenses = []
        if hasattr(task, 'budget_line_id') and task.budget_line_id:
            expenses = self.env['hr.expense'].search([
                ('project_budget_line_id', '=', task.budget_line_id.id)
            ], limit=10, order='create_date desc')

            recent_expenses = [{
                'id': exp.id,
                'name': exp.name,
                'amount': exp.total_amount,
                'date': exp.date.strftime('%Y-%m-%d') if exp.date else '',
                'state': exp.state,
                'employee': exp.employee_id.name,
            } for exp in expenses]

        # Get available status options
        available_stages = [{
            'name': stage.name,
            'key': stage.name.lower().replace(' ', ''),
            'color': self._get_status_color(stage.name),
        } for stage in task.project_id.type_ids]

        return {
            'id': task.id,
            'name': task.name,
            'description': task.description or 'No description provided',
            'project_name': task.project_id.name,
            'current_stage': task.stage_id.name if task.stage_id else 'No Stage',
            'current_stage_color': self._get_status_color(task.stage_id.name if task.stage_id else ''),
            'priority': task.priority,
            'deadline': task.date_deadline.strftime('%Y-%m-%d') if task.date_deadline else None,
            'assignees': [{'id': user.id, 'name': user.name} for user in task.user_ids],
            'parent_task': task.parent_id.name if task.parent_id else None,
            'budget_info': budget_info,
            'recent_expenses': recent_expenses,
            'available_stages': available_stages,
            'is_assigned': self.env.user in task.user_ids,
        }
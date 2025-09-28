# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class PMTaskBoard(models.Model):
    _name = 'construction.pm.task.board'
    _description = 'Project Manager Task Board'

    name = fields.Char(string='Board Name', default='Task Board')
    project_id = fields.Many2one('project.project', string='Project', required=True)
    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user)

    @api.model
    def get_board_data(self, project_id, filters=None):
        """Get Kanban board data with optional filters"""
        if not project_id:
            return {'stages': [], 'tasks': []}

        project = self.env['project.project'].browse(project_id)
        if not project.exists():
            return {'stages': [], 'tasks': []}

        # Apply filters
        domain = [('project_id', '=', project_id)]
        if filters:
            if filters.get('user_id'):
                domain.append(('user_ids', 'in', [filters['user_id']]))
            if filters.get('priority'):
                domain.append(('priority', '=', filters['priority']))
            if filters.get('date_from'):
                domain.append(('date_deadline', '>=', filters['date_from']))
            if filters.get('date_to'):
                domain.append(('date_deadline', '<=', filters['date_to']))

        tasks = self.env['project.task'].search(domain)
        stages = project.type_ids or self.env['project.task.type'].search([])

        return {
            'stages': self._get_stages_data(stages, tasks),
            'tasks': self._get_tasks_data(tasks),
            'filters': self._get_filter_options(project),
        }

    def _get_stages_data(self, stages, tasks):
        """Get stage data with task counts"""
        stages_data = []
        for stage in stages:
            stage_tasks = tasks.filtered(lambda t: t.stage_id.id == stage.id)
            stages_data.append({
                'id': stage.id,
                'name': stage.name,
                'sequence': stage.sequence,
                'task_count': len(stage_tasks),
                'fold': stage.fold if hasattr(stage, 'fold') else False,
            })

        # Add tasks without stage
        unassigned_tasks = tasks.filtered(lambda t: not t.stage_id)
        if unassigned_tasks:
            stages_data.append({
                'id': 0,
                'name': 'Unassigned',
                'sequence': 999,
                'task_count': len(unassigned_tasks),
                'fold': False,
            })

        return sorted(stages_data, key=lambda x: x['sequence'])

    def _get_tasks_data(self, tasks):
        """Get detailed task data for Kanban cards"""
        tasks_data = []
        for task in tasks:
            budget_info = self._get_task_budget_info(task)

            tasks_data.append({
                'id': task.id,
                'name': task.name,
                'description': task.description or '',
                'stage_id': task.stage_id.id if task.stage_id else 0,
                'stage_name': task.stage_id.name if task.stage_id else 'Unassigned',
                'priority': task.priority,
                'priority_label': dict(task._fields['priority'].selection).get(task.priority, 'Normal'),

                # Assignees
                'assignees': [{
                    'id': user.id,
                    'name': user.name,
                    'avatar': f'/web/image/res.users/{user.id}/avatar_128',
                } for user in task.user_ids],

                # Dates
                'deadline': task.date_deadline.strftime('%Y-%m-%d') if task.date_deadline else None,
                'deadline_label': self._format_deadline(task.date_deadline),
                'is_overdue': self._is_task_overdue(task),

                # Budget information
                'budget_allocated': budget_info.get('allocated', 0),
                'budget_spent': budget_info.get('spent', 0),
                'budget_remaining': budget_info.get('remaining', 0),
                'budget_percentage': budget_info.get('percentage', 0),
                'is_over_budget': budget_info.get('over_budget', False),
                'has_budget': budget_info.get('allocated', 0) > 0,

                # Hierarchy
                'parent_task': task.parent_id.name if task.parent_id else None,
                'child_count': len(task.child_ids),

                # Activity
                'activity_count': self._get_task_activity_count(task),
                'last_update': task.write_date.strftime('%Y-%m-%d') if task.write_date else None,

                # Status indicators
                'color': self._get_task_color(task),
                'tags': [tag.name for tag in task.tag_ids] if hasattr(task, 'tag_ids') else [],
            })

        return tasks_data

    def _get_filter_options(self, project):
        """Get available filter options"""
        # Get all users assigned to project tasks
        users = project.task_ids.mapped('user_ids')

        # Get all priorities used in project
        priorities = project.task_ids.mapped('priority')
        priority_options = [
            {'value': p, 'label': dict(self.env['project.task']._fields['priority'].selection).get(p, p)}
            for p in set(priorities) if p
        ]

        return {
            'users': [{'id': u.id, 'name': u.name} for u in users],
            'priorities': priority_options,
        }

    def _get_task_budget_info(self, task):
        """Get budget information for a task"""
        if hasattr(task, 'budget_line_id') and task.budget_line_id:
            line = task.budget_line_id
            allocated = line.budget_amount
            spent = line.spent_amount
            remaining = allocated - spent
            percentage = (spent / allocated * 100) if allocated > 0 else 0

            return {
                'allocated': allocated,
                'spent': spent,
                'remaining': remaining,
                'percentage': percentage,
                'over_budget': spent > allocated
            }
        return {
            'allocated': 0,
            'spent': 0,
            'remaining': 0,
            'percentage': 0,
            'over_budget': False
        }

    def _format_deadline(self, deadline):
        """Format deadline for display"""
        if not deadline:
            return None

        today = fields.Date.today()
        days_diff = (deadline - today).days

        if days_diff < 0:
            return f"{abs(days_diff)} days overdue"
        elif days_diff == 0:
            return "Due today"
        elif days_diff == 1:
            return "Due tomorrow"
        elif days_diff <= 7:
            return f"Due in {days_diff} days"
        else:
            return deadline.strftime('%b %d, %Y')

    def _is_task_overdue(self, task):
        """Check if task is overdue"""
        if not task.date_deadline:
            return False
        return task.date_deadline < fields.Date.today()

    def _get_task_activity_count(self, task):
        """Get recent activity count for task"""
        # Count recent messages/activities (simplified)
        return 0

    def _get_task_color(self, task):
        """Get color for task card based on status"""
        if self._is_task_overdue(task):
            return 'danger'
        elif task.priority == '1':  # High priority
            return 'warning'
        elif task.stage_id and 'done' in task.stage_id.name.lower():
            return 'success'
        elif task.stage_id and 'progress' in task.stage_id.name.lower():
            return 'info'
        return 'light'

    @api.model
    def move_task(self, task_id, new_stage_id):
        """Move task to new stage (for drag & drop)"""
        try:
            task = self.env['project.task'].browse(task_id)
            if not task.exists():
                return {'success': False, 'message': 'Task not found'}

            # Handle special case for "Unassigned" stage (stage_id = 0)
            if new_stage_id == 0:
                task.stage_id = False
            else:
                stage = self.env['project.task.type'].browse(new_stage_id)
                if not stage.exists():
                    return {'success': False, 'message': 'Stage not found'}
                task.stage_id = stage

            return {
                'success': True,
                'message': f'Task moved to {task.stage_id.name if task.stage_id else "Unassigned"}',
                'new_stage': task.stage_id.name if task.stage_id else 'Unassigned'
            }

        except Exception as e:
            _logger.error(f"Error moving task {task_id}: {str(e)}")
            return {'success': False, 'message': 'Failed to move task'}

    @api.model
    def update_task_priority(self, task_id, priority):
        """Update task priority"""
        try:
            task = self.env['project.task'].browse(task_id)
            if not task.exists():
                return {'success': False, 'message': 'Task not found'}

            task.priority = priority
            return {
                'success': True,
                'message': f'Task priority updated to {dict(task._fields["priority"].selection).get(priority, priority)}'
            }

        except Exception as e:
            _logger.error(f"Error updating task priority {task_id}: {str(e)}")
            return {'success': False, 'message': 'Failed to update priority'}

    @api.model
    def assign_task_user(self, task_id, user_id):
        """Assign user to task"""
        try:
            task = self.env['project.task'].browse(task_id)
            user = self.env['res.users'].browse(user_id)

            if not task.exists() or not user.exists():
                return {'success': False, 'message': 'Task or user not found'}

            # Add user to task if not already assigned
            if user not in task.user_ids:
                task.user_ids = [(4, user_id)]
                return {
                    'success': True,
                    'message': f'Assigned {user.name} to task'
                }
            else:
                return {
                    'success': False,
                    'message': f'{user.name} is already assigned to this task'
                }

        except Exception as e:
            _logger.error(f"Error assigning user to task {task_id}: {str(e)}")
            return {'success': False, 'message': 'Failed to assign user'}

    @api.model
    def create_quick_task(self, project_id, name, stage_id=None, user_id=None):
        """Create a quick task from the board"""
        try:
            project = self.env['project.project'].browse(project_id)
            if not project.exists():
                return {'success': False, 'message': 'Project not found'}

            task_vals = {
                'name': name,
                'project_id': project_id,
            }

            if stage_id and stage_id != 0:
                stage = self.env['project.task.type'].browse(stage_id)
                if stage.exists():
                    task_vals['stage_id'] = stage_id

            if user_id:
                user = self.env['res.users'].browse(user_id)
                if user.exists():
                    task_vals['user_ids'] = [(6, 0, [user_id])]

            task = self.env['project.task'].create(task_vals)

            return {
                'success': True,
                'message': f'Task "{name}" created successfully',
                'task_id': task.id
            }

        except Exception as e:
            _logger.error(f"Error creating quick task: {str(e)}")
            return {'success': False, 'message': 'Failed to create task'}
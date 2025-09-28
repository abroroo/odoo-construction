# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class PMDashboard(models.Model):
    _name = 'construction.pm.dashboard'
    _description = 'Project Manager Dashboard'

    name = fields.Char(string='Dashboard Name', compute='_compute_name', store=True)
    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user)
    project_id = fields.Many2one('project.project', string='Selected Project')
    last_refresh = fields.Datetime(string='Last Refresh', default=fields.Datetime.now)

    # Dashboard data fields
    project_name = fields.Char(string='Project Name', readonly=True)
    total_tasks = fields.Integer(string='Total Tasks', readonly=True)
    todo_count = fields.Integer(string='To Do', readonly=True)
    progress_count = fields.Integer(string='In Progress', readonly=True)
    done_count = fields.Integer(string='Completed', readonly=True)
    progress_percentage = fields.Float(string='Progress %', readonly=True)

    budget_allocated = fields.Float(string='Budget Allocated', readonly=True)
    budget_spent = fields.Float(string='Budget Spent', readonly=True)
    budget_remaining = fields.Float(string='Budget Remaining', readonly=True)
    budget_percentage = fields.Float(string='Budget Used %', readonly=True)
    over_budget = fields.Boolean(string='Over Budget', readonly=True)

    team_size = fields.Integer(string='Team Size', readonly=True)
    active_workers = fields.Integer(string='Active Workers', readonly=True)
    pending_approvals = fields.Integer(string='Pending Approvals', readonly=True)

    dashboard_status = fields.Text(string='Dashboard Status', readonly=True, default='Select a project to load dashboard data')

    @api.depends('user_id')
    def _compute_name(self):
        for record in self:
            record.name = f"PM Dashboard - {record.user_id.name}"

    @api.model
    def get_dashboard_data(self, project_id=None):
        """Get comprehensive dashboard data for project manager"""
        user = self.env.user

        # Get projects where user is manager or has tasks
        if project_id:
            projects = self.env['project.project'].browse(project_id)
        else:
            projects = self.env['project.project'].search([
                '|',
                ('user_id', '=', user.id),  # Project manager
                ('task_ids.user_ids', 'in', [user.id])  # Has assigned tasks
            ])

        if not projects:
            return {'error': 'No projects found for current user'}

        # Use first project if none selected
        current_project = projects[0] if not project_id else projects

        return {
            'projects': self._get_project_list(projects),
            'current_project': self._get_project_overview(current_project),
            'task_board': self._get_task_board_data(current_project),
            'budget_monitor': self._get_budget_monitor_data(current_project),
            'team_overview': self._get_team_overview(current_project),
            'recent_activity': self._get_recent_activity(current_project),
        }

    def _get_project_list(self, projects):
        """Get list of available projects for dropdown"""
        return [{
            'id': project.id,
            'name': project.name,
            'progress': self._calculate_project_progress(project),
            'budget_status': self._get_project_budget_status(project),
        } for project in projects]

    def _get_project_overview(self, project):
        """Get comprehensive project overview data"""
        if not project:
            return {}

        tasks = project.task_ids
        total_tasks = len(tasks)

        # Task status counts
        todo_tasks = tasks.filtered(lambda t: t.stage_id.name.lower() in ['to do', 'new', 'draft'])
        progress_tasks = tasks.filtered(lambda t: 'progress' in t.stage_id.name.lower() or 'doing' in t.stage_id.name.lower())
        done_tasks = tasks.filtered(lambda t: t.stage_id.name.lower() in ['done', 'complete', 'closed'])

        # Budget calculations
        budget_info = self._get_project_budget_status(project)

        # Team stats
        team_members = tasks.mapped('user_ids')
        active_members = team_members.filtered(lambda u: u.active)

        return {
            'id': project.id,
            'name': project.name,
            'description': project.description or '',
            'progress_percentage': self._calculate_project_progress(project),

            # Task statistics
            'total_tasks': total_tasks,
            'todo_count': len(todo_tasks),
            'progress_count': len(progress_tasks),
            'done_count': len(done_tasks),

            # Budget information
            'budget_allocated': budget_info.get('allocated', 0),
            'budget_spent': budget_info.get('spent', 0),
            'budget_remaining': budget_info.get('remaining', 0),
            'budget_percentage': budget_info.get('percentage', 0),
            'over_budget': budget_info.get('over_budget', False),

            # Team information
            'team_size': len(active_members),
            'active_workers': len(team_members.filtered(lambda u: u.id in progress_tasks.mapped('user_ids.id'))),

            # Timeline
            'deadline': project.date.strftime('%Y-%m-%d') if project.date else None,
            'days_remaining': (project.date - fields.Date.today()).days if project.date else None,
        }

    def _get_task_board_data(self, project):
        """Get Kanban board data for tasks"""
        if not project:
            return {'stages': [], 'tasks': []}

        tasks = project.task_ids
        stages = project.type_ids or self.env['project.task.type'].search([])

        # Group tasks by stage
        task_data = []
        for task in tasks:
            budget_info = self._get_task_budget_info(task)

            task_data.append({
                'id': task.id,
                'name': task.name,
                'stage_id': task.stage_id.id if task.stage_id else None,
                'stage_name': task.stage_id.name if task.stage_id else 'No Stage',
                'priority': task.priority,
                'assignees': [{'id': u.id, 'name': u.name} for u in task.user_ids],
                'deadline': task.date_deadline.strftime('%Y-%m-%d') if task.date_deadline else None,
                'budget_allocated': budget_info.get('allocated', 0),
                'budget_spent': budget_info.get('spent', 0),
                'budget_percentage': budget_info.get('percentage', 0),
                'is_over_budget': budget_info.get('over_budget', False),
                'parent_task': task.parent_id.name if task.parent_id else None,
            })

        stages_data = [{
            'id': stage.id,
            'name': stage.name,
            'sequence': stage.sequence,
            'task_count': len(tasks.filtered(lambda t: t.stage_id.id == stage.id)),
        } for stage in stages]

        return {
            'stages': stages_data,
            'tasks': task_data,
        }

    def _get_budget_monitor_data(self, project):
        """Get budget monitoring data with category breakdown"""
        if not project:
            return {}

        # Get all budget lines for this project
        budget_lines = self.env['construction.project.budget.line'].search([
            ('budget_id.project_id', '=', project.id)
        ])

        # Category breakdown
        categories = {}
        total_allocated = 0
        total_spent = 0

        for line in budget_lines:
            cat_name = line.category_id.name if line.category_id else 'Uncategorized'
            if cat_name not in categories:
                categories[cat_name] = {
                    'allocated': 0,
                    'spent': 0,
                    'count': 0
                }

            categories[cat_name]['allocated'] += line.budget_amount
            categories[cat_name]['spent'] += line.spent_amount
            categories[cat_name]['count'] += 1

            total_allocated += line.budget_amount
            total_spent += line.spent_amount

        # Recent expenses
        recent_expenses = self.env['hr.expense'].search([
            ('construction_project_id', '=', project.id),
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=7))
        ], order='create_date desc', limit=10)

        expense_data = [{
            'id': exp.id,
            'name': exp.name,
            'amount': exp.total_amount,
            'date': exp.date.strftime('%Y-%m-%d') if exp.date else '',
            'state': exp.state,
            'employee': exp.employee_id.name,
            'category': exp.budget_category_id.name if hasattr(exp, 'budget_category_id') and exp.budget_category_id else 'General',
        } for exp in recent_expenses]

        # Budget alerts
        alerts = []
        for cat_name, cat_data in categories.items():
            if cat_data['allocated'] > 0:
                percentage = (cat_data['spent'] / cat_data['allocated']) * 100
                if percentage > 90:
                    alerts.append({
                        'type': 'danger' if percentage > 100 else 'warning',
                        'category': cat_name,
                        'message': f"{cat_name} is {percentage:.1f}% of budget",
                        'percentage': percentage
                    })

        return {
            'total_allocated': total_allocated,
            'total_spent': total_spent,
            'total_percentage': (total_spent / total_allocated * 100) if total_allocated > 0 else 0,
            'categories': categories,
            'recent_expenses': expense_data,
            'budget_alerts': alerts,
            'pending_approvals': len(recent_expenses.filtered(lambda e: e.state == 'reported')),
        }

    def _get_team_overview(self, project):
        """Get team management overview"""
        if not project:
            return {}

        # Get all team members from project tasks
        team_members = project.task_ids.mapped('user_ids')

        team_data = []
        for member in team_members:
            member_tasks = project.task_ids.filtered(lambda t: member in t.user_ids)
            active_tasks = member_tasks.filtered(lambda t: t.stage_id.name.lower() not in ['done', 'complete', 'closed'])

            # Get recent expenses by this member
            recent_expenses = self.env['hr.expense'].search([
                ('employee_id.user_id', '=', member.id),
                ('construction_project_id', '=', project.id),
                ('state', '=', 'reported')
            ])

            team_data.append({
                'id': member.id,
                'name': member.name,
                'email': member.email,
                'total_tasks': len(member_tasks),
                'active_tasks': len(active_tasks),
                'completed_tasks': len(member_tasks) - len(active_tasks),
                'pending_expenses': len(recent_expenses),
                'last_activity': self._get_user_last_activity(member, project),
            })

        return {
            'team_members': team_data,
            'total_members': len(team_members),
            'active_members': len([m for m in team_data if m['active_tasks'] > 0]),
            'pending_expense_approvals': sum(m['pending_expenses'] for m in team_data),
        }

    def _get_recent_activity(self, project):
        """Get recent project activity feed"""
        if not project:
            return []

        activities = []

        # Recent task updates (last 7 days)
        recent_tasks = self.env['project.task'].search([
            ('project_id', '=', project.id),
            ('write_date', '>=', fields.Datetime.now() - timedelta(days=7))
        ], order='write_date desc', limit=10)

        for task in recent_tasks:
            activities.append({
                'type': 'task',
                'icon': 'fa-tasks',
                'title': f"Task updated: {task.name}",
                'description': f"Stage: {task.stage_id.name if task.stage_id else 'No Stage'}",
                'user': task.user_ids[0].name if task.user_ids else 'Unassigned',
                'date': task.write_date.strftime('%Y-%m-%d %H:%M'),
                'priority': task.priority,
            })

        # Recent expenses
        recent_expenses = self.env['hr.expense'].search([
            ('construction_project_id', '=', project.id),
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=7))
        ], order='create_date desc', limit=5)

        for expense in recent_expenses:
            activities.append({
                'type': 'expense',
                'icon': 'fa-money-bill',
                'title': f"Expense: {expense.name}",
                'description': f"Amount: ${expense.total_amount:.2f}",
                'user': expense.employee_id.name,
                'date': expense.create_date.strftime('%Y-%m-%d %H:%M'),
                'state': expense.state,
            })

        # Sort by date and return latest
        activities.sort(key=lambda x: x['date'], reverse=True)
        return activities[:15]

    # Helper methods
    def _calculate_project_progress(self, project):
        """Calculate overall project progress percentage"""
        if not project or not project.task_ids:
            return 0

        total_tasks = len(project.task_ids)
        completed_tasks = len(project.task_ids.filtered(
            lambda t: t.stage_id.name.lower() in ['done', 'complete', 'closed']
        ))

        return int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    def _get_project_budget_status(self, project):
        """Get project budget status summary"""
        if not project:
            return {'allocated': 0, 'spent': 0, 'remaining': 0, 'percentage': 0, 'over_budget': False}

        budget_lines = self.env['construction.project.budget.line'].search([
            ('budget_id.project_id', '=', project.id)
        ])

        allocated = sum(budget_lines.mapped('budget_amount'))
        spent = sum(budget_lines.mapped('spent_amount'))
        remaining = allocated - spent
        percentage = (spent / allocated * 100) if allocated > 0 else 0

        return {
            'allocated': allocated,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage,
            'over_budget': spent > allocated
        }

    def _get_task_budget_info(self, task):
        """Get budget information for a specific task"""
        if hasattr(task, 'budget_line_id') and task.budget_line_id:
            line = task.budget_line_id
            percentage = (line.spent_amount / line.budget_amount * 100) if line.budget_amount > 0 else 0
            return {
                'allocated': line.budget_amount,
                'spent': line.spent_amount,
                'percentage': percentage,
                'over_budget': line.spent_amount > line.budget_amount
            }
        return {'allocated': 0, 'spent': 0, 'percentage': 0, 'over_budget': False}

    def _get_user_last_activity(self, user, project):
        """Get user's last activity in the project"""
        # Check last task update
        last_task_update = self.env['project.task'].search([
            ('project_id', '=', project.id),
            ('user_ids', 'in', [user.id])
        ], order='write_date desc', limit=1)

        if last_task_update:
            return last_task_update.write_date.strftime('%Y-%m-%d')

        return 'No recent activity'

    def action_load_dashboard_data(self):
        """Load dashboard data for selected project"""
        if not self.project_id:
            self.dashboard_status = 'Please select a project first'
            return

        try:
            data = self.get_dashboard_data(self.project_id.id)

            if 'error' in data:
                self.dashboard_status = data['error']
                return

            project_info = data.get('current_project', {})
            budget_info = data.get('budget_monitor', {})
            team_info = data.get('team_overview', {})

            # Update dashboard fields
            self.project_name = project_info.get('name', '')
            self.total_tasks = project_info.get('total_tasks', 0)
            self.todo_count = project_info.get('todo_count', 0)
            self.progress_count = project_info.get('progress_count', 0)
            self.done_count = project_info.get('done_count', 0)
            self.progress_percentage = project_info.get('progress_percentage', 0)

            self.budget_allocated = project_info.get('budget_allocated', 0)
            self.budget_spent = project_info.get('budget_spent', 0)
            self.budget_remaining = project_info.get('budget_remaining', 0)
            self.budget_percentage = project_info.get('budget_percentage', 0)
            self.over_budget = project_info.get('over_budget', False)

            self.team_size = project_info.get('team_size', 0)
            self.active_workers = project_info.get('active_workers', 0)
            self.pending_approvals = team_info.get('pending_expense_approvals', 0)

            self.last_refresh = fields.Datetime.now()
            self.dashboard_status = f'Dashboard loaded successfully for {self.project_name} at {self.last_refresh.strftime("%Y-%m-%d %H:%M")}'

            _logger.info(f"Dashboard data loaded for project {self.project_id.name}")

        except Exception as e:
            _logger.error(f"Error loading dashboard data: {str(e)}")
            self.dashboard_status = f'Error loading dashboard data: {str(e)}'

    @api.model
    def refresh_dashboard(self, project_id=None):
        """Refresh dashboard data"""
        return self.get_dashboard_data(project_id)
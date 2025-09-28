# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectBudgetLine(models.Model):
    _inherit = 'construction.project.budget.line'

    # Task integration
    task_id = fields.Many2one(
        'project.task',
        string='Project Task',
        help='Linked project task for work management'
    )
    task_stage = fields.Char(
        related='task_id.stage_id.name',
        string='Task Status',
        readonly=True
    )
    task_progress = fields.Float(
        string='Task Progress (%)',
        compute='_compute_task_progress',
        readonly=True,
        help='Computed based on task stage completion'
    )
    assignee_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        compute='_compute_task_assignee',
        readonly=True
    )

    # Enhanced tracking
    has_linked_task = fields.Boolean(
        string='Has Task',
        compute='_compute_has_linked_task',
        help='True if budget line has a linked project task'
    )

    @api.depends('task_id')
    def _compute_has_linked_task(self):
        for line in self:
            line.has_linked_task = bool(line.task_id)

    @api.depends('task_id.stage_id')
    def _compute_task_progress(self):
        """Compute task progress based on stage"""
        for line in self:
            if line.task_id and line.task_id.stage_id:
                # Simple progress mapping based on stage
                stage_name = line.task_id.stage_id.name.lower()
                if 'done' in stage_name or 'complete' in stage_name or 'finish' in stage_name:
                    line.task_progress = 100.0
                elif 'progress' in stage_name or 'doing' in stage_name or 'working' in stage_name:
                    line.task_progress = 50.0
                elif 'review' in stage_name or 'test' in stage_name:
                    line.task_progress = 75.0
                else:
                    line.task_progress = 0.0
            else:
                line.task_progress = 0.0

    @api.depends('task_id.user_ids')
    def _compute_task_assignee(self):
        """Get the first assigned user from the task"""
        for line in self:
            if line.task_id and line.task_id.user_ids:
                line.assignee_id = line.task_id.user_ids[0]
            else:
                line.assignee_id = False

    def action_view_task(self):
        """Open the linked project task"""
        if not self.task_id:
            return

        return {
            'type': 'ir.actions.act_window',
            'name': 'Project Task',
            'res_model': 'project.task',
            'res_id': self.task_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_task(self):
        """Create a new project task linked to this budget line"""
        if self.task_id:
            # If task already exists, open it
            return self.action_view_task()

        # Create new task
        task = self.env['project.task'].create({
            'name': self.name,
            'project_id': self.project_id.id,
            'budget_line_id': self.id,
            'description': f"Task created from budget line: {self.name}",
        })

        # Link back to budget line
        self.task_id = task.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Project Task',
            'res_model': 'project.task',
            'res_id': task.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_task_expenses(self):
        """View expenses for this budget line through task view"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Task Expenses',
            'res_model': 'hr.expense',
            'view_mode': 'tree,form',
            'domain': [('project_budget_line_id', '=', self.id)],
            'context': {
                'default_project_budget_line_id': self.id,
                'default_construction_project_id': self.project_id.id,
                'default_budget_category_id': self.category_id.id,
            }
        }
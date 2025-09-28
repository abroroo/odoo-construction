# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Smeta integration fields
    smeta_number = fields.Char(
        string='Smeta Number',
        help='Original smeta task number (e.g., 1.1, 2.3)',
        index=True
    )
    smeta_section = fields.Char(
        string='Smeta Section',
        help='РАЗДЕЛ section from smeta file'
    )
    smeta_type = fields.Selection([
        ('main_task', 'Main Task'),
        ('sub_task', 'Sub-task'),
        ('additional_task', 'Additional Task'),
    ], string='Smeta Type', help='Type of task in smeta hierarchy')

    # Budget integration
    budget_line_id = fields.Many2one(
        'construction.project.budget.line',
        string='Budget Line',
        help='Linked budget line for expense tracking'
    )
    budget_amount = fields.Float(
        related='budget_line_id.budget_amount',
        string='Budget Amount',
        readonly=True
    )
    spent_amount = fields.Float(
        related='budget_line_id.spent_amount',
        string='Spent Amount',
        readonly=True
    )
    remaining_budget = fields.Float(
        related='budget_line_id.remaining_amount',
        string='Remaining Budget',
        readonly=True
    )
    budget_category = fields.Char(
        related='budget_line_id.category_id.name',
        string='Budget Category',
        readonly=True
    )

    # Enhanced task management with direct quantity fields
    planned_quantity = fields.Float(
        string='Planned Quantity',
        help='Planned quantity from smeta import',
        default=1.0
    )
    actual_quantity = fields.Float(
        string='Actual Quantity',
        help='Actual quantity completed',
        default=0.0
    )
    quantity_uom = fields.Char(
        string='Unit of Measure',
        help='Unit like m², kg, hours, etc.'
    )
    quantity_per_unit = fields.Float(
        string='Quantity per Unit',
        help='Rate or factor from smeta',
        default=1.0
    )

    # Progress tracking
    is_over_budget = fields.Boolean(
        string='Over Budget',
        compute='_compute_budget_status',
        help='True if task spending exceeds budget'
    )
    budget_utilization = fields.Float(
        string='Budget Utilization (%)',
        compute='_compute_budget_status',
        help='Percentage of budget used'
    )

    @api.depends('budget_amount', 'spent_amount')
    def _compute_budget_status(self):
        for task in self:
            if task.budget_amount > 0:
                task.budget_utilization = (task.spent_amount / task.budget_amount) * 100
                task.is_over_budget = task.spent_amount > task.budget_amount
            else:
                task.budget_utilization = 0.0
                task.is_over_budget = False

    def action_view_budget_line(self):
        """Open the linked budget line"""
        if not self.budget_line_id:
            return

        return {
            'type': 'ir.actions.act_window',
            'name': 'Budget Line',
            'res_model': 'construction.project.budget.line',
            'res_id': self.budget_line_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_expenses(self):
        """View expenses recorded against this task's budget line"""
        if not self.budget_line_id:
            return

        return {
            'type': 'ir.actions.act_window',
            'name': 'Related Expenses',
            'res_model': 'hr.expense',
            'view_mode': 'tree,form',
            'domain': [('project_budget_line_id', '=', self.budget_line_id.id)],
            'context': {
                'default_project_budget_line_id': self.budget_line_id.id,
                'default_construction_project_id': self.project_id.id,
                'default_budget_category_id': self.budget_line_id.category_id.id,
            }
        }

    def action_create_expense(self):
        """Quick action to create expense for this task"""
        if not self.budget_line_id:
            return

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Expense',
            'res_model': 'hr.expense',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f'Expense for {self.name}',
                'default_project_budget_line_id': self.budget_line_id.id,
                'default_construction_project_id': self.project_id.id,
                'default_budget_category_id': self.budget_line_id.category_id.id,
            }
        }

    @api.model
    def create_additional_task(self, project_id, name, description=None, estimated_quantity=1.0):
        """
        Create additional task for foreman "новая задача" workflow.

        Args:
            project_id (int): Target project ID
            name (str): Task name
            description (str, optional): Task description
            estimated_quantity (float, optional): Estimated quantity for the task

        Returns:
            recordset: Created project.task record
        """
        project = self.env['project.project'].browse(project_id)
        if not project.exists():
            raise UserError(_("Project does not exist."))

        # Get next sequence number for additional tasks
        additional_tasks = self.search([
            ('project_id', '=', project_id),
            ('smeta_type', '=', 'additional_task')
        ])
        next_sequence = len(additional_tasks) + 1000  # Start from 1000 to avoid conflicts

        # Create task with Additional Task tag
        additional_tag = self._get_or_create_additional_task_tag()

        task_vals = {
            'name': name,
            'project_id': project_id,
            'description': description or f"<strong>Additional Task</strong><br/><br/>"
                                       f"Created by foreman for additional construction work.<br/>"
                                       f"<strong>Estimated Quantity:</strong> {estimated_quantity}<br/>"
                                       f"<em>Not part of original смета</em>",
            'smeta_type': 'additional_task',
            'planned_quantity': estimated_quantity,
            'actual_quantity': 0.0,
            'sequence': next_sequence,
            'stage_id': self._get_todo_stage_id(project_id),
            'tag_ids': [(6, 0, [additional_tag.id])],
        }

        task = self.create(task_vals)

        # Log creation for audit trail
        task.message_post(
            body=f"Additional task created by foreman for construction work not in original смета.",
            subtype_xmlid='mail.mt_note'
        )

        return task

    def _get_todo_stage_id(self, project_id):
        """Get or create 'To Do' stage for the project"""
        project = self.env['project.project'].browse(project_id)

        # Look for existing 'To Do' stage
        todo_stage = project.type_ids.filtered(lambda s: s.name.lower() in ['to do', 'todo', 'new', 'draft'])
        if todo_stage:
            return todo_stage[0].id

        # Look for first stage
        if project.type_ids:
            return project.type_ids[0].id

        # Create default 'To Do' stage
        stage = self.env['project.task.type'].create({
            'name': 'To Do',
            'sequence': 1,
            'project_ids': [(6, 0, [project_id])],
        })
        return stage.id

    def _get_or_create_additional_task_tag(self):
        """Get or create a tag for additional (non-smeta) tasks"""
        tag = self.env['project.tags'].search([('name', '=', 'Additional Task')], limit=1)
        if not tag:
            tag = self.env['project.tags'].create({
                'name': 'Additional Task',
                'color': 3,  # Orange color
            })
        return tag
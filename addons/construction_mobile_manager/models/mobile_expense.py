# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class MobileExpense(models.Model):
    _name = 'construction.mobile.expense'
    _description = 'Mobile Expense Entry'

    name = fields.Char(string='Description', required=True)
    amount = fields.Float(string='Amount', required=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)

    # Task and project selection
    project_id = fields.Many2one('project.project', string='Project', required=True)
    task_id = fields.Many2one('project.task', string='Task', domain="[('project_id', '=', project_id), ('user_ids', 'in', [uid])]", required=True)

    # Material selection
    material_type = fields.Selection([
        ('cement', 'Cement'),
        ('steel', 'Steel/Rebar'),
        ('lumber', 'Lumber/Wood'),
        ('electrical', 'Electrical Supplies'),
        ('plumbing', 'Plumbing Supplies'),
        ('tools', 'Tools & Equipment'),
        ('fuel', 'Fuel & Transportation'),
        ('other', 'Other Materials'),
    ], string='Material Type', required=True)

    # User and employee
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    employee_id = fields.Many2one('hr.employee', string='Employee', compute='_compute_employee', store=True)

    # Photo upload
    receipt_image = fields.Binary(string='Receipt Photo', attachment=True)
    receipt_filename = fields.Char(string='Receipt Filename')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    ], string='Status', default='draft')

    # Link to actual expense
    expense_id = fields.Many2one('hr.expense', string='HR Expense')

    @api.depends('user_id')
    def _compute_employee(self):
        for record in self:
            employee = self.env['hr.employee'].search([('user_id', '=', record.user_id.id)], limit=1)
            record.employee_id = employee.id if employee else False

    def action_submit_expense(self):
        """Convert mobile expense to HR expense and submit"""
        if not self.employee_id:
            # Create employee if doesn't exist
            self.employee_id = self.env['hr.employee'].create({
                'name': self.user_id.name,
                'user_id': self.user_id.id,
            })

        # Create HR expense
        expense_vals = {
            'name': self.name,
            'employee_id': self.employee_id.id,
            'total_amount': self.amount,
            'date': self.date,
            'construction_project_id': self.project_id.id,
        }

        # Add budget line if task has one
        if hasattr(self.task_id, 'budget_line_id') and self.task_id.budget_line_id:
            expense_vals.update({
                'project_budget_line_id': self.task_id.budget_line_id.id,
                'budget_category_id': self.task_id.budget_line_id.category_id.id,
            })

        # Add receipt image if available
        if self.receipt_image:
            expense_vals.update({
                'attachment_ids': [(0, 0, {
                    'name': self.receipt_filename or f'Receipt_{self.name}.jpg',
                    'datas': self.receipt_image,
                    'res_model': 'hr.expense',
                })]
            })

        expense = self.env['hr.expense'].create(expense_vals)

        # Link to mobile expense
        self.expense_id = expense.id
        self.state = 'submitted'

        # Submit the expense
        try:
            expense.action_submit_expenses()
        except Exception as e:
            _logger.warning(f"Could not auto-submit expense {expense.id}: {str(e)}")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Expense Submitted',
                'message': f'Expense "{self.name}" has been submitted for approval.',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def get_user_projects(self):
        """Get projects where user has assigned tasks"""
        user = self.env.user
        tasks = self.env['project.task'].search([('user_ids', 'in', [user.id])])
        projects = tasks.mapped('project_id')

        return [{
            'id': project.id,
            'name': project.name,
            'task_count': len(tasks.filtered(lambda t: t.project_id.id == project.id))
        } for project in projects]

    @api.model
    def get_project_tasks(self, project_id):
        """Get user's tasks for a specific project"""
        user = self.env.user
        tasks = self.env['project.task'].search([
            ('project_id', '=', project_id),
            ('user_ids', 'in', [user.id])
        ])

        return [{
            'id': task.id,
            'name': task.name,
            'stage': task.stage_id.name if task.stage_id else 'No Stage',
            'has_budget': bool(hasattr(task, 'budget_line_id') and task.budget_line_id),
        } for task in tasks]


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    mobile_expense_id = fields.Many2one('construction.mobile.expense', string='Mobile Expense')

    def get_mobile_expense_data(self):
        """Get expense data for mobile display"""
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.total_amount,
            'date': self.date,
            'state': self.state,
            'project': self.construction_project_id.name if self.construction_project_id else '',
            'task': self.project_budget_line_id.task_id.name if hasattr(self, 'project_budget_line_id') and self.project_budget_line_id and hasattr(self.project_budget_line_id, 'task_id') and self.project_budget_line_id.task_id else '',
        }
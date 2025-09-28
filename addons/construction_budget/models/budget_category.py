# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BudgetCategory(models.Model):
    _name = 'construction.budget.category'
    _description = 'Construction Budget Category'
    _order = 'sequence, name'

    name = fields.Char(
        string='Category Name',
        required=True,
        help='Budget category name (e.g., Materials, Labor)'
    )
    code = fields.Char(
        string='Category Code',
        required=True,
        help='Short code for the category (e.g., MAT, LAB)'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of appearance'
    )
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color for visual representation'
    )
    parent_id = fields.Many2one(
        'construction.budget.category',
        string='Parent Category',
        help='Parent category for hierarchical structure'
    )
    child_ids = fields.One2many(
        'construction.budget.category',
        'parent_id',
        string='Sub-categories'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of what this category covers'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    # Statistics
    budget_line_ids = fields.One2many(
        'construction.project.budget.line',
        'category_id',
        string='Budget Lines'
    )
    total_budget = fields.Float(
        string='Total Budget',
        compute='_compute_totals',
        store=True,
        help='Total budgeted amount for this category across all projects'
    )
    total_spent = fields.Float(
        string='Total Spent',
        compute='_compute_totals',
        store=True,
        help='Total spent amount for this category across all projects'
    )

    @api.depends('budget_line_ids.budget_amount', 'budget_line_ids.spent_amount')
    def _compute_totals(self):
        for category in self:
            category.total_budget = sum(category.budget_line_ids.mapped('budget_amount'))
            category.total_spent = sum(category.budget_line_ids.mapped('spent_amount'))

    @api.constrains('parent_id')
    def _check_parent_recursion(self):
        if not self._check_recursion():
            raise models.ValidationError('You cannot create recursive categories.')

    def name_get(self):
        result = []
        for category in self:
            if category.parent_id:
                name = f"{category.parent_id.name} / {category.name}"
            else:
                name = category.name
            result.append((category.id, name))
        return result
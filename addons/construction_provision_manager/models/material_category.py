# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaterialCategory(models.Model):
    _name = 'construction.material.category'
    _description = 'Material Category'
    _order = 'sequence, name'

    name = fields.Char(
        string='Category Name',
        required=True,
        help='Material category name (e.g., Construction Materials, Tools, Equipment)'
    )
    code = fields.Char(
        string='Category Code',
        required=True,
        help='Short code for category identification'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of the material category'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display in lists'
    )
    color = fields.Integer(
        string='Color',
        help='Color for kanban view'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    # Statistics
    material_count = fields.Integer(
        string='Material Count',
        compute='_compute_material_count',
        help='Number of materials in this category'
    )

    @api.depends('name')
    def _compute_material_count(self):
        for category in self:
            category.material_count = self.env['construction.common.material'].search_count([
                ('category_id', '=', category.id)
            ])

    def action_view_materials(self):
        """Open materials in this category"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Materials - {self.name}',
            'res_model': 'construction.common.material',
            'view_mode': 'tree,form',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id}
        }
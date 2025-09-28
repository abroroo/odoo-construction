# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CommonMaterial(models.Model):
    _name = 'construction.common.material'
    _description = 'Common Construction Materials'
    _order = 'category_id, name'

    name = fields.Char(
        string='Material Name',
        required=True,
        help='Name of the material (e.g., Portland Cement, Steel Rebar)'
    )
    category_id = fields.Many2one(
        'construction.material.category',
        string='Category',
        required=True,
        help='Material category classification'
    )
    default_unit = fields.Selection([
        ('kg', 'Kilograms'),
        ('tons', 'Tons'),
        ('m', 'Meters'),
        ('m2', 'Square Meters'),
        ('m3', 'Cubic Meters'),
        ('pcs', 'Pieces'),
        ('boxes', 'Boxes'),
        ('bags', 'Bags'),
        ('liters', 'Liters'),
        ('hours', 'Hours'),
        ('days', 'Days'),
    ], string='Default Unit', required=True, default='pcs')

    description = fields.Text(
        string='Description',
        help='Detailed description of the material'
    )
    specifications = fields.Text(
        string='Specifications',
        help='Technical specifications of the material'
    )
    average_price = fields.Float(
        string='Average Price',
        help='Average market price for reference'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    is_frequently_used = fields.Boolean(
        string='Frequently Used',
        default=False,
        help='Mark as frequently used for quick access'
    )

    # Usage statistics
    usage_count = fields.Integer(
        string='Usage Count',
        compute='_compute_usage_stats',
        help='Number of times this material has been used'
    )
    last_used_date = fields.Datetime(
        string='Last Used',
        compute='_compute_usage_stats',
        help='Last time this material was used'
    )

    @api.depends('name')
    def _compute_usage_stats(self):
        for material in self:
            deliveries = self.env['construction.material.delivery'].search([
                ('material_name', '=', material.name)
            ])
            material.usage_count = len(deliveries)
            material.last_used_date = deliveries[0].delivery_date if deliveries else False

    def action_quick_add_to_project(self):
        """Quick add this material to a project"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Add {self.name} to Project',
            'res_model': 'construction.material.delivery',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_material_name': self.name,
                'default_category_id': self.category_id.id,
                'default_unit': self.default_unit,
                'default_unit_price': self.average_price,
            }
        }
# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectMaterial(models.Model):
    _name = 'construction.project.material'
    _description = 'Project Material Inventory'
    _order = 'project_id, category_id, material_name'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        help='Project for this material inventory'
    )
    material_name = fields.Char(
        string='Material Name',
        required=True,
        help='Name of the material'
    )
    category_id = fields.Many2one(
        'construction.material.category',
        string='Category',
        required=True,
        help='Material category'
    )

    # Inventory Summary
    total_delivered = fields.Float(
        string='Total Delivered',
        compute='_compute_inventory_summary',
        store=True,
        help='Total quantity delivered to project'
    )
    total_consumed = fields.Float(
        string='Total Consumed',
        compute='_compute_inventory_summary',
        store=True,
        help='Total quantity consumed in project'
    )
    current_stock = fields.Float(
        string='Current Stock',
        compute='_compute_inventory_summary',
        store=True,
        help='Current available quantity'
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_inventory_summary',
        store=True,
        help='Total cost of all deliveries'
    )

    # Last Activity
    last_delivery_date = fields.Datetime(
        string='Last Delivery',
        compute='_compute_inventory_summary',
        store=True,
        help='Date of last delivery'
    )
    last_consumption_date = fields.Datetime(
        string='Last Consumption',
        compute='_compute_inventory_summary',
        store=True,
        help='Date of last consumption'
    )

    # Status
    status = fields.Selection([
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('over_stock', 'Over Stock'),
    ], string='Status', compute='_compute_status', store=True)

    # Related deliveries
    delivery_ids = fields.One2many(
        'construction.material.delivery',
        string='Deliveries',
        compute='_compute_deliveries'
    )
    delivery_count = fields.Integer(
        string='Delivery Count',
        compute='_compute_deliveries',
        store=True
    )

    @api.depends('project_id', 'material_name')
    def _compute_deliveries(self):
        for material in self:
            deliveries = self.env['construction.material.delivery'].search([
                ('project_id', '=', material.project_id.id),
                ('material_name', '=', material.material_name)
            ])
            material.delivery_ids = deliveries
            material.delivery_count = len(deliveries)

    @api.depends('delivery_ids.quantity', 'delivery_ids.consumed_quantity', 'delivery_ids.total_cost')
    def _compute_inventory_summary(self):
        for material in self:
            deliveries = material.delivery_ids

            material.total_delivered = sum(deliveries.mapped('quantity'))
            material.total_consumed = sum(deliveries.mapped('consumed_quantity'))
            material.current_stock = material.total_delivered - material.total_consumed
            material.total_cost = sum(deliveries.mapped('total_cost'))

            # Last activity dates
            if deliveries:
                material.last_delivery_date = max(deliveries.mapped('delivery_date'))
                # Last consumption would need consumption tracking
                material.last_consumption_date = False
            else:
                material.last_delivery_date = False
                material.last_consumption_date = False

    @api.depends('current_stock')
    def _compute_status(self):
        for material in self:
            if material.current_stock <= 0:
                material.status = 'out_of_stock'
            elif material.current_stock < 10:  # Configurable threshold
                material.status = 'low_stock'
            else:
                material.status = 'in_stock'

    def action_view_deliveries(self):
        """View all deliveries for this material"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Deliveries - {self.material_name}',
            'res_model': 'construction.material.delivery',
            'view_mode': 'tree,form',
            'domain': [
                ('project_id', '=', self.project_id.id),
                ('material_name', '=', self.material_name)
            ],
            'context': {
                'default_project_id': self.project_id.id,
                'default_material_name': self.material_name,
                'default_category_id': self.category_id.id,
            }
        }

    def action_add_delivery(self):
        """Quick add delivery for this material"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Add {self.material_name}',
            'res_model': 'construction.material.delivery',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.project_id.id,
                'default_material_name': self.material_name,
                'default_category_id': self.category_id.id,
            }
        }

    @api.model
    def update_project_materials(self):
        """Update project material summary from deliveries"""
        # This method will be called to refresh the material inventory
        # when new deliveries are added
        deliveries = self.env['construction.material.delivery'].search([])

        # Group by project and material
        project_materials = {}
        for delivery in deliveries:
            key = (delivery.project_id.id, delivery.material_name, delivery.category_id.id)
            if key not in project_materials:
                project_materials[key] = {
                    'project_id': delivery.project_id.id,
                    'material_name': delivery.material_name,
                    'category_id': delivery.category_id.id,
                }

        # Create or update project material records
        for key, values in project_materials.items():
            existing = self.search([
                ('project_id', '=', values['project_id']),
                ('material_name', '=', values['material_name']),
                ('category_id', '=', values['category_id']),
            ])

            if not existing:
                self.create(values)
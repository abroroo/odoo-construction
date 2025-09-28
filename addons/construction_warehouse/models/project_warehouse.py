# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectWarehouse(models.Model):
    _name = 'construction.project.warehouse'
    _description = 'Project Warehouse - Physical Storage Location'
    _order = 'project_id, name'

    name = fields.Char(
        string='Warehouse Name',
        required=True,
        help='Name of the physical warehouse/storage area'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        help='Construction project this warehouse serves'
    )

    # Location Information
    address = fields.Text(
        string='Physical Address',
        help='Physical location of the warehouse'
    )
    warehouse_type = fields.Selection([
        ('on_site', 'On-Site Storage'),
        ('off_site', 'Off-Site Warehouse'),
        ('temporary', 'Temporary Storage'),
        ('supplier_yard', 'Supplier Yard'),
    ], string='Warehouse Type', required=True, default='on_site')

    # Capacity and Status
    storage_capacity = fields.Float(
        string='Storage Capacity (m³)',
        help='Maximum storage capacity in cubic meters'
    )
    current_utilization = fields.Float(
        string='Current Utilization (%)',
        compute='_compute_utilization',
        help='Percentage of warehouse capacity currently used'
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this warehouse is currently operational'
    )

    # Responsible Persons
    warehouse_manager_id = fields.Many2one(
        'res.users',
        string='Warehouse Manager',
        help='Person responsible for this warehouse'
    )

    # Stock Information
    stock_ids = fields.One2many(
        'construction.warehouse.stock',
        'warehouse_id',
        string='Current Stock',
        help='Materials currently stored in this warehouse'
    )
    stock_count = fields.Integer(
        string='Material Types',
        compute='_compute_stock_info',
        help='Number of different material types in warehouse'
    )
    total_stock_value = fields.Float(
        string='Total Stock Value',
        compute='_compute_stock_info',
        help='Total value of materials in warehouse'
    )

    # Recent Activity
    recent_receipts = fields.One2many(
        'construction.material.receipt',
        'warehouse_id',
        string='Recent Receipts',
        domain=[('receipt_date', '>=', fields.Date.today())],
        help='Materials received today'
    )
    recent_consumptions = fields.One2many(
        'construction.material.consumption',
        'warehouse_id',
        string='Recent Consumptions',
        domain=[('consumption_date', '>=', fields.Date.today())],
        help='Materials consumed today'
    )

    @api.depends('stock_ids.quantity', 'stock_ids.unit_cost')
    def _compute_stock_info(self):
        for warehouse in self:
            warehouse.stock_count = len(warehouse.stock_ids)
            warehouse.total_stock_value = sum(
                stock.quantity * stock.unit_cost
                for stock in warehouse.stock_ids
            )

    @api.depends('stock_ids', 'storage_capacity')
    def _compute_utilization(self):
        for warehouse in self:
            if warehouse.storage_capacity > 0:
                # Simple calculation - would need material volumes for accuracy
                used_space = len(warehouse.stock_ids) * 10  # Rough estimate
                warehouse.current_utilization = (used_space / warehouse.storage_capacity) * 100
            else:
                warehouse.current_utilization = 0

    def action_view_stock(self):
        """View all stock in this warehouse"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Stock in {self.name}',
            'res_model': 'construction.warehouse.stock',
            'view_mode': 'tree,form',
            'domain': [('warehouse_id', '=', self.id)],
            'context': {
                'default_warehouse_id': self.id,
                'default_project_id': self.project_id.id,
            }
        }

    def action_receive_material(self):
        """Quick receive material to this warehouse"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Receive Material - {self.name}',
            'res_model': 'construction.material.receipt',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_warehouse_id': self.id,
                'default_project_id': self.project_id.id,
            }
        }

    def action_consume_material(self):
        """Site manager consume material from warehouse"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Consume Material - {self.name}',
            'res_model': 'construction.material.consumption',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_warehouse_id': self.id,
                'default_project_id': self.project_id.id,
            }
        }

    def action_warehouse_dashboard(self):
        """Open warehouse dashboard"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Warehouse Dashboard - {self.name}',
            'res_model': 'construction.project.warehouse',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
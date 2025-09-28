# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ConstructionMaterial(models.Model):
    _name = 'construction.material'
    _description = 'Construction Materials - Physical Goods'
    _order = 'category, name'

    name = fields.Char(
        string='Material Name',
        required=True,
        help='Name of the construction material'
    )
    category = fields.Selection([
        ('concrete', 'Concrete & Cement'),
        ('steel', 'Steel & Metal'),
        ('lumber', 'Lumber & Wood'),
        ('masonry', 'Masonry & Stone'),
        ('roofing', 'Roofing Materials'),
        ('insulation', 'Insulation'),
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('hardware', 'Hardware & Fasteners'),
        ('tools', 'Tools & Equipment'),
        ('safety', 'Safety Equipment'),
        ('other', 'Other'),
    ], string='Category', required=True, default='other')

    # Physical Properties
    unit_of_measure = fields.Selection([
        ('kg', 'Kilograms'),
        ('tons', 'Tons'),
        ('m', 'Meters'),
        ('m2', 'Square Meters'),
        ('m3', 'Cubic Meters'),
        ('pcs', 'Pieces'),
        ('boxes', 'Boxes'),
        ('bags', 'Bags'),
        ('sacks', 'Sacks'),
        ('rolls', 'Rolls'),
        ('sheets', 'Sheets'),
        ('liters', 'Liters'),
        ('sets', 'Sets'),
    ], string='Unit of Measure', required=True, default='pcs')

    weight_per_unit = fields.Float(
        string='Weight per Unit (kg)',
        help='Weight of one unit in kilograms'
    )
    volume_per_unit = fields.Float(
        string='Volume per Unit (m³)',
        help='Volume of one unit in cubic meters'
    )

    # Material Specifications
    description = fields.Text(
        string='Description',
        help='Detailed description of the material'
    )
    specifications = fields.Text(
        string='Technical Specifications',
        help='Technical specifications and requirements'
    )
    grade_quality = fields.Char(
        string='Grade/Quality',
        help='Material grade or quality specification (e.g., Grade 40 concrete)'
    )

    # Storage Requirements
    storage_requirements = fields.Text(
        string='Storage Requirements',
        help='Special storage requirements (temperature, humidity, etc.)'
    )
    shelf_life_days = fields.Integer(
        string='Shelf Life (Days)',
        help='Number of days material remains usable'
    )
    hazardous = fields.Boolean(
        string='Hazardous Material',
        help='Requires special handling'
    )

    # Supplier and Costing
    standard_cost = fields.Float(
        string='Standard Cost',
        help='Standard cost per unit'
    )
    preferred_supplier_id = fields.Many2one(
        'res.partner',
        string='Preferred Supplier',
        domain=[('is_company', '=', True)],
        help='Preferred supplier for this material'
    )

    # Usage Tracking
    active = fields.Boolean(
        string='Active',
        default=True
    )
    frequently_used = fields.Boolean(
        string='Frequently Used',
        help='Mark as frequently used for quick access'
    )

    # Stock Information (computed)
    total_stock_quantity = fields.Float(
        string='Total Stock',
        compute='_compute_stock_info',
        help='Total quantity across all warehouses'
    )
    total_stock_value = fields.Float(
        string='Total Stock Value',
        compute='_compute_stock_info',
        help='Total value across all warehouses'
    )
    warehouse_count = fields.Integer(
        string='Warehouses',
        compute='_compute_stock_info',
        help='Number of warehouses storing this material'
    )

    # Related Records
    stock_ids = fields.One2many(
        'construction.warehouse.stock',
        'material_id',
        string='Warehouse Stock',
        help='Stock levels across warehouses'
    )

    @api.depends('stock_ids.quantity', 'stock_ids.total_value')
    def _compute_stock_info(self):
        for material in self:
            material.total_stock_quantity = sum(material.stock_ids.mapped('quantity'))
            material.total_stock_value = sum(material.stock_ids.mapped('total_value'))
            material.warehouse_count = len(material.stock_ids.filtered('quantity'))

    def action_view_stock(self):
        """View stock across all warehouses"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Stock - {self.name}',
            'res_model': 'construction.warehouse.stock',
            'view_mode': 'tree,form',
            'domain': [('material_id', '=', self.id)],
            'context': {
                'default_material_id': self.id,
            }
        }

    def action_quick_receive(self):
        """Quick receive this material to a warehouse"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Receive {self.name}',
            'res_model': 'construction.material.receipt',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_material_id': self.id,
            }
        }

    @api.model
    def create_common_materials(self):
        """Create common construction materials"""
        common_materials = [
            # Concrete & Cement
            {'name': 'Portland Cement', 'category': 'concrete', 'unit_of_measure': 'bags', 'weight_per_unit': 50},
            {'name': 'Ready Mix Concrete', 'category': 'concrete', 'unit_of_measure': 'm3', 'weight_per_unit': 2400},
            {'name': 'Concrete Blocks', 'category': 'concrete', 'unit_of_measure': 'pcs', 'weight_per_unit': 15},

            # Steel & Metal
            {'name': 'Steel Rebar 12mm', 'category': 'steel', 'unit_of_measure': 'm', 'weight_per_unit': 0.888},
            {'name': 'Steel Rebar 16mm', 'category': 'steel', 'unit_of_measure': 'm', 'weight_per_unit': 1.578},
            {'name': 'Steel Beams', 'category': 'steel', 'unit_of_measure': 'm', 'weight_per_unit': 50},

            # Lumber
            {'name': 'Lumber 2x4', 'category': 'lumber', 'unit_of_measure': 'm', 'weight_per_unit': 2.5},
            {'name': 'Plywood 18mm', 'category': 'lumber', 'unit_of_measure': 'sheets', 'weight_per_unit': 25},

            # Masonry
            {'name': 'Red Bricks', 'category': 'masonry', 'unit_of_measure': 'pcs', 'weight_per_unit': 3.5},
            {'name': 'Sand', 'category': 'masonry', 'unit_of_measure': 'm3', 'weight_per_unit': 1600},
            {'name': 'Gravel', 'category': 'masonry', 'unit_of_measure': 'm3', 'weight_per_unit': 1800},

            # Hardware
            {'name': 'Nails 100mm', 'category': 'hardware', 'unit_of_measure': 'kg', 'weight_per_unit': 1},
            {'name': 'Screws 50mm', 'category': 'hardware', 'unit_of_measure': 'boxes', 'weight_per_unit': 2},

            # Safety
            {'name': 'Hard Hats', 'category': 'safety', 'unit_of_measure': 'pcs', 'weight_per_unit': 0.4},
            {'name': 'Safety Vests', 'category': 'safety', 'unit_of_measure': 'pcs', 'weight_per_unit': 0.2},
        ]

        for material_data in common_materials:
            material_data['frequently_used'] = True
            existing = self.search([('name', '=', material_data['name'])], limit=1)
            if not existing:
                self.create(material_data)
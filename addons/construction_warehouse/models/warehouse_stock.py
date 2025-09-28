# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WarehouseStock(models.Model):
    _name = 'construction.warehouse.stock'
    _description = 'Warehouse Stock - Current Inventory Levels'
    _order = 'warehouse_id, material_id'
    _rec_name = 'display_name'

    # Basic Information
    warehouse_id = fields.Many2one(
        'construction.project.warehouse',
        string='Warehouse',
        required=True,
        help='Physical warehouse where material is stored'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        related='warehouse_id.project_id',
        store=True,
        help='Project this stock belongs to'
    )
    material_id = fields.Many2one(
        'construction.material',
        string='Material',
        required=True,
        help='Type of construction material'
    )

    # Stock Quantities
    quantity = fields.Float(
        string='Current Quantity',
        default=0.0,
        help='Current quantity in warehouse'
    )
    reserved_quantity = fields.Float(
        string='Reserved Quantity',
        default=0.0,
        help='Quantity reserved for specific tasks'
    )
    available_quantity = fields.Float(
        string='Available Quantity',
        compute='_compute_available_quantity',
        store=True,
        help='Quantity available for consumption'
    )

    # Unit and Costing
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
    ], string='Unit', related='material_id.unit_of_measure', help='Unit of measurement')
    unit_cost = fields.Float(
        string='Average Unit Cost',
        compute='_compute_unit_cost',
        store=True,
        help='Average cost per unit based on receipts'
    )
    total_value = fields.Float(
        string='Total Stock Value',
        compute='_compute_total_value',
        store=True,
        help='Total value of current stock'
    )

    # Stock Status
    minimum_quantity = fields.Float(
        string='Minimum Stock Level',
        default=0.0,
        help='Alert when stock falls below this level'
    )
    stock_status = fields.Selection([
        ('ok', 'In Stock'),
        ('low', 'Low Stock'),
        ('out', 'Out of Stock'),
        ('excess', 'Excess Stock'),
    ], string='Stock Status', compute='_compute_stock_status', store=True)

    # Storage Information
    storage_location = fields.Char(
        string='Storage Location',
        help='Specific location within warehouse (e.g., Bay A, Shelf 3)'
    )
    storage_notes = fields.Text(
        string='Storage Notes',
        help='Special storage requirements or notes'
    )

    # Activity Tracking
    last_receipt_date = fields.Datetime(
        string='Last Receipt',
        compute='_compute_last_activity',
        help='Date of last material receipt'
    )
    last_consumption_date = fields.Datetime(
        string='Last Consumption',
        compute='_compute_last_activity',
        help='Date of last material consumption'
    )

    # Related Records
    receipt_ids = fields.One2many(
        'construction.material.receipt',
        string='Receipts',
        compute='_compute_related_records'
    )
    consumption_ids = fields.One2many(
        'construction.material.consumption',
        string='Consumptions',
        compute='_compute_related_records'
    )

    # Display Name
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('quantity', 'reserved_quantity')
    def _compute_available_quantity(self):
        for stock in self:
            stock.available_quantity = stock.quantity - stock.reserved_quantity

    @api.depends('receipt_ids.unit_cost', 'receipt_ids.quantity')
    def _compute_unit_cost(self):
        for stock in self:
            receipts = self.env['construction.material.receipt'].search([
                ('warehouse_id', '=', stock.warehouse_id.id),
                ('material_id', '=', stock.material_id.id)
            ])
            if receipts:
                total_cost = sum(r.quantity * r.unit_cost for r in receipts)
                total_quantity = sum(r.quantity for r in receipts)
                stock.unit_cost = total_cost / total_quantity if total_quantity > 0 else 0
            else:
                stock.unit_cost = 0

    @api.depends('quantity', 'unit_cost')
    def _compute_total_value(self):
        for stock in self:
            stock.total_value = stock.quantity * stock.unit_cost

    @api.depends('quantity', 'minimum_quantity', 'available_quantity')
    def _compute_stock_status(self):
        for stock in self:
            if stock.quantity <= 0:
                stock.stock_status = 'out'
            elif stock.quantity <= stock.minimum_quantity:
                stock.stock_status = 'low'
            elif stock.quantity > stock.minimum_quantity * 3:  # Arbitrary excess threshold
                stock.stock_status = 'excess'
            else:
                stock.stock_status = 'ok'

    @api.depends('warehouse_id', 'material_id')
    def _compute_last_activity(self):
        for stock in self:
            # Last receipt
            last_receipt = self.env['construction.material.receipt'].search([
                ('warehouse_id', '=', stock.warehouse_id.id),
                ('material_id', '=', stock.material_id.id)
            ], order='receipt_date desc', limit=1)
            stock.last_receipt_date = last_receipt.receipt_date if last_receipt else False

            # Last consumption
            last_consumption = self.env['construction.material.consumption'].search([
                ('warehouse_id', '=', stock.warehouse_id.id),
                ('material_id', '=', stock.material_id.id)
            ], order='consumption_date desc', limit=1)
            stock.last_consumption_date = last_consumption.consumption_date if last_consumption else False

    @api.depends('warehouse_id', 'material_id')
    def _compute_related_records(self):
        for stock in self:
            stock.receipt_ids = self.env['construction.material.receipt'].search([
                ('warehouse_id', '=', stock.warehouse_id.id),
                ('material_id', '=', stock.material_id.id)
            ])
            stock.consumption_ids = self.env['construction.material.consumption'].search([
                ('warehouse_id', '=', stock.warehouse_id.id),
                ('material_id', '=', stock.material_id.id)
            ])

    @api.depends('warehouse_id', 'material_id', 'quantity')
    def _compute_display_name(self):
        for stock in self:
            warehouse_name = stock.warehouse_id.name if stock.warehouse_id else 'No Warehouse'
            material_name = stock.material_id.name if stock.material_id else 'No Material'
            stock.display_name = f"{material_name} ({stock.quantity} {stock.unit_of_measure}) - {warehouse_name}"

    def action_receive_material(self):
        """Add material to this stock"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Receive {self.material_id.name}',
            'res_model': 'construction.material.receipt',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_warehouse_id': self.warehouse_id.id,
                'default_material_id': self.material_id.id,
                'default_project_id': self.project_id.id,
            }
        }

    def action_consume_material(self):
        """Consume material from this stock"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Consume {self.material_id.name}',
            'res_model': 'construction.material.consumption',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_warehouse_id': self.warehouse_id.id,
                'default_material_id': self.material_id.id,
                'default_project_id': self.project_id.id,
                'default_available_quantity': self.available_quantity,
            }
        }

    def action_view_movements(self):
        """View all stock movements for this material"""
        receipt_action = {
            'type': 'ir.actions.act_window',
            'name': f'Stock Movements - {self.material_id.name}',
            'res_model': 'construction.material.receipt',
            'view_mode': 'tree,form',
            'domain': [
                ('warehouse_id', '=', self.warehouse_id.id),
                ('material_id', '=', self.material_id.id)
            ],
        }
        return receipt_action

    @api.model
    def update_stock_from_receipt(self, warehouse_id, material_id, quantity):
        """Update stock levels when material is received"""
        stock = self.search([
            ('warehouse_id', '=', warehouse_id),
            ('material_id', '=', material_id)
        ], limit=1)

        if stock:
            stock.quantity += quantity
        else:
            # Create new stock record
            self.create({
                'warehouse_id': warehouse_id,
                'material_id': material_id,
                'quantity': quantity,
            })

    @api.model
    def update_stock_from_consumption(self, warehouse_id, material_id, quantity):
        """Update stock levels when material is consumed"""
        stock = self.search([
            ('warehouse_id', '=', warehouse_id),
            ('material_id', '=', material_id)
        ], limit=1)

        if stock:
            stock.quantity -= quantity
            if stock.quantity < 0:
                stock.quantity = 0  # Prevent negative stock
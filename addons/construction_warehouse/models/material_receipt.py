# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaterialReceipt(models.Model):
    _name = 'construction.material.receipt'
    _description = 'Material Receipt - Supplier Delivery to Warehouse'
    _order = 'receipt_date desc, id desc'
    _rec_name = 'display_name'

    # Basic Information
    warehouse_id = fields.Many2one(
        'construction.project.warehouse',
        string='Warehouse',
        required=True,
        help='Warehouse receiving the material'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        related='warehouse_id.project_id',
        store=True,
        help='Project this delivery is for'
    )
    material_id = fields.Many2one(
        'construction.material',
        string='Material',
        required=True,
        help='Material being delivered'
    )

    # Delivery Details
    receipt_date = fields.Datetime(
        string='Receipt Date',
        required=True,
        default=fields.Datetime.now,
        help='Date and time material was received'
    )
    delivery_reference = fields.Char(
        string='Delivery Reference',
        help='Delivery note or reference number'
    )

    # Quantities
    quantity = fields.Float(
        string='Received Quantity',
        required=True,
        help='Quantity of material received'
    )
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

    # Supplier Information
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        required=True,
        domain=[('is_company', '=', True)],
        help='Supplier who delivered the material'
    )
    supplier_contact = fields.Char(
        string='Supplier Contact',
        help='Contact person or phone number'
    )
    delivery_truck = fields.Char(
        string='Delivery Truck',
        help='Truck license plate or driver info'
    )

    # Costing
    unit_cost = fields.Float(
        string='Unit Cost',
        required=True,
        help='Cost per unit from supplier'
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True,
        help='Total cost of this delivery'
    )
    purchase_order_ref = fields.Char(
        string='Purchase Order',
        help='Related purchase order reference'
    )

    # Quality and Condition
    quality_check = fields.Selection([
        ('passed', 'Quality Check Passed'),
        ('failed', 'Quality Check Failed'),
        ('partial', 'Partial Acceptance'),
        ('pending', 'Quality Check Pending'),
    ], string='Quality Status', default='pending')

    condition_notes = fields.Text(
        string='Condition Notes',
        help='Notes about material condition upon receipt'
    )
    damaged_quantity = fields.Float(
        string='Damaged Quantity',
        help='Quantity that was damaged upon receipt'
    )

    # Receipt Process
    received_by_id = fields.Many2one(
        'res.users',
        string='Received By',
        required=True,
        default=lambda self: self.env.user,
        help='Person who received the delivery'
    )
    receipt_status = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('quality_check', 'Quality Check'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', required=True)

    # Storage
    storage_location = fields.Char(
        string='Storage Location',
        help='Where material was stored in warehouse'
    )
    storage_notes = fields.Text(
        string='Storage Notes',
        help='Special storage instructions or notes'
    )

    # Documentation
    delivery_photos = fields.Many2many(
        'ir.attachment',
        string='Delivery Photos',
        help='Photos of delivered materials'
    )
    receipt_notes = fields.Text(
        string='Receipt Notes',
        help='Additional notes about the receipt'
    )

    # Display Name
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('quantity', 'unit_cost')
    def _compute_total_cost(self):
        for receipt in self:
            receipt.total_cost = receipt.quantity * receipt.unit_cost

    @api.depends('material_id', 'quantity', 'supplier_id', 'receipt_date')
    def _compute_display_name(self):
        for receipt in self:
            material_name = receipt.material_id.name if receipt.material_id else 'No Material'
            supplier_name = receipt.supplier_id.name if receipt.supplier_id else 'No Supplier'
            date_str = receipt.receipt_date.strftime('%Y-%m-%d') if receipt.receipt_date else ''
            receipt.display_name = f"{material_name} ({receipt.quantity}) from {supplier_name} - {date_str}"

    @api.constrains('quantity', 'damaged_quantity')
    def _check_quantities(self):
        for receipt in self:
            if receipt.quantity <= 0:
                raise ValidationError("Received quantity must be greater than zero.")
            if receipt.damaged_quantity < 0:
                raise ValidationError("Damaged quantity cannot be negative.")
            if receipt.damaged_quantity > receipt.quantity:
                raise ValidationError("Damaged quantity cannot exceed received quantity.")

    def action_mark_received(self):
        """Mark receipt as received and update warehouse stock"""
        for receipt in self:
            if receipt.receipt_status == 'draft':
                receipt.receipt_status = 'received'

                # Update warehouse stock
                acceptable_quantity = receipt.quantity - receipt.damaged_quantity
                if acceptable_quantity > 0:
                    self.env['construction.warehouse.stock'].update_stock_from_receipt(
                        receipt.warehouse_id.id,
                        receipt.material_id.id,
                        acceptable_quantity
                    )

    def action_quality_check(self):
        """Perform quality check"""
        self.receipt_status = 'quality_check'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quality Check',
            'res_model': 'construction.material.receipt',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_accept_material(self):
        """Accept material after quality check"""
        for receipt in self:
            receipt.receipt_status = 'accepted'
            receipt.quality_check = 'passed'

    def action_reject_material(self):
        """Reject material - reverse stock update"""
        for receipt in self:
            receipt.receipt_status = 'rejected'
            receipt.quality_check = 'failed'

            # Reverse stock update
            acceptable_quantity = receipt.quantity - receipt.damaged_quantity
            if acceptable_quantity > 0:
                self.env['construction.warehouse.stock'].update_stock_from_consumption(
                    receipt.warehouse_id.id,
                    receipt.material_id.id,
                    acceptable_quantity
                )

    def action_upload_photos(self):
        """Upload delivery photos"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload Delivery Photos',
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': 'construction.material.receipt',
                'default_res_id': self.id,
                'default_name': f'Delivery Photo - {self.display_name}',
            }
        }

    @api.model
    def create_supplier_receipt(self, warehouse_id, material_id, quantity, unit_cost, supplier_id):
        """Helper method for suppliers to create receipts via portal"""
        return self.create({
            'warehouse_id': warehouse_id,
            'material_id': material_id,
            'quantity': quantity,
            'unit_cost': unit_cost,
            'supplier_id': supplier_id,
            'receipt_status': 'draft',
        })

    def action_create_from_po(self):
        """Create receipt from purchase order (future integration)"""
        # Placeholder for purchase order integration
        pass
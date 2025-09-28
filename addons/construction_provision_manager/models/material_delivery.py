# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class MaterialDelivery(models.Model):
    _name = 'construction.material.delivery'
    _description = 'Material Delivery to Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'delivery_date desc, id desc'
    _rec_name = 'display_name'

    # Basic Information
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        help='Project where material is delivered'
    )
    material_name = fields.Char(
        string='Material Name',
        required=True,
        help='Name of the delivered material'
    )
    category_id = fields.Many2one(
        'construction.material.category',
        string='Category',
        required=True,
        help='Material category'
    )

    # Quantity and Pricing
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
        help='Quantity delivered'
    )
    unit = fields.Selection([
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
    ], string='Unit', required=True, default='pcs')

    unit_price = fields.Float(
        string='Unit Price',
        required=True,
        help='Price per unit'
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True,
        help='Total cost of delivery'
    )

    # Supplier Information
    supplier_name = fields.Char(
        string='Supplier',
        help='Name of the supplier'
    )
    supplier_contact = fields.Char(
        string='Supplier Contact',
        help='Contact information of supplier'
    )
    purchase_order_ref = fields.Char(
        string='PO Reference',
        help='Purchase order reference number'
    )

    # Delivery Information
    delivery_date = fields.Datetime(
        string='Delivery Date',
        default=fields.Datetime.now,
        required=True,
        help='Date and time of delivery'
    )
    received_by = fields.Many2one(
        'res.users',
        string='Received By',
        default=lambda self: self.env.user,
        required=True,
        help='Person who received the delivery'
    )
    delivery_notes = fields.Text(
        string='Delivery Notes',
        help='Additional notes about the delivery'
    )

    # Status and Tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('delivered', 'Delivered'),
        ('consumed', 'Consumed'),
        ('returned', 'Returned'),
    ], string='Status', default='draft', required=True, tracking=True)

    # Usage Tracking
    consumed_quantity = fields.Float(
        string='Consumed Quantity',
        default=0.0,
        tracking=True,
        help='Quantity already consumed/used'
    )
    remaining_quantity = fields.Float(
        string='Remaining Quantity',
        compute='_compute_remaining_quantity',
        store=True,
        help='Quantity still available'
    )

    # Display name
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('quantity', 'unit_price')
    def _compute_total_cost(self):
        for delivery in self:
            delivery.total_cost = delivery.quantity * delivery.unit_price

    @api.depends('quantity', 'consumed_quantity')
    def _compute_remaining_quantity(self):
        for delivery in self:
            delivery.remaining_quantity = delivery.quantity - delivery.consumed_quantity

    @api.depends('material_name', 'quantity', 'unit', 'project_id')
    def _compute_display_name(self):
        for delivery in self:
            project_name = delivery.project_id.name if delivery.project_id else 'No Project'
            delivery.display_name = f"{delivery.material_name} ({delivery.quantity} {delivery.unit}) - {project_name}"

    def action_mark_delivered(self):
        """Mark delivery as completed"""
        self.state = 'delivered'

    def action_consume_material(self):
        """Open wizard to consume material"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Consume Material',
            'res_model': 'construction.material.consumption.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_delivery_id': self.id,
                'default_available_quantity': self.remaining_quantity,
            }
        }

    def create_expense_entry(self):
        """Create expense entry for this material delivery"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Expense',
            'res_model': 'hr.expense',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': f"Material: {self.material_name}",
                'default_total_amount': self.total_cost,
                'default_construction_project_id': self.project_id.id,
                'default_description': f"Delivery of {self.quantity} {self.unit} {self.material_name}",
            }
        }
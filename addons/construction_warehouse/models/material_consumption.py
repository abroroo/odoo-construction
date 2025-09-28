# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaterialConsumption(models.Model):
    _name = 'construction.material.consumption'
    _description = 'Material Consumption - Site Manager Takes Materials from Warehouse'
    _order = 'consumption_date desc, id desc'
    _rec_name = 'display_name'

    # Basic Information
    warehouse_id = fields.Many2one(
        'construction.project.warehouse',
        string='Warehouse',
        required=True,
        help='Warehouse where material is taken from'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        related='warehouse_id.project_id',
        store=True,
        help='Project this consumption is for'
    )
    material_id = fields.Many2one(
        'construction.material',
        string='Material',
        required=True,
        help='Material being consumed'
    )

    # Consumption Details
    consumption_date = fields.Datetime(
        string='Consumption Date',
        required=True,
        default=fields.Datetime.now,
        help='Date and time material was taken'
    )
    quantity = fields.Float(
        string='Consumed Quantity',
        required=True,
        help='Quantity of material consumed'
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

    # Available Stock Information
    available_quantity = fields.Float(
        string='Available in Warehouse',
        compute='_compute_available_quantity',
        help='Quantity available for consumption'
    )

    # Usage Information
    consumed_by_id = fields.Many2one(
        'res.users',
        string='Consumed By',
        required=True,
        default=lambda self: self.env.user,
        help='Site manager who took the material'
    )
    task_id = fields.Many2one(
        'project.task',
        string='Used for Task',
        required=True,
        domain="[('project_id', '=', project_id)]",
        help='Required: Specific смета task this material is used for'
    )
    work_location = fields.Char(
        string='Work Location',
        help='Specific location where material will be used (e.g., Foundation Block A)'
    )

    # Purpose and Tracking
    consumption_purpose = fields.Selection([
        ('direct_use', 'Direct Construction Use'),
        ('testing', 'Quality Testing'),
        ('waste', 'Waste/Damage'),
        ('transfer', 'Transfer to Another Location'),
        ('return', 'Return to Supplier'),
        ('other', 'Other'),
    ], string='Purpose', required=True, default='direct_use')

    consumption_notes = fields.Text(
        string='Consumption Notes',
        help='Notes about how material will be used'
    )

    # Status and Validation
    consumption_status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)

    # Documentation
    usage_photos = fields.Many2many(
        'ir.attachment',
        string='Usage Photos',
        help='Photos showing material usage'
    )

    # Costing (from warehouse stock)
    unit_cost = fields.Float(
        string='Unit Cost',
        compute='_compute_cost_info',
        store=True,
        help='Unit cost from warehouse stock'
    )
    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_cost_info',
        store=True,
        help='Total cost of consumed material'
    )

    # Display Name
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    @api.depends('warehouse_id', 'material_id')
    def _compute_available_quantity(self):
        for consumption in self:
            if consumption.warehouse_id and consumption.material_id:
                stock = self.env['construction.warehouse.stock'].search([
                    ('warehouse_id', '=', consumption.warehouse_id.id),
                    ('material_id', '=', consumption.material_id.id)
                ], limit=1)
                consumption.available_quantity = stock.available_quantity if stock else 0
            else:
                consumption.available_quantity = 0

    @api.depends('warehouse_id', 'material_id', 'quantity')
    def _compute_cost_info(self):
        for consumption in self:
            if consumption.warehouse_id and consumption.material_id:
                stock = self.env['construction.warehouse.stock'].search([
                    ('warehouse_id', '=', consumption.warehouse_id.id),
                    ('material_id', '=', consumption.material_id.id)
                ], limit=1)
                if stock:
                    consumption.unit_cost = stock.unit_cost
                    consumption.total_cost = consumption.quantity * consumption.unit_cost
                else:
                    consumption.unit_cost = 0
                    consumption.total_cost = 0
            else:
                consumption.unit_cost = 0
                consumption.total_cost = 0

    @api.depends('material_id', 'quantity', 'consumed_by_id', 'consumption_date')
    def _compute_display_name(self):
        for consumption in self:
            material_name = consumption.material_id.name if consumption.material_id else 'No Material'
            user_name = consumption.consumed_by_id.name if consumption.consumed_by_id else 'Unknown User'
            date_str = consumption.consumption_date.strftime('%Y-%m-%d') if consumption.consumption_date else ''
            consumption.display_name = f"{material_name} ({consumption.quantity}) used by {user_name} - {date_str}"

    @api.constrains('quantity', 'available_quantity')
    def _check_consumption_quantity(self):
        for consumption in self:
            if consumption.quantity <= 0:
                raise ValidationError("Consumption quantity must be greater than zero.")

            # Check if enough stock available (only for confirmed consumptions)
            if consumption.consumption_status in ['confirmed', 'completed']:
                available = consumption.available_quantity
                if consumption.quantity > available:
                    raise ValidationError(
                        f"Cannot consume {consumption.quantity} units. "
                        f"Only {available} units available in warehouse."
                    )

    @api.constrains('task_id')
    def _check_task_required(self):
        """Russian Spec: Every material consumption must be tied to a смета task"""
        for consumption in self:
            if not consumption.task_id:
                raise ValidationError(
                    "Russian Spec Compliance: Material consumption MUST be assigned to a specific смета task. "
                    "Select a task from the dropdown or create a new task if work was not in original смета."
                )

    @api.constrains('task_id', 'total_cost', 'material_id')
    def _check_task_budget_allocation(self):
        """Warn if consumption exceeds task budget allocation"""
        for consumption in self:
            if consumption.task_id and consumption.total_cost > 0:
                # Check if task has budget allocation
                task = consumption.task_id
                if hasattr(task, 'budget_allocation') and task.budget_allocation:
                    # Calculate total consumed for this task
                    total_consumed = self.search([
                        ('task_id', '=', task.id),
                        ('consumption_status', 'in', ['confirmed', 'completed']),
                        ('id', '!=', consumption.id)  # Exclude current record
                    ])
                    total_spent = sum(total_consumed.mapped('total_cost')) + consumption.total_cost

                    if total_spent > task.budget_allocation * 1.1:  # 10% tolerance
                        raise ValidationError(
                            f"Budget Warning: Material consumption ({total_spent:.2f}) exceeds "
                            f"task budget allocation ({task.budget_allocation:.2f}) by more than 10%. "
                            f"Task: {task.name}"
                        )

    @api.onchange('warehouse_id', 'material_id')
    def _onchange_warehouse_material(self):
        """Update available quantity when warehouse or material changes"""
        if self.warehouse_id and self.material_id:
            stock = self.env['construction.warehouse.stock'].search([
                ('warehouse_id', '=', self.warehouse_id.id),
                ('material_id', '=', self.material_id.id)
            ], limit=1)
            if stock:
                self.available_quantity = stock.available_quantity
            else:
                self.available_quantity = 0

    @api.onchange('task_id')
    def _onchange_task_selection(self):
        """Russian Spec: When task is selected, filter available materials for that task"""
        if self.task_id:
            # Reset material selection to force user to choose based on task
            self.material_id = False
            self.available_quantity = 0

            # Get task type to potentially filter materials
            task = self.task_id
            task_info = f"Task selected: {task.name}"
            if hasattr(task, 'smeta_number') and task.smeta_number:
                task_info += f" (смета #{task.smeta_number})"
            elif 'смета' in task.name.lower():
                task_info += " (смета задача)"

            # You could add material filtering logic here based on task type
            # For now, just clear material selection to enforce task-first workflow
            return {
                'domain': {
                    'material_id': [('active', '=', True)]  # Show all materials for now
                }
            }

    def action_confirm_consumption(self):
        """Confirm consumption and update warehouse stock"""
        for consumption in self:
            if consumption.consumption_status == 'draft':
                # Check stock availability
                if consumption.quantity > consumption.available_quantity:
                    raise ValidationError(
                        f"Cannot consume {consumption.quantity} units. "
                        f"Only {consumption.available_quantity} units available."
                    )

                consumption.consumption_status = 'confirmed'

                # Update warehouse stock
                self.env['construction.warehouse.stock'].update_stock_from_consumption(
                    consumption.warehouse_id.id,
                    consumption.material_id.id,
                    consumption.quantity
                )

                # Russian Spec: Log task-centric consumption
                consumption._log_russian_consumption_message()

    def action_complete_consumption(self):
        """Mark consumption as completed"""
        self.consumption_status = 'completed'

    def action_cancel_consumption(self):
        """Cancel consumption and restore stock if it was confirmed"""
        for consumption in self:
            if consumption.consumption_status == 'confirmed':
                # Restore stock
                self.env['construction.warehouse.stock'].update_stock_from_receipt(
                    consumption.warehouse_id.id,
                    consumption.material_id.id,
                    consumption.quantity
                )

            consumption.consumption_status = 'cancelled'

    def action_upload_photos(self):
        """Upload usage photos"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload Usage Photos',
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': 'construction.material.consumption',
                'default_res_id': self.id,
                'default_name': f'Usage Photo - {self.display_name}',
            }
        }

    def action_quick_consume(self):
        """Quick consumption for site managers"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quick Consume Material',
            'res_model': 'construction.material.consumption',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_warehouse_id': self.warehouse_id.id,
                'default_material_id': self.material_id.id,
                'default_project_id': self.project_id.id,
            }
        }

    @api.model
    def get_available_materials(self, warehouse_id):
        """Get all materials available for consumption in a warehouse"""
        stocks = self.env['construction.warehouse.stock'].search([
            ('warehouse_id', '=', warehouse_id),
            ('available_quantity', '>', 0)
        ])

        materials = []
        for stock in stocks:
            materials.append({
                'material_id': stock.material_id.id,
                'material_name': stock.material_id.name,
                'available_quantity': stock.available_quantity,
                'unit_of_measure': stock.unit_of_measure,
                'storage_location': stock.storage_location,
            })

        return materials

    @api.model
    def site_manager_consume_material(self, warehouse_id, material_id, quantity, task_id=None, notes=None):
        """Helper method for site managers to quickly consume materials"""
        consumption = self.create({
            'warehouse_id': warehouse_id,
            'material_id': material_id,
            'quantity': quantity,
            'task_id': task_id,
            'consumption_notes': notes,
            'consumption_status': 'draft',
        })

        # Auto-confirm if stock is available
        if consumption.quantity <= consumption.available_quantity:
            consumption.action_confirm_consumption()

        return consumption

    def _log_russian_consumption_message(self):
        """Log consumption in Russian specification format"""
        if self.task_id and self.material_id and self.consumed_by_id:
            # Russian format: "Прораб [Name] списал [Quantity] [Material] на задачу [Task]"
            user_name = self.consumed_by_id.name
            material_name = self.material_id.name
            quantity_unit = f"{self.quantity} {self.unit_of_measure}"
            task_name = self.task_id.name

            smeta_info = ""
            # Check if task has smeta information (might be in description or name)
            task = self.task_id
            if hasattr(task, 'smeta_number') and task.smeta_number:
                smeta_info = f" (смета #{task.smeta_number})"
            elif 'смета' in task.name.lower() or 'smeta' in task.name.lower():
                smeta_info = " (смета задача)"

            message = f"Прораб {user_name} списал {quantity_unit} {material_name} на задачу «{task_name}»{smeta_info}"

            # Log to consumption record
            self.message_post(body=message)

            # Also log to project (for centralized tracking)
            if self.project_id:
                self.project_id.message_post(
                    body=f"Материал списан: {message}",
                    subtype_xmlid='mail.mt_note'
                )

    def action_create_new_task(self):
        """Quick action to create new task for material consumption"""
        if not self.project_id:
            raise ValidationError("Project must be selected to create a new task.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create New Task',
            'res_model': 'construction.quick.task.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.project_id.id,
                'consumption_id': self.id,
                'material_name': self.material_id.name if self.material_id else '',
            }
        }
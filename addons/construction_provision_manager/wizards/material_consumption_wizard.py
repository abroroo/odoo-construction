# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaterialConsumptionWizard(models.TransientModel):
    _name = 'construction.material.consumption.wizard'
    _description = 'Material Consumption Wizard'

    delivery_id = fields.Many2one(
        'construction.material.delivery',
        string='Material Delivery',
        required=True
    )
    available_quantity = fields.Float(
        string='Available Quantity',
        readonly=True
    )
    consume_quantity = fields.Float(
        string='Quantity to Consume',
        required=True,
        default=1.0
    )
    consumption_date = fields.Datetime(
        string='Consumption Date',
        default=fields.Datetime.now,
        required=True
    )
    notes = fields.Text(
        string='Consumption Notes',
        help='Notes about where/how the material was used'
    )
    project_task_id = fields.Many2one(
        'project.task',
        string='Related Task',
        help='Task where this material was consumed'
    )

    @api.onchange('delivery_id')
    def _onchange_delivery_id(self):
        if self.delivery_id:
            self.available_quantity = self.delivery_id.remaining_quantity

    @api.constrains('consume_quantity', 'available_quantity')
    def _check_consume_quantity(self):
        for wizard in self:
            if wizard.consume_quantity <= 0:
                raise ValidationError("Consumption quantity must be greater than zero.")
            if wizard.consume_quantity > wizard.available_quantity:
                raise ValidationError(
                    f"Cannot consume {wizard.consume_quantity} units. "
                    f"Only {wizard.available_quantity} units available."
                )

    def action_consume_material(self):
        """Record material consumption"""
        for wizard in self:
            # Update delivery consumed quantity
            wizard.delivery_id.consumed_quantity += wizard.consume_quantity

            # Update delivery state if fully consumed
            if wizard.delivery_id.remaining_quantity <= 0:
                wizard.delivery_id.state = 'consumed'

            # Create consumption record (could be expanded to separate model)
            consumption_data = {
                'delivery_id': wizard.delivery_id.id,
                'consumed_quantity': wizard.consume_quantity,
                'consumption_date': wizard.consumption_date,
                'notes': wizard.notes,
                'task_id': wizard.project_task_id.id if wizard.project_task_id else False,
            }

            # For now, we'll add to delivery notes
            current_notes = wizard.delivery_id.delivery_notes or ""
            consumption_note = f"\n[{wizard.consumption_date.strftime('%Y-%m-%d %H:%M')}] " \
                             f"Consumed: {wizard.consume_quantity} units"
            if wizard.notes:
                consumption_note += f" - {wizard.notes}"
            if wizard.project_task_id:
                consumption_note += f" (Task: {wizard.project_task_id.name})"

            wizard.delivery_id.delivery_notes = current_notes + consumption_note

            # Trigger project material inventory update
            self.env['construction.project.material'].update_project_materials()

        return {'type': 'ir.actions.act_window_close'}
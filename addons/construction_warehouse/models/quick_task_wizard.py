# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class QuickTaskWizard(models.TransientModel):
    _name = 'construction.quick.task.wizard'
    _description = 'Quick Task Creation Wizard for Foreman'

    # Required fields
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        help='Project for the new task'
    )
    name = fields.Char(
        string='Task Name',
        required=True,
        help='Name of the new task'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of the work'
    )
    estimated_quantity = fields.Float(
        string='Estimated Quantity',
        default=1.0,
        help='Estimated quantity of work'
    )

    # Context fields (populated from material consumption)
    consumption_id = fields.Integer(
        string='Consumption ID',
        help='ID of the consumption record that triggered this wizard'
    )
    material_name = fields.Char(
        string='Material Name',
        help='Name of material being consumed'
    )

    @api.model
    def default_get(self, fields_list):
        """Pre-populate fields from context"""
        res = super().default_get(fields_list)

        # Get context values
        consumption_id = self.env.context.get('consumption_id')
        material_name = self.env.context.get('material_name', '')

        if consumption_id:
            res['consumption_id'] = consumption_id

        if material_name:
            res['material_name'] = material_name
            # Pre-fill task name with material reference
            res['name'] = f"Additional work with {material_name}"
            res['description'] = f"Additional construction work requiring {material_name}. " \
                               f"This task was created to track work not included in the original смета."

        return res

    def action_create_task(self):
        """Create the additional task and return to material consumption"""
        if not self.project_id:
            raise ValidationError("Project is required to create a task.")

        if not self.name:
            raise ValidationError("Task name is required.")

        # Create the additional task using the smeta integration module
        try:
            task = self.env['project.task'].create_additional_task(
                project_id=self.project_id.id,
                name=self.name,
                description=self.description,
                estimated_quantity=self.estimated_quantity
            )
        except Exception as e:
            raise ValidationError(f"Failed to create task: {str(e)}")

        # If this was triggered from material consumption, update the consumption record
        if self.consumption_id:
            consumption = self.env['construction.material.consumption'].browse(self.consumption_id)
            if consumption.exists():
                consumption.write({'task_id': task.id})

                # Log the task creation
                consumption.message_post(
                    body=f"Created new additional task: <a href='#' data-oe-model='project.task' data-oe-id='{task.id}'>{task.name}</a>",
                    subtype_xmlid='mail.mt_note'
                )

        # Return action to close wizard and show the new task
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Task Created',
            'res_model': 'project.task',
            'res_id': task.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel(self):
        """Cancel task creation and return to consumption"""
        return {'type': 'ir.actions.act_window_close'}
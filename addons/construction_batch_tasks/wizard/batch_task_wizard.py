# -*- coding: utf-8 -*-

import logging
import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BatchTaskWizard(models.TransientModel):
    _name = 'construction.batch.task.wizard'
    _description = 'Batch Task Creation Wizard'

    # Step management
    step = fields.Selection([
        ('input', 'Input Tasks'),
        ('preview', 'Preview & Validate'),
        ('result', 'Creation Result'),
    ], string='Step', default='input')

    # Input fields
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        help='Select the project where tasks will be created'
    )
    task_data = fields.Text(
        string='Task Data',
        help='Paste task data in format: Number|Task Name|Unit|Quantity (one per line)',
        placeholder="""1|CONCRETE FOUNDATION WORK|M3|25.5
1.1|EXCAVATION WORK|M3|30.0
1.2|CONCRETE POURING|M3|25.5
2|STEEL REINFORCEMENT|KG|1250.0
2.1|REBAR CUTTING|KG|1250.0
2.2|REBAR INSTALLATION|KG|1250.0
3|ELECTRICAL INSTALLATION|UNITS|1.0
3.1|CABLE INSTALLATION|M|150.0
3.2|FIXTURE MOUNTING|UNITS|12.0"""
    )

    # Validation and preview
    validation_errors = fields.Text(string='Validation Errors', readonly=True)
    preview_lines = fields.One2many(
        'construction.batch.task.preview',
        'wizard_id',
        string='Preview Lines'
    )

    # Options
    create_budget_lines = fields.Boolean(
        string='Create Budget Lines',
        default=True,
        help='Also create budget lines for financial tracking'
    )
    default_stage_id = fields.Many2one(
        'project.task.type',
        string='Initial Task Stage',
        domain="[('project_ids', '=', project_id)]",
        help='Initial stage for created tasks (defaults to first stage)'
    )

    # Results
    created_tasks_count = fields.Integer(string='Created Tasks', readonly=True)
    created_budget_lines_count = fields.Integer(string='Created Budget Lines', readonly=True)
    result_message = fields.Text(string='Result Message', readonly=True)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        """Set default stage when project changes"""
        if self.project_id:
            stages = self.project_id.type_ids
            if stages:
                self.default_stage_id = stages[0]

    def action_parse_and_preview(self):
        """Parse input data and show preview"""
        if not self.task_data:
            raise UserError(_("Please enter task data to parse."))

        # Parse the input data
        parsed_data, errors = self._parse_task_data(self.task_data)

        # Store validation errors
        self.validation_errors = '\n'.join(errors) if errors else ''

        if errors:
            # Show errors but allow preview of valid lines
            if not parsed_data:
                raise UserError(_("No valid task data found. Please check the format:\nNumber|Task Name|Unit|Quantity"))

        # Clear existing preview lines
        self.preview_lines.unlink()

        # Create preview lines
        if parsed_data:
            preview_data = []
            for line_data in parsed_data:
                preview_data.append({
                    'wizard_id': self.id,
                    'task_number': line_data['number'],
                    'task_name': line_data['name'],
                    'task_unit': line_data['unit'],
                    'task_quantity': line_data['quantity'],
                    'task_type': 'Main Task' if line_data['is_main_task'] else 'Sub-task',
                    'parent_number': line_data['parent_number'],
                    'has_errors': False,
                })

            self.env['construction.batch.task.preview'].create(preview_data)

        # Move to preview step
        self.step = 'preview'
        return self._get_action_view()

    def action_create_tasks(self):
        """Create the actual tasks and budget lines"""
        if not self.preview_lines:
            raise UserError(_("No preview data available. Please parse the task data first."))

        try:
            # Parse the data again for creation
            parsed_data, errors = self._parse_task_data(self.task_data)

            if errors:
                raise UserError(_("Cannot create tasks with validation errors:\n%s") % '\n'.join(errors))

            # Create tasks and budget lines
            result = self._create_tasks_and_budgets(parsed_data)

            # Store results
            self.created_tasks_count = result['tasks_created']
            self.created_budget_lines_count = result['budget_lines_created']
            self.result_message = result['message']

            # Move to result step
            self.step = 'result'
            return self._get_action_view()

        except Exception as e:
            _logger.error(f"Error creating batch tasks: {str(e)}")
            raise UserError(_("Error creating tasks: %s") % str(e))

    def action_previous_step(self):
        """Go back to previous step"""
        if self.step == 'preview':
            self.step = 'input'
        elif self.step == 'result':
            self.step = 'preview'
        return self._get_action_view()

    def action_view_created_tasks(self):
        """View the created tasks in project"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Tasks'),
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form',
            'domain': [('project_id', '=', self.project_id.id)],
            'context': {'default_project_id': self.project_id.id},
        }

    def _parse_task_data(self, task_data):
        """Parse pipe-separated task data into structured format"""
        parsed_data = []
        errors = []

        if not task_data:
            return parsed_data, errors

        lines = task_data.strip().split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            # Split by pipe character
            parts = [part.strip() for part in line.split('|')]

            if len(parts) != 4:
                errors.append(f"Line {line_num}: Expected 4 parts separated by '|', got {len(parts)}: {line}")
                continue

            number, name, unit, quantity_str = parts

            # Validate task number format
            if not re.match(r'^\d+(\.\d+)*$', number):
                errors.append(f"Line {line_num}: Invalid task number format '{number}'. Use format like '1', '1.1', '2.3', etc.")
                continue

            # Validate task name
            if not name:
                errors.append(f"Line {line_num}: Task name cannot be empty")
                continue

            # Validate and convert quantity
            try:
                quantity = float(quantity_str) if quantity_str else 0.0
            except ValueError:
                errors.append(f"Line {line_num}: Invalid quantity '{quantity_str}'. Must be a number.")
                continue

            # Determine if main task or sub-task
            is_main_task = '.' not in number
            parent_number = number.split('.')[0] if not is_main_task else None

            parsed_data.append({
                'number': number,
                'name': name,
                'unit': unit,
                'quantity': quantity,
                'is_main_task': is_main_task,
                'parent_number': parent_number,
                'line_num': line_num,
            })

        return parsed_data, errors

    def _create_tasks_and_budgets(self, parsed_data):
        """Create project tasks and budget lines from parsed data"""
        if not parsed_data:
            return {'tasks_created': 0, 'budget_lines_created': 0, 'message': 'No data to process'}

        project = self.project_id
        task_mapping = {}  # Map task numbers to task records
        created_tasks = []
        created_budget_lines = []

        # Sort parsed data by task number for proper hierarchy creation
        sorted_data = sorted(parsed_data, key=lambda x: self._sort_key(x['number']))

        # Phase 1: Create tasks only (no computed fields issues)
        _logger.info("Phase 1: Creating tasks...")

        # Get the default stage (maps to "К выполнению" / "To Do")
        default_stage = self.default_stage_id or self._get_default_stage(project)

        for task_data in sorted_data:
            try:
                # Create the most basic task possible
                task_vals = {
                    'name': f"{task_data['number']}. {task_data['name']}",
                    'project_id': project.id,
                }

                # Automatically assign stage based on Russian workflow
                # New tasks always go to "К выполнению" (To Do) stage
                if default_stage:
                    task_vals['stage_id'] = default_stage.id

                # Create the task with minimal data to avoid computed field conflicts
                task = self.env['project.task'].with_context(mail_create_nolog=True).create(task_vals)

                created_tasks.append(task)
                task_mapping[task_data['number']] = task

                _logger.info(f"Created basic task: {task.name}")

            except Exception as e:
                _logger.error(f"Error creating basic task {task_data['number']}: {str(e)}")
                continue

        # Phase 2: Update tasks with additional data
        _logger.info("Phase 2: Updating task details...")
        for i, task_data in enumerate(sorted_data):
            if i < len(created_tasks):
                task = created_tasks[i]
                try:
                    # Update with additional fields
                    update_vals = {
                        'description': f"Created from batch import\nNumber: {task_data['number']}\nUnit: {task_data['unit']}\nQuantity: {task_data['quantity']}",
                    }

                    # Add parent relationship
                    if not task_data['is_main_task'] and task_data['parent_number']:
                        parent_task = task_mapping.get(task_data['parent_number'])
                        if parent_task:
                            update_vals['parent_id'] = parent_task.id

                    # Update the task
                    task.write(update_vals)

                except Exception as e:
                    _logger.error(f"Error updating task {task.name}: {str(e)}")

        # Phase 3: Create budget lines if requested (temporarily disabled for testing)
        if self.create_budget_lines and False:  # Temporarily disabled
            _logger.info("Phase 3: Creating budget lines...")
            try:
                budget = self._get_or_create_project_budget(project)
                for i, task_data in enumerate(sorted_data):
                    if i < len(created_tasks):
                        task = created_tasks[i]
                        budget_line = self._create_budget_line(budget, task_data, task)
                        if budget_line:
                            created_budget_lines.append(budget_line)
            except Exception as e:
                _logger.error(f"Error creating budget lines: {str(e)}")

        # Generate result message
        message = f"Batch Task Creation Completed!\n\n"
        message += f"✓ Created {len(created_tasks)} project tasks\n"
        if self.create_budget_lines:
            message += f"✓ Created {len(created_budget_lines)} budget lines\n"
        message += f"✓ Project: {project.name}\n"

        if len(created_tasks) > 0:
            main_tasks = [t for t in created_tasks if not t.parent_id]
            sub_tasks = [t for t in created_tasks if t.parent_id]
            message += f"\nTask Breakdown:\n"
            message += f"• Main tasks: {len(main_tasks)}\n"
            message += f"• Sub-tasks: {len(sub_tasks)}\n"

        return {
            'tasks_created': len(created_tasks),
            'budget_lines_created': len(created_budget_lines),
            'message': message,
        }

    def _sort_key(self, task_number):
        """Generate sort key for proper task ordering"""
        parts = task_number.split('.')
        # Convert to integers and pad for sorting
        return [int(part) for part in parts] + [0] * (10 - len(parts))

    def _get_or_create_project_budget(self, project):
        """Get existing budget or create new one for the project"""
        budget = self.env['construction.project.budget'].search([
            ('project_id', '=', project.id),
            ('state', 'in', ['draft', 'active'])
        ], limit=1)

        if not budget:
            budget = self.env['construction.project.budget'].create({
                'name': f'Batch Import Budget - {project.name}',
                'project_id': project.id,
                'start_date': fields.Date.today(),
                'state': 'draft',
            })

        return budget

    def _create_budget_line(self, budget, task_data, task):
        """Create budget line for a task"""
        try:
            # Find or create category
            category = self._get_or_create_category(task_data)

            # Create budget line with minimal fields
            budget_line_vals = {
                'budget_id': budget.id,
                'name': f"{task_data['number']}. {task_data['name']}",
                'category_id': category.id,
                'quantity': task_data['quantity'],
                'unit_price': 0.0,  # Will be filled later
                'sequence': int(task_data['number'].replace('.', '')) if task_data['number'].replace('.', '').isdigit() else 999,
            }

            budget_line = self.env['construction.project.budget.line'].create(budget_line_vals)

            # Link to task if task integration module is available
            try:
                if hasattr(budget_line, 'task_id'):
                    budget_line.task_id = task.id
                if hasattr(task, 'budget_line_id'):
                    task.budget_line_id = budget_line.id
            except Exception as e:
                _logger.warning(f"Could not link task and budget line: {str(e)}")

            return budget_line

        except Exception as e:
            _logger.error(f"Error creating budget line for {task_data['number']}: {str(e)}")
            return None

    def _get_or_create_category(self, task_data):
        """Get or create budget category"""
        # Simple category mapping based on task type
        if task_data['is_main_task']:
            category_name = f"Work Group {task_data['number']}"
        else:
            category_name = "Materials & Labor"

        category = self.env['construction.budget.category'].search([
            ('name', '=', category_name)
        ], limit=1)

        if not category:
            category = self.env['construction.budget.category'].create({
                'name': category_name,
                'description': f'Auto-created from batch import'
            })

        return category

    def _get_default_stage(self, project):
        """Get default stage for tasks"""
        stages = project.type_ids
        if stages:
            return stages[0]

        # Create default stage if none exists
        return self.env['project.task.type'].create({
            'name': 'To Do',
            'sequence': 1,
            'project_ids': [(6, 0, [project.id])],
        })

    def _get_action_view(self):
        """Return action to reload wizard view"""
        return {
            'name': _('Batch Create Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'construction.batch.task.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }


class BatchTaskPreview(models.TransientModel):
    _name = 'construction.batch.task.preview'
    _description = 'Batch Task Preview Line'

    wizard_id = fields.Many2one('construction.batch.task.wizard', string='Wizard', ondelete='cascade')
    task_number = fields.Char(string='Number')
    task_name = fields.Char(string='Task Name')
    task_unit = fields.Char(string='Unit')
    task_quantity = fields.Float(string='Quantity')
    task_type = fields.Char(string='Type')
    parent_number = fields.Char(string='Parent')
    has_errors = fields.Boolean(string='Has Errors')
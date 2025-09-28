# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SmetaImportProcessor(models.TransientModel):
    _inherit = 'construction.smeta.processor'

    def process_smeta_data(self, excel_data, column_mapping, project_id, budget_id=None):
        """Override to create both budget lines AND project tasks from Russian smeta"""

        # First, call the original method to create budget lines
        result = super().process_smeta_data(excel_data, column_mapping, project_id, budget_id)

        # Then create project tasks from the same data
        try:
            task_result = self._create_project_tasks_from_smeta(excel_data, project_id, result['budget_id'])

            # Update result with task information
            result.update({
                'created_tasks': task_result['created_tasks'],
                'task_count': task_result['task_count'],
                'main_task_count': task_result['main_task_count'],
                'sub_task_count': task_result['sub_task_count'],
            })

            # Update the result message
            original_message = result.get('import_result', '')
            task_message = f"\n\nProject Tasks Created:\n"
            task_message += f"• Main Tasks: {task_result['main_task_count']}\n"
            task_message += f"• Sub-Tasks: {task_result['sub_task_count']}\n"
            task_message += f"• Total Tasks: {task_result['task_count']}\n"
            task_message += f"• Task-Budget Links: {task_result['linked_count']}"

            # Add task management note
            task_message += f"\n\nNow available for project management:\n"
            task_message += f"• Assign tasks to team members\n"
            task_message += f"• Track work progress and completion\n"
            task_message += f"• Manage task dependencies and scheduling\n"
            task_message += f"• View in Kanban, List, and Gantt charts"

        except Exception as e:
            _logger.error(f"Error creating project tasks from smeta: {str(e)}")
            # Don't fail the entire import if task creation fails
            result.update({
                'task_creation_error': str(e),
                'created_tasks': [],
                'task_count': 0,
            })

        return result

    def _create_project_tasks_from_smeta(self, excel_data, project_id, budget_id):
        """Create hierarchical project tasks from parsed Russian smeta structure"""

        project = self.env['project.project'].browse(project_id)
        if not project.exists():
            raise UserError(_("Project does not exist."))

        # Parse the Russian smeta structure
        parsed_tasks = self._parse_russian_smeta_structure(excel_data)

        # Get budget lines to link with tasks
        budget_lines = self.env['construction.project.budget.line'].search([
            ('budget_id', '=', budget_id)
        ])

        created_tasks = []
        task_mapping = {}  # Map smeta numbers to task IDs for hierarchy
        main_task_count = 0
        sub_task_count = 0
        linked_count = 0

        # Phase 1: Create main tasks (1, 2, 3...)
        for task_data in parsed_tasks:
            if task_data['type'] == 'main_task':
                try:
                    task_name = task_data['name'][:100] if task_data['name'] else f"Task {task_data['number']}"

                    # Create main task
                    main_task = self.env['project.task'].create({
                        'name': f"{task_data['number']}. {task_name}",
                        'project_id': project_id,
                        'description': self._build_task_description(task_data),
                        'stage_id': self._get_todo_stage_id(project_id),
                        'sequence': self._get_sequence_from_number(task_data['number']),
                        'smeta_number': task_data['number'],
                        'smeta_section': task_data['section'],
                        'smeta_type': 'main_task',
                        'tag_ids': [(6, 0, [self._get_or_create_smeta_tag().id])],
                    })

                    created_tasks.append(main_task)
                    task_mapping[task_data['number']] = main_task.id
                    main_task_count += 1

                    _logger.info(f"Created main task: {main_task.name}")

                except Exception as e:
                    _logger.error(f"Error creating main task {task_data['number']}: {str(e)}")

        # Phase 2: Create sub-tasks (1.1, 1.2, 2.1...) and link to budget lines
        for task_data in parsed_tasks:
            if task_data['type'] == 'sub_task':
                try:
                    task_name = task_data['name'][:100] if task_data['name'] else f"Sub-task {task_data['number']}"

                    # Find parent task
                    parent_task_id = None
                    if task_data['parent_task'] and task_data['parent_task'] in task_mapping:
                        parent_task_id = task_mapping[task_data['parent_task']]

                    # Create sub-task with quantity information
                    sub_task = self.env['project.task'].create({
                        'name': f"{task_data['number']} - {task_name}",
                        'project_id': project_id,
                        'parent_id': parent_task_id,
                        'description': self._build_task_description(task_data),
                        'stage_id': self._get_todo_stage_id(project_id),
                        'sequence': self._get_sequence_from_number(task_data['number']),
                        'smeta_number': task_data['number'],
                        'smeta_section': task_data['section'],
                        'smeta_type': 'sub_task',
                        'planned_quantity': self._clean_numeric_value(task_data['total_quantity']),
                        'quantity_per_unit': self._clean_numeric_value(task_data['quantity_per_unit']),
                        'quantity_uom': task_data['unit'][:50] if task_data['unit'] else '',
                        'tag_ids': [(6, 0, [self._get_or_create_smeta_tag().id])],
                    })

                    # Link to corresponding budget line
                    budget_line = self._find_matching_budget_line(budget_lines, task_data)
                    if budget_line:
                        sub_task.write({'budget_line_id': budget_line.id})
                        budget_line.write({'task_id': sub_task.id})
                        linked_count += 1

                    created_tasks.append(sub_task)
                    task_mapping[task_data['number']] = sub_task.id
                    sub_task_count += 1

                    _logger.info(f"Created sub-task: {sub_task.name}")

                except Exception as e:
                    _logger.error(f"Error creating sub-task {task_data['number']}: {str(e)}")

        return {
            'created_tasks': created_tasks,
            'task_count': len(created_tasks),
            'main_task_count': main_task_count,
            'sub_task_count': sub_task_count,
            'linked_count': linked_count,
        }

    def _build_task_description(self, task_data):
        """Build detailed task description from smeta data"""
        description = f"<strong>Smeta Task {task_data['number']}</strong><br/><br/>"

        if task_data['section']:
            description += f"<strong>Section:</strong> {task_data['section']}<br/>"

        if task_data['justification']:
            description += f"<strong>Justification:</strong> {task_data['justification']}<br/>"

        if task_data['unit']:
            description += f"<strong>Unit:</strong> {task_data['unit']}<br/>"

        if task_data['total_quantity']:
            quantity = self._clean_numeric_value(task_data['total_quantity'])
            if quantity > 0:
                description += f"<strong>Planned Quantity:</strong> {quantity}<br/>"

        description += f"<br/><em>Imported from Russian construction smeta</em>"

        return description

    def _get_todo_stage_id(self, project_id):
        """Get or create 'To Do' stage for the project"""
        project = self.env['project.project'].browse(project_id)

        # Look for existing 'To Do' stage
        todo_stage = project.type_ids.filtered(lambda s: s.name.lower() in ['to do', 'todo', 'new', 'draft'])
        if todo_stage:
            return todo_stage[0].id

        # Look for first stage
        if project.type_ids:
            return project.type_ids[0].id

        # Create default 'To Do' stage
        stage = self.env['project.task.type'].create({
            'name': 'To Do',
            'sequence': 1,
            'project_ids': [(6, 0, [project_id])],
        })
        return stage.id

    def _get_sequence_from_number(self, smeta_number):
        """Convert smeta number to integer sequence for sorting"""
        try:
            # Convert "1.2" to 120, "2.1" to 210, etc.
            if '.' in str(smeta_number):
                parts = str(smeta_number).split('.')
                return int(parts[0]) * 100 + int(parts[1])
            else:
                return int(smeta_number) * 100
        except:
            return 999  # Default for non-numeric

    def _get_or_create_smeta_tag(self):
        """Get or create a tag for smeta-imported tasks"""
        tag = self.env['project.tags'].search([('name', '=', 'Smeta Import')], limit=1)
        if not tag:
            tag = self.env['project.tags'].create({
                'name': 'Smeta Import',
                'color': 5,  # Blue color - original smeta tasks
            })
        return tag

    def _get_or_create_additional_task_tag(self):
        """Get or create a tag for additional (non-smeta) tasks"""
        tag = self.env['project.tags'].search([('name', '=', 'Additional Task')], limit=1)
        if not tag:
            tag = self.env['project.tags'].create({
                'name': 'Additional Task',
                'color': 3,  # Orange color - additional tasks
            })
        return tag

    def _find_matching_budget_line(self, budget_lines, task_data):
        """Find the budget line that corresponds to this task"""
        # Look for budget line with matching smeta number in the name
        for line in budget_lines:
            if task_data['number'] in line.name:
                return line
        return None
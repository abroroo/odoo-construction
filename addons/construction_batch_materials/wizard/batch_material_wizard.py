# -*- coding: utf-8 -*-

import logging
import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BatchMaterialWizard(models.TransientModel):
    _name = 'construction.batch.material.wizard'
    _description = 'Batch Material Creation Wizard'

    # Step management
    step = fields.Selection([
        ('input', 'Input Materials'),
        ('preview', 'Preview & Validate'),
        ('result', 'Creation Result'),
    ], string='Step', default='input')

    # Input fields
    material_data = fields.Text(
        string='Material Data',
        help='Paste material data in format: Code|Name|Unit|Price (one per line)',
        placeholder="""00001|ЗАТРАТЫ ТРУДА РАБОЧИХ-СТРОИТЕЛЕЙ|ЧЕЛ-Ч|24855.64
06323|БЕТОН ТЯЖЕЛЫЙ М-200 ФРАКЦИИ 10-20ММ|М3|450000.00
09219|ВОДА|М3|400.00
26626|ГРУНТ|М3|0.00
30407|ГВОЗДИ СТРОИТЕЛЬНЫЕ|Т|8500000.00"""
    )

    # Validation and preview
    validation_errors = fields.Text(string='Validation Errors', readonly=True)
    preview_lines = fields.One2many(
        'construction.batch.material.preview',
        'wizard_id',
        string='Preview Lines'
    )

    # Options
    skip_duplicates = fields.Boolean(
        string='Skip Duplicates',
        default=True,
        help='Skip materials with codes that already exist'
    )

    # Results
    created_materials_count = fields.Integer(string='Created Materials', readonly=True)
    skipped_count = fields.Integer(string='Skipped Duplicates', readonly=True)
    result_message = fields.Text(string='Result Message', readonly=True)

    def action_parse_and_preview(self):
        """Parse input data and show preview"""
        if not self.material_data:
            raise UserError(_("Please enter material data to parse."))

        # Parse the input data
        parsed_data, errors = self._parse_material_data(self.material_data)

        # Store validation errors
        self.validation_errors = '\n'.join(errors) if errors else ''

        if errors:
            # Show errors but allow preview of valid lines
            if not parsed_data:
                raise UserError(_("No valid material data found. Please check the format:\nCode|Name|Unit|Price"))

        # Clear existing preview lines
        self.preview_lines.unlink()

        # Create preview lines
        if parsed_data:
            preview_data = []
            for line_data in parsed_data:
                # Check if material code already exists
                existing = self.env['construction.material'].search([
                    ('code', '=', line_data['code'])
                ], limit=1)

                preview_data.append({
                    'wizard_id': self.id,
                    'material_code': line_data['code'],
                    'material_name': line_data['name'],
                    'material_unit': line_data['unit'],
                    'material_price': line_data['price'],
                    'is_duplicate': bool(existing),
                    'has_errors': False,
                })

            self.env['construction.batch.material.preview'].create(preview_data)

        # Move to preview step
        self.step = 'preview'
        return self._get_action_view()

    def action_create_materials(self):
        """Create the actual materials"""
        if not self.preview_lines:
            raise UserError(_("No preview data available. Please parse the material data first."))

        try:
            # Parse the data again for creation
            parsed_data, errors = self._parse_material_data(self.material_data)

            if errors:
                raise UserError(_("Cannot create materials with validation errors:\n%s") % '\n'.join(errors))

            # Create materials
            result = self._create_materials(parsed_data)

            # Store results
            self.created_materials_count = result['materials_created']
            self.skipped_count = result['duplicates_skipped']
            self.result_message = result['message']

            # Move to result step
            self.step = 'result'
            return self._get_action_view()

        except Exception as e:
            _logger.error(f"Error creating batch materials: {str(e)}")
            raise UserError(_("Error creating materials: %s") % str(e))

    def action_previous_step(self):
        """Go back to previous step"""
        if self.step == 'preview':
            self.step = 'input'
        elif self.step == 'result':
            self.step = 'preview'
        return self._get_action_view()

    def action_view_created_materials(self):
        """View the created materials"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Materials'),
            'res_model': 'construction.material',
            'view_mode': 'tree,form',
            'domain': [],
            'context': {},
        }

    def _parse_material_data(self, material_data):
        """Parse pipe-separated material data into structured format"""
        parsed_data = []
        errors = []

        if not material_data:
            return parsed_data, errors

        lines = material_data.strip().split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            # Remove leading/trailing pipes and split
            line = line.strip('|').strip()
            if not line:
                continue

            # Split by pipe character and strip whitespace, filter empty parts
            parts = [part.strip() for part in line.split('|') if part.strip()]

            if len(parts) < 3:
                errors.append(f"Line {line_num}: Expected at least 3 parts separated by '|', got {len(parts)}: {line}")
                continue

            code = parts[0]
            name = parts[1]
            unit = parts[2]
            price_str = parts[3] if len(parts) > 3 else '0'

            # Validate material code
            if not code:
                errors.append(f"Line {line_num}: Material code cannot be empty")
                continue

            # Validate material name
            if not name:
                errors.append(f"Line {line_num}: Material name cannot be empty")
                continue

            # Validate and convert price
            try:
                # Remove any spaces or commas from price
                price_str = price_str.replace(',', '').replace(' ', '')
                price = float(price_str) if price_str else 0.0
            except ValueError:
                errors.append(f"Line {line_num}: Invalid price '{price_str}'. Must be a number.")
                continue

            parsed_data.append({
                'code': code,
                'name': name,
                'unit': unit,
                'price': price,
                'line_num': line_num,
            })

        return parsed_data, errors

    def _create_materials(self, parsed_data):
        """Create construction materials from parsed data"""
        if not parsed_data:
            return {'materials_created': 0, 'duplicates_skipped': 0, 'message': 'No data to process'}

        created_materials = []
        duplicates_skipped = 0

        for material_data in parsed_data:
            try:
                # Check if material already exists
                existing = self.env['construction.material'].search([
                    ('code', '=', material_data['code'])
                ], limit=1)

                if existing:
                    if self.skip_duplicates:
                        _logger.info(f"Skipping duplicate material: {material_data['code']}")
                        duplicates_skipped += 1
                        continue
                    else:
                        # Update existing material
                        existing.write({
                            'name': material_data['name'],
                            'unit_of_measure': material_data['unit'],
                            'standard_price': material_data['price'],
                        })
                        created_materials.append(existing)
                        _logger.info(f"Updated existing material: {existing.name}")
                        continue

                # Create new material
                material_vals = {
                    'code': material_data['code'],
                    'name': material_data['name'],
                    'unit_of_measure': material_data['unit'],
                    'standard_price': material_data['price'],
                    'active': True,
                }

                material = self.env['construction.material'].create(material_vals)
                created_materials.append(material)

                _logger.info(f"Created material: {material.name}")

            except Exception as e:
                _logger.error(f"Error creating material {material_data['code']}: {str(e)}")
                continue

        # Generate result message
        message = f"Batch Material Creation Completed!\n\n"
        message += f"✓ Created {len(created_materials)} materials\n"
        if duplicates_skipped > 0:
            message += f"⊘ Skipped {duplicates_skipped} duplicates\n"
        message += f"\nTotal processed: {len(parsed_data)} lines\n"

        return {
            'materials_created': len(created_materials),
            'duplicates_skipped': duplicates_skipped,
            'message': message,
        }

    def _get_action_view(self):
        """Return action to reload wizard view"""
        return {
            'name': _('Batch Create Materials'),
            'type': 'ir.actions.act_window',
            'res_model': 'construction.batch.material.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }


class BatchMaterialPreview(models.TransientModel):
    _name = 'construction.batch.material.preview'
    _description = 'Batch Material Preview Line'

    wizard_id = fields.Many2one('construction.batch.material.wizard', string='Wizard', ondelete='cascade')
    material_code = fields.Char(string='Code')
    material_name = fields.Char(string='Material Name')
    material_unit = fields.Char(string='Unit')
    material_price = fields.Float(string='Price')
    is_duplicate = fields.Boolean(string='Duplicate')
    has_errors = fields.Boolean(string='Has Errors')

import base64
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SmetaImportWizard(models.TransientModel):
    _name = 'construction.smeta.import.wizard'
    _description = 'Smeta Import Wizard'

    # Step 1: File Upload
    file_data = fields.Binary(string='Excel File', required=True,
                              help="Upload your Excel smeta file (.xls or .xlsx)")
    filename = fields.Char(string='File Name')
    project_id = fields.Many2one('project.project', string='Project', required=True,
                                 help="Select the project for this budget import")
    budget_id = fields.Many2one('construction.project.budget', string='Existing Budget',
                                domain="[('project_id', '=', project_id)]",
                                help="Optional: Select existing budget or leave empty to create new one")

    # Step 2: Column Mapping
    step = fields.Selection([
        ('upload', 'Upload File'),
        ('mapping', 'Column Mapping'),
        ('preview', 'Preview'),
        ('result', 'Import Result'),
    ], string='Step', default='upload')

    # Excel data storage
    excel_headers = fields.Text(string='Excel Headers')  # JSON string
    sample_data = fields.Text(string='Sample Data')      # JSON string

    # Column mapping fields
    category_column = fields.Selection([], string='Category Column', help="Column containing budget categories")
    item_column = fields.Selection([], string='Item Column', help="Column containing item descriptions")
    quantity_column = fields.Selection([], string='Quantity Column', help="Column containing quantities")
    unit_price_column = fields.Selection([], string='Unit Price Column', help="Column containing unit prices")
    total_column = fields.Selection([], string='Total Column', help="Column containing total amounts")
    uom_column = fields.Selection([], string='Unit of Measure Column', help="Column containing units of measure")

    # Header row
    header_row = fields.Integer(string='Header Row', default=1,
                                help="Row number containing column headers (starting from 1)")
    data_start_row = fields.Integer(string='Data Start Row', default=2,
                                    help="Row number where data starts (starting from 1)")

    # Preview data
    preview_lines = fields.One2many('construction.smeta.import.preview', 'wizard_id', string='Preview Lines')

    # Results
    import_result = fields.Text(string='Import Result', readonly=True)
    created_budget_id = fields.Many2one('construction.project.budget', string='Created/Updated Budget', readonly=True)
    import_log_id = fields.Many2one('construction.smeta.import.log', string='Import Log', readonly=True)

    @api.model
    def create(self, vals):
        """Override create to handle initial wizard creation"""
        record = super().create(vals)
        # Don't set item_column here - it will be set during file upload
        return record

    @api.onchange('file_data', 'filename')
    def _onchange_file_data(self):
        """Process uploaded file and extract headers"""
        if self.file_data and self.filename:
            try:
                # Decode file
                file_content = base64.b64decode(self.file_data)

                # Get processor and extract data
                processor = self.env['construction.smeta.processor']
                excel_data = processor._get_excel_data(file_content, self.filename)

                if excel_data and len(excel_data) > 0:
                    # Store headers and sample data
                    headers = excel_data[0] if excel_data else []
                    sample_rows = excel_data[1:6] if len(excel_data) > 1 else []  # First 5 data rows

                    import json
                    self.excel_headers = json.dumps(headers)
                    self.sample_data = json.dumps(sample_rows)

                    # Update column selection options
                    self._update_column_options(headers)

                    # Immediately check if this is Russian smeta and auto-map
                    if self._is_russian_smeta_file():
                        self._auto_map_russian_smeta_columns()
                        _logger.info("Auto-mapped Russian smeta columns during file upload")

            except Exception as e:
                raise UserError(_("Error processing file: %s") % str(e))

    def _update_column_options(self, headers):
        """Update selection field options based on Excel headers"""
        # Create selection options (index, header)
        options = [(str(i), f"{i+1}. {header}") for i, header in enumerate(headers)]

        # Update field definitions dynamically
        fields_to_update = ['category_column', 'item_column', 'quantity_column',
                           'unit_price_column', 'total_column', 'uom_column']

        for field_name in fields_to_update:
            field = self._fields[field_name]
            field.selection = options

        # Set a default item_column to prevent validation errors
        if len(headers) > 0:
            self.item_column = '0'  # Default to first column

        # Try to auto-map columns based on header names
        self._auto_map_columns(headers)

    def _auto_map_columns(self, headers):
        """Automatically map columns based on header names"""
        # Convert headers to lowercase for comparison and normalize spaces
        headers_lower = [header.lower().strip().replace(' ', '') for header in headers]

        # Enhanced auto-mapping rules for Russian smeta format
        mapping_rules = {
            'category_column': ['category', 'категория', 'раздел', 'тип', 'group', 'группа', 'обоснование'],
            'item_column': [
                'item', 'description', 'наименование', 'описание', 'работы', 'материал', 'name',
                'наименованиеработ', 'наименованиеработиресурсов', 'работыиресурсов', 'ресурсов'
            ],
            'quantity_column': [
                'quantity', 'qty', 'количество', 'кол-во', 'кол', 'объем', 'попроекту', 'проекту'
            ],
            'unit_price_column': ['unit_price', 'price', 'цена', 'стоимость', 'расценка', 'unit cost'],
            'total_column': ['total', 'amount', 'сумма', 'итого', 'всего', 'стоимость общая'],
            'uom_column': [
                'unit', 'uom', 'measure', 'единица', 'ед.изм', 'ед', 'изм', 'ед.', 'едизм'
            ],
        }

        # First, try exact Russian smeta header matching
        russian_smeta_mapping = {
            'наименованиеработиресурсов': 'item_column',
            'ед.изм': 'uom_column',
            'попроекту': 'quantity_column',
            '№№': 'category_column',  # Number column as category identifier
            'обоснование': 'category_column'
        }

        # Try exact Russian matches first
        for i, header in enumerate(headers_lower):
            for russian_header, field_name in russian_smeta_mapping.items():
                if russian_header in header.replace('.', '').replace(' ', ''):
                    setattr(self, field_name, str(i))
                    _logger.info(f"Auto-mapped Russian header '{headers[i]}' to {field_name}")

        # If we haven't found item_column yet, try broader keyword matching
        if not getattr(self, 'item_column', None):
            for field_name, keywords in mapping_rules.items():
                if not getattr(self, field_name, None):  # Only set if not already mapped
                    for i, header in enumerate(headers_lower):
                        if any(keyword in header for keyword in keywords):
                            setattr(self, field_name, str(i))
                            _logger.info(f"Auto-mapped header '{headers[i]}' to {field_name}")
                            break

        # Final fallback: if still no item_column, use the longest header (likely description)
        if not getattr(self, 'item_column', None) and headers:
            longest_header_idx = max(range(len(headers)), key=lambda i: len(headers[i]))
            self.item_column = str(longest_header_idx)
            _logger.info(f"Fallback: mapped longest header '{headers[longest_header_idx]}' to item_column")

    def _is_russian_smeta_file(self):
        """Check if the uploaded file is a Russian smeta format"""
        if not self.excel_headers:
            return False

        try:
            import json
            headers = json.loads(self.excel_headers)
            headers_str = ' '.join(headers).lower()

            # Check for Russian smeta indicators
            russian_indicators = [
                'наименование работ и ресурсов',
                'ед.изм',
                'по проекту',
                'раздел',
                'обоснование'
            ]

            return any(indicator in headers_str for indicator in russian_indicators)
        except:
            return False

    def _auto_map_russian_smeta_columns(self):
        """Auto-map columns for known Russian smeta format"""
        try:
            import json
            headers = json.loads(self.excel_headers)

            # Russian smeta standard column positions (0-indexed)
            # Column 0: №№ (Number)
            # Column 1: ОБОСНОВАНИЕ (Justification)
            # Column 2: НАИМЕНОВАНИЕ РАБОТ И РЕСУРСОВ (Item description)
            # Column 3: ЕД.ИЗМ (Unit of measure)
            # Column 4: КОЛ-ВО НА ЕДИНИЦУ (Quantity per unit)
            # Column 5: ПО ПРОЕКТУ (Project quantity)

            if len(headers) >= 6:
                # Standard Russian smeta format mapping
                self.category_column = '1'  # ОБОСНОВАНИЕ column
                self.item_column = '2'      # НАИМЕНОВАНИЕ РАБОТ И РЕСУРСОВ
                self.uom_column = '3'       # ЕД.ИЗМ
                self.quantity_column = '5'  # ПО ПРОЕКТУ

                _logger.info("Applied Russian smeta column mapping: item=2, uom=3, quantity=5, category=1")
            else:
                # Fallback: just ensure item_column is set
                if len(headers) >= 3:
                    self.item_column = '2'
                elif len(headers) >= 1:
                    self.item_column = '0'

                _logger.warning(f"Russian smeta has only {len(headers)} columns, using fallback mapping")

        except Exception as e:
            _logger.error(f"Error in Russian smeta auto-mapping: {str(e)}")
            # Final fallback - just set item_column to avoid validation error
            self.item_column = '0'

    @api.constrains('item_column', 'step')
    def _check_item_column_required(self):
        """Only validate item_column when moving to preview step"""
        for record in self:
            # Only check when step is 'preview' or later, not during initial creation
            if record.step in ('preview', 'result') and not record.item_column:
                raise ValidationError(_("Item column mapping is required to proceed with import."))

    def action_next_step(self):
        """Move to next step"""
        if self.step == 'upload':
            if not self.file_data or not self.filename:
                raise UserError(_("Please upload an Excel file first."))
            if not self.project_id:
                raise UserError(_("Please select a project."))

            self.step = 'mapping'
            return self._get_action_view()

        elif self.step == 'mapping':
            # Check if this is a Russian smeta file - if so, auto-detect and skip manual mapping
            if self._is_russian_smeta_file():
                _logger.info("Detected Russian smeta format - auto-mapping columns and proceeding")
                self._auto_map_russian_smeta_columns()

            # Final validation - ensure we have at least item_column mapped
            if not self.item_column:
                # Try auto-mapping one more time
                if self.excel_headers:
                    import json
                    headers = json.loads(self.excel_headers)
                    self._auto_map_columns(headers)

                # If still no mapping, throw error
                if not self.item_column:
                    raise UserError(_("Unable to detect item description column. Please ensure your file contains recognizable headers."))

            self._generate_preview()
            self.step = 'preview'
            return self._get_action_view()

        elif self.step == 'preview':
            result = self._execute_import()
            self.step = 'result'
            return self._get_action_view()

    def action_previous_step(self):
        """Move to previous step"""
        if self.step == 'mapping':
            self.step = 'upload'
        elif self.step == 'preview':
            self.step = 'mapping'
        elif self.step == 'result':
            self.step = 'preview'

        return self._get_action_view()

    def _generate_preview(self):
        """Generate preview of Russian smeta import data"""
        if not self.file_data or not self.filename:
            return

        try:
            # Decode and process file
            file_content = base64.b64decode(self.file_data)
            processor = self.env['construction.smeta.processor']
            excel_data = processor._get_excel_data(file_content, self.filename)

            # Clear existing preview lines
            self.preview_lines.unlink()

            # Parse the Russian smeta structure for preview
            parsed_tasks = processor._parse_russian_smeta_structure(excel_data)

            # Create preview data from parsed tasks
            preview_data = []
            preview_count = 0

            for task in parsed_tasks:
                if preview_count >= 15:  # Limit preview to first 15 items
                    break

                # Show both main tasks and sub-tasks in preview
                if task['type'] == 'main_task':
                    preview_data.append({
                        'wizard_id': self.id,
                        'row_number': f"MAIN {task['number']}",
                        'category': task['section'][:50] if task['section'] else 'Section',
                        'item': f"🏗️ {task['name'][:150]}" if task['name'] else '',
                        'quantity': '-',
                        'unit_price': '-',
                        'total': '-',
                        'uom': task['unit'][:20] if task['unit'] else '',
                    })
                    preview_count += 1

                elif task['type'] == 'sub_task' and task['total_quantity']:
                    quantity = processor._clean_numeric_value(task['total_quantity'])
                    if quantity > 0:  # Only show sub-tasks with quantities
                        preview_data.append({
                            'wizard_id': self.id,
                            'row_number': f"SUB {task['number']}",
                            'category': task['section'][:50] if task['section'] else '',
                            'item': f"  ↳ {task['name'][:140]}" if task['name'] else '',
                            'quantity': str(quantity),
                            'unit_price': '0.00',  # No prices in smeta
                            'total': '0.00',  # Will be filled from actual expenses
                            'uom': task['unit'][:20] if task['unit'] else '',
                        })
                        preview_count += 1

            # Create preview lines
            if preview_data:
                self.env['construction.smeta.import.preview'].create(preview_data)

        except Exception as e:
            _logger.error(f"Error generating Russian smeta preview: {str(e)}")
            raise UserError(_("Error generating preview: %s") % str(e))

    def _execute_import(self):
        """Execute the actual import for Russian smeta format"""
        if not self.file_data or not self.filename:
            raise UserError(_("No file to import."))

        try:
            # Decode and process file
            file_content = base64.b64decode(self.file_data)
            processor = self.env['construction.smeta.processor']
            excel_data = processor._get_excel_data(file_content, self.filename)

            # For Russian smeta format, use fixed column structure
            # №№ (0), ОБОСНОВАНИЕ (1), НАИМЕНОВАНИЕ РАБОТ И РЕСУРСОВ (2),
            # ЕД.ИЗМ (3), КОЛ-ВО НА ЕДИНИЦУ (4), ПО ПРОЕКТУ (5)
            column_mapping = {
                'number': 0,
                'justification': 1,
                'name': 2,
                'unit': 3,
                'quantity_per_unit': 4,
                'total_quantity': 5
            }

            # Process the Russian smeta import directly (no need for header adjustment)
            result = processor.process_smeta_data(
                excel_data,
                column_mapping,
                self.project_id.id,
                self.budget_id.id if self.budget_id else None
            )

            # Store results
            self.created_budget_id = result['budget_id']
            self.import_log_id = result['import_log_id']

            # Format result message for Russian smeta
            message = f"Russian Smeta Import completed!\n\n"
            message += f"• Imported: {result['imported_count']} budget lines (sub-tasks)\n"
            message += f"• Parsed: {result.get('parsed_tasks', 0)} total tasks from smeta\n"
            if result['error_count'] > 0:
                message += f"• Errors: {result['error_count']} lines had errors\n"
            message += f"• Budget: {self.created_budget_id.name}\n"
            message += f"• Project: {self.project_id.name}\n\n"
            message += "Created hierarchical budget structure:\n"
            message += "• Main tasks (1, 2, 3...) for work organization\n"
            message += "• Sub-tasks (1.1, 1.2, 2.1...) for specific resources"

            if result['errors']:
                message += f"\n\nErrors:\n" + '\n'.join(result['errors'][:10])  # Show first 10 errors
                if len(result['errors']) > 10:
                    message += f"\n... and {len(result['errors']) - 10} more errors"

            self.import_result = message

            return result

        except Exception as e:
            _logger.error(f"Error executing Russian smeta import: {str(e)}")
            error_message = f"Russian Smeta Import failed:\n{str(e)}"
            self.import_result = error_message
            raise UserError(_("Import failed: %s") % str(e))

    def _get_action_view(self):
        """Return action to reload wizard view"""
        return {
            'name': _('Import Smeta'),
            'type': 'ir.actions.act_window',
            'res_model': 'construction.smeta.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def action_view_budget(self):
        """Open created/updated budget"""
        if not self.created_budget_id:
            raise UserError(_("No budget was created."))

        return {
            'name': _('Budget'),
            'type': 'ir.actions.act_window',
            'res_model': 'construction.project.budget',
            'res_id': self.created_budget_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_import_log(self):
        """Open import log"""
        if not self.import_log_id:
            raise UserError(_("No import log available."))

        return {
            'name': _('Import Log'),
            'type': 'ir.actions.act_window',
            'res_model': 'construction.smeta.import.log',
            'res_id': self.import_log_id.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_download_template(self):
        """Download Excel template"""
        # This would generate and return an Excel template
        # For now, return action to show template info
        return {
            'type': 'ir.actions.act_window',
            'name': _('Download Template'),
            'res_model': 'construction.smeta.template',
            'view_mode': 'form',
            'target': 'new',
        }


class SmetaImportPreview(models.TransientModel):
    _name = 'construction.smeta.import.preview'
    _description = 'Smeta Import Preview Line'

    wizard_id = fields.Many2one('construction.smeta.import.wizard', string='Wizard', ondelete='cascade')
    row_number = fields.Integer(string='Row #')
    category = fields.Char(string='Category')
    item = fields.Char(string='Item Description')
    quantity = fields.Char(string='Quantity')
    unit_price = fields.Char(string='Unit Price')
    total = fields.Char(string='Total')
    uom = fields.Char(string='UoM')


class SmetaTemplate(models.TransientModel):
    """Helper model for template download"""
    _name = 'construction.smeta.template'
    _description = 'Smeta Template'

    name = fields.Char(string='Template Name', default='Smeta Template')
    description = fields.Html(string='Description', default="""
    <h3>Excel Smeta Template</h3>
    <p>Create an Excel file with the following columns:</p>
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>Column</th>
                <th>Description</th>
                <th>Example</th>
                <th>Required</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Category</strong></td>
                <td>Budget category (Materials, Labor, etc.)</td>
                <td>Materials / Материалы</td>
                <td>Optional</td>
            </tr>
            <tr>
                <td><strong>Item</strong></td>
                <td>Description of work or material</td>
                <td>Concrete foundation / Бетонное основание</td>
                <td><strong>Required</strong></td>
            </tr>
            <tr>
                <td><strong>Quantity</strong></td>
                <td>Amount/quantity needed</td>
                <td>10.5</td>
                <td>Optional</td>
            </tr>
            <tr>
                <td><strong>Unit Price</strong></td>
                <td>Price per unit</td>
                <td>1500.00</td>
                <td>Optional</td>
            </tr>
            <tr>
                <td><strong>Total</strong></td>
                <td>Total amount (calculated if empty)</td>
                <td>15750.00</td>
                <td>Optional</td>
            </tr>
            <tr>
                <td><strong>Unit of Measure</strong></td>
                <td>Unit (m², kg, hours, etc.)</td>
                <td>m² / кв.м</td>
                <td>Optional</td>
            </tr>
        </tbody>
    </table>
    <h4>Notes:</h4>
    <ul>
        <li>Use .xls or .xlsx format</li>
        <li>First row should contain column headers</li>
        <li>Russian text is fully supported</li>
        <li>Empty rows will be skipped</li>
        <li>If Total is not provided, it will be calculated as Quantity × Unit Price</li>
    </ul>
    """)
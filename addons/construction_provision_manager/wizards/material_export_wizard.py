# -*- coding: utf-8 -*-

import base64
import io
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.tools import pycompat


class MaterialExportWizard(models.TransientModel):
    _name = 'construction.material.export.wizard'
    _description = 'Material Export Wizard'

    export_type = fields.Selection([
        ('deliveries', 'Material Deliveries'),
        ('inventory', 'Project Inventory'),
        ('summary', 'Cost Summary by Project'),
    ], string='Export Type', required=True, default='deliveries')

    date_from = fields.Date(
        string='From Date',
        default=lambda self: fields.Date.today() - timedelta(days=30)
    )
    date_to = fields.Date(
        string='To Date',
        default=fields.Date.today
    )

    project_ids = fields.Many2many(
        'project.project',
        'material_export_project_rel',
        'wizard_id',
        'project_id',
        string='Projects',
        help='Leave empty to export all projects'
    )
    category_ids = fields.Many2many(
        'construction.material.category',
        'material_export_category_rel',
        'wizard_id',
        'category_id',
        string='Categories',
        help='Leave empty to export all categories'
    )

    file_format = fields.Selection([
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
    ], string='File Format', required=True, default='csv')

    export_file = fields.Binary(
        string='Export File',
        readonly=True
    )
    export_filename = fields.Char(
        string='Filename',
        readonly=True
    )

    def action_export(self):
        """Generate and download export file"""
        if self.export_type == 'deliveries':
            data = self._get_deliveries_data()
            filename = f"material_deliveries_{datetime.now().strftime('%Y%m%d_%H%M')}"
        elif self.export_type == 'inventory':
            data = self._get_inventory_data()
            filename = f"project_inventory_{datetime.now().strftime('%Y%m%d_%H%M')}"
        else:  # summary
            data = self._get_summary_data()
            filename = f"cost_summary_{datetime.now().strftime('%Y%m%d_%H%M')}"

        if self.file_format == 'csv':
            file_content = self._generate_csv(data)
            filename += '.csv'
        else:
            file_content = self._generate_xlsx(data)
            filename += '.xlsx'

        self.export_file = base64.b64encode(file_content)
        self.export_filename = filename

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'show_download': True}
        }

    def _get_deliveries_data(self):
        """Get material deliveries data"""
        domain = [
            ('delivery_date', '>=', self.date_from),
            ('delivery_date', '<=', self.date_to),
        ]

        if self.project_ids:
            domain.append(('project_id', 'in', self.project_ids.ids))
        if self.category_ids:
            domain.append(('category_id', 'in', self.category_ids.ids))

        deliveries = self.env['construction.material.delivery'].search(domain)

        data = []
        for delivery in deliveries:
            data.append({
                'Project': delivery.project_id.name,
                'Material': delivery.material_name,
                'Category': delivery.category_id.name,
                'Quantity': delivery.quantity,
                'Unit': delivery.unit,
                'Unit Price': delivery.unit_price,
                'Total Cost': delivery.total_cost,
                'Supplier': delivery.supplier_name or '',
                'Delivery Date': delivery.delivery_date.strftime('%Y-%m-%d %H:%M'),
                'Status': delivery.state,
                'Consumed': delivery.consumed_quantity,
                'Remaining': delivery.remaining_quantity,
                'Received By': delivery.received_by.name,
            })

        return data

    def _get_inventory_data(self):
        """Get project inventory data"""
        domain = []

        if self.project_ids:
            domain.append(('project_id', 'in', self.project_ids.ids))
        if self.category_ids:
            domain.append(('category_id', 'in', self.category_ids.ids))

        materials = self.env['construction.project.material'].search(domain)

        data = []
        for material in materials:
            data.append({
                'Project': material.project_id.name,
                'Material': material.material_name,
                'Category': material.category_id.name,
                'Total Delivered': material.total_delivered,
                'Total Consumed': material.total_consumed,
                'Current Stock': material.current_stock,
                'Total Cost': material.total_cost,
                'Status': material.status,
                'Last Delivery': material.last_delivery_date.strftime('%Y-%m-%d') if material.last_delivery_date else '',
                'Delivery Count': material.delivery_count,
            })

        return data

    def _get_summary_data(self):
        """Get cost summary by project"""
        domain = [
            ('delivery_date', '>=', self.date_from),
            ('delivery_date', '<=', self.date_to),
        ]

        if self.project_ids:
            domain.append(('project_id', 'in', self.project_ids.ids))
        if self.category_ids:
            domain.append(('category_id', 'in', self.category_ids.ids))

        deliveries = self.env['construction.material.delivery'].search(domain)

        # Group by project and category
        summary = {}
        for delivery in deliveries:
            project_name = delivery.project_id.name
            category_name = delivery.category_id.name

            if project_name not in summary:
                summary[project_name] = {}

            if category_name not in summary[project_name]:
                summary[project_name][category_name] = {
                    'quantity': 0,
                    'cost': 0,
                    'deliveries': 0
                }

            summary[project_name][category_name]['quantity'] += delivery.quantity
            summary[project_name][category_name]['cost'] += delivery.total_cost
            summary[project_name][category_name]['deliveries'] += 1

        # Convert to flat data structure
        data = []
        for project, categories in summary.items():
            for category, values in categories.items():
                data.append({
                    'Project': project,
                    'Category': category,
                    'Total Deliveries': values['deliveries'],
                    'Total Quantity': values['quantity'],
                    'Total Cost': values['cost'],
                    'Average Cost per Delivery': values['cost'] / values['deliveries'] if values['deliveries'] > 0 else 0,
                })

        return data

    def _generate_csv(self, data):
        """Generate CSV file content"""
        if not data:
            return b"No data to export"

        output = io.StringIO()

        # Write header
        headers = list(data[0].keys())
        output.write(','.join(headers) + '\n')

        # Write data rows
        for row in data:
            values = [str(row.get(header, '')) for header in headers]
            output.write(','.join(values) + '\n')

        content = output.getvalue()
        output.close()

        return content.encode('utf-8')

    def _generate_xlsx(self, data):
        """Generate Excel file content"""
        try:
            import xlsxwriter
        except ImportError:
            # Fallback to CSV if xlsxwriter not available
            return self._generate_csv(data)

        if not data:
            return b"No data to export"

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Materials Export')

        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#0064FF',
            'font_color': 'white',
            'border': 1
        })

        # Data format
        data_format = workbook.add_format({'border': 1})
        currency_format = workbook.add_format({'num_format': '$#,##0.00', 'border': 1})

        # Write headers
        headers = list(data[0].keys())
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Write data
        for row_num, row_data in enumerate(data, 1):
            for col, header in enumerate(headers):
                value = row_data.get(header, '')

                # Format currency columns
                if 'cost' in header.lower() or 'price' in header.lower():
                    worksheet.write(row_num, col, float(value) if value else 0, currency_format)
                else:
                    worksheet.write(row_num, col, value, data_format)

        # Auto-adjust column widths
        for col, header in enumerate(headers):
            worksheet.set_column(col, col, len(header) + 5)

        workbook.close()
        output.seek(0)
        content = output.read()
        output.close()

        return content

    def action_download(self):
        """Download the exported file"""
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model={self._name}&id={self.id}&field=export_file&download=true&filename={self.export_filename}',
            'target': 'self',
        }
# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json


class PMDashboardController(http.Controller):

    @http.route('/pm_dashboard', type='http', auth='user')
    def pm_dashboard_page(self, project_id=None, **kwargs):
        """Render PM Dashboard web page"""
        # Get dashboard data
        dashboard = request.env['construction.pm.dashboard']
        data = dashboard.get_dashboard_data(int(project_id) if project_id else None)

        return request.render('construction_pm_dashboard.pm_dashboard_template', {
            'dashboard_data': data,
            'page_title': 'Project Manager Dashboard'
        })

    @http.route('/pm_dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, project_id=None):
        """Get dashboard data via AJAX"""
        dashboard = request.env['construction.pm.dashboard']
        return dashboard.get_dashboard_data(project_id)

    @http.route('/pm_dashboard/refresh', type='json', auth='user')
    def refresh_dashboard(self, project_id=None):
        """Refresh dashboard data"""
        dashboard = request.env['construction.pm.dashboard']
        return dashboard.refresh_dashboard(project_id)

    @http.route('/pm_dashboard/task_board', type='json', auth='user')
    def get_task_board(self, project_id, filters=None):
        """Get task board data"""
        task_board = request.env['construction.pm.task.board']
        return task_board.get_board_data(project_id, filters)

    @http.route('/pm_dashboard/move_task', type='json', auth='user')
    def move_task(self, task_id, new_stage_id):
        """Move task to new stage"""
        task_board = request.env['construction.pm.task.board']
        return task_board.move_task(task_id, new_stage_id)

    @http.route('/pm_dashboard/update_task_priority', type='json', auth='user')
    def update_task_priority(self, task_id, priority):
        """Update task priority"""
        task_board = request.env['construction.pm.task.board']
        return task_board.update_task_priority(task_id, priority)

    @http.route('/pm_dashboard/assign_task_user', type='json', auth='user')
    def assign_task_user(self, task_id, user_id):
        """Assign user to task"""
        task_board = request.env['construction.pm.task.board']
        return task_board.assign_task_user(task_id, user_id)

    @http.route('/pm_dashboard/create_quick_task', type='json', auth='user')
    def create_quick_task(self, project_id, name, stage_id=None, user_id=None):
        """Create quick task"""
        task_board = request.env['construction.pm.task.board']
        return task_board.create_quick_task(project_id, name, stage_id, user_id)

    @http.route('/pm_dashboard/budget_analytics', type='json', auth='user')
    def get_budget_analytics(self, project_id, period='week'):
        """Get budget analytics"""
        budget_monitor = request.env['construction.pm.budget.monitor']
        return budget_monitor.get_budget_analytics(project_id, period)

    @http.route('/pm_dashboard/approve_expense', type='json', auth='user')
    def approve_expense(self, expense_id):
        """Approve expense"""
        budget_monitor = request.env['construction.pm.budget.monitor']
        return budget_monitor.approve_expense(expense_id)

    @http.route('/pm_dashboard/batch_approve_expenses', type='json', auth='user')
    def batch_approve_expenses(self, expense_ids):
        """Batch approve expenses"""
        budget_monitor = request.env['construction.pm.budget.monitor']
        return budget_monitor.batch_approve_expenses(expense_ids)

    @http.route('/pm_dashboard/export_budget', type='http', auth='user')
    def export_budget_report(self, project_id, format='xlsx'):
        """Export budget report"""
        project = request.env['project.project'].browse(int(project_id))
        if not project.exists():
            return request.not_found()

        budget_monitor = request.env['construction.pm.budget.monitor']
        export_data = budget_monitor._get_export_data(project)

        if format == 'csv':
            return self._export_csv(export_data, project.name)
        else:
            return self._export_xlsx(export_data, project.name)

    def _export_csv(self, data, project_name):
        """Export data as CSV"""
        import io
        import csv

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'category', 'item', 'budget_amount', 'spent_amount',
            'remaining_amount', 'percentage_used', 'task'
        ])

        writer.writeheader()
        for row in data:
            writer.writerow(row)

        content = output.getvalue()
        output.close()

        filename = f"budget_report_{project_name}_{fields.Date.today()}.csv"

        return request.make_response(
            content,
            headers=[
                ('Content-Type', 'text/csv'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )

    def _export_xlsx(self, data, project_name):
        """Export data as Excel"""
        try:
            import xlsxwriter
            import io

            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Budget Report')

            # Headers
            headers = ['Category', 'Item', 'Budget Amount', 'Spent Amount',
                      'Remaining Amount', 'Percentage Used', 'Task']

            # Write headers
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)

            # Write data
            for row, item in enumerate(data, 1):
                worksheet.write(row, 0, item['category'])
                worksheet.write(row, 1, item['item'])
                worksheet.write(row, 2, item['budget_amount'])
                worksheet.write(row, 3, item['spent_amount'])
                worksheet.write(row, 4, item['remaining_amount'])
                worksheet.write(row, 5, f"{item['percentage_used']:.1f}%")
                worksheet.write(row, 6, item['task'])

            workbook.close()
            content = output.getvalue()
            output.close()

            filename = f"budget_report_{project_name}_{fields.Date.today()}.xlsx"

            return request.make_response(
                content,
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', f'attachment; filename="{filename}"')
                ]
            )

        except ImportError:
            # Fallback to CSV if xlsxwriter not available
            return self._export_csv(data, project_name)
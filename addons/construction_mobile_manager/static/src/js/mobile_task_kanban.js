/** @odoo-module **/

import { KanbanView } from "@web/views/kanban/kanban_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { registry } from "@web/core/registry";

export class MobileTaskKanbanController extends KanbanController {
    /**
     * Handle mobile task status updates
     */
    async updateTaskStatus(taskId, newStatus) {
        try {
            const result = await this.rpc("/web/dataset/call_kw/construction.mobile.task.manager/update_task_status", {
                model: "construction.mobile.task.manager",
                method: "update_task_status",
                args: [taskId, newStatus],
                kwargs: {},
            });

            if (result.success) {
                // Reload the view to show updated status
                await this.reload();
                // Show success notification
                this.notification.add(result.message, {
                    type: "success",
                    title: "Task Updated",
                });
            } else {
                this.notification.add(result.message, {
                    type: "danger",
                    title: "Update Failed",
                });
            }
        } catch (error) {
            this.notification.add("Failed to update task status", {
                type: "danger",
                title: "Error",
            });
        }
    }

    /**
     * Load tasks with filtering
     */
    async loadTasks(filter = null) {
        try {
            const tasks = await this.rpc("/web/dataset/call_kw/construction.mobile.task.manager/get_my_tasks", {
                model: "construction.mobile.task.manager",
                method: "get_my_tasks",
                args: [filter],
                kwargs: {},
            });

            return tasks;
        } catch (error) {
            console.error("Failed to load tasks:", error);
            return [];
        }
    }
}

export class MobileTaskKanbanRenderer extends KanbanRenderer {
    /**
     * Setup mobile-specific event handlers
     */
    setup() {
        super.setup();
        this.setupMobileHandlers();
    }

    setupMobileHandlers() {
        // Handle filter button clicks
        $(document).on('click', '.o_mobile_filter_btn', (ev) => {
            ev.preventDefault();
            const filter = $(ev.currentTarget).data('filter');
            this.handleFilterChange(filter);
        });

        // Handle status change clicks
        $(document).on('click', '.o_mobile_status_change', (ev) => {
            ev.preventDefault();
            const status = $(ev.currentTarget).data('status');
            const taskId = $(ev.currentTarget).closest('.o_kanban_record').data('record-id');
            this.handleStatusChange(taskId, status);
        });

        // Handle quick action buttons
        $(document).on('click', '.o_mobile_status_btn', (ev) => {
            ev.preventDefault();
            const taskId = $(ev.currentTarget).data('task-id');
            const currentStage = $(ev.currentTarget).data('current-stage');
            this.handleQuickStatusUpdate(taskId, currentStage);
        });
    }

    handleFilterChange(filter) {
        // Update active filter button
        $('.o_mobile_filter_btn').removeClass('active btn-primary').addClass('btn-secondary');
        $(`.o_mobile_filter_btn[data-filter="${filter}"]`).removeClass('btn-secondary').addClass('btn-primary active');

        // Load filtered tasks
        this.controller.loadTasks(filter === 'all' ? null : filter).then(tasks => {
            this.renderTaskList(tasks);
        });
    }

    handleStatusChange(taskId, newStatus) {
        this.controller.updateTaskStatus(taskId, newStatus);
    }

    handleQuickStatusUpdate(taskId, currentStage) {
        // Determine next status based on current stage
        let nextStatus;
        const stageLower = currentStage.toLowerCase();

        if (stageLower.includes('todo') || stageLower.includes('new')) {
            nextStatus = 'progress';
        } else if (stageLower.includes('progress') || stageLower.includes('doing')) {
            nextStatus = 'done';
        } else {
            nextStatus = 'todo'; // Reset to beginning
        }

        this.controller.updateTaskStatus(taskId, nextStatus);
    }

    renderTaskList(tasks) {
        const taskListContainer = $('#mobile_task_list');
        if (!taskListContainer.length) return;

        taskListContainer.empty();

        if (tasks.length === 0) {
            taskListContainer.html(`
                <div class="text-center text-muted p-3">
                    <i class="fa fa-tasks fa-2x mb-2"></i>
                    <p>No tasks found</p>
                </div>
            `);
            return;
        }

        tasks.forEach(task => {
            const taskHtml = this.renderTaskCard(task);
            taskListContainer.append(taskHtml);
        });
    }

    renderTaskCard(task) {
        const priorityIcon = task.priority === '1' ? '<i class="fa fa-star text-warning" title="High Priority"></i>' : '';
        const deadlineText = task.deadline ? `<div class="small text-muted"><i class="fa fa-calendar"></i> ${task.deadline}</div>` : '';
        const budgetInfo = task.has_budget ? `
            <div class="small text-info">
                <i class="fa fa-dollar-sign"></i>
                ${task.budget_spent}/${task.budget_allocated}
                (${Math.round(task.budget_percentage)}%)
            </div>
        ` : '';

        return `
            <div class="card mb-2 o_mobile_task_item" data-task-id="${task.id}">
                <div class="card-body p-2">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="card-title mb-1">
                                ${priorityIcon}
                                ${task.name}
                            </h6>
                            <small class="text-muted">${task.project_name}</small>
                            ${deadlineText}
                            ${budgetInfo}
                        </div>
                        <div class="ml-2">
                            <span class="badge badge-${task.stage_color}">${task.stage}</span>
                        </div>
                    </div>
                    <div class="mt-2">
                        <div class="btn-group btn-group-sm w-100" role="group">
                            <button type="button" class="btn btn-outline-secondary o_mobile_status_change"
                                    data-status="todo" data-task-id="${task.id}">
                                To Do
                            </button>
                            <button type="button" class="btn btn-outline-warning o_mobile_status_change"
                                    data-status="progress" data-task-id="${task.id}">
                                Progress
                            </button>
                            <button type="button" class="btn btn-outline-success o_mobile_status_change"
                                    data-status="done" data-task-id="${task.id}">
                                Done
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

export const MobileTaskKanbanView = {
    ...KanbanView,
    Controller: MobileTaskKanbanController,
    Renderer: MobileTaskKanbanRenderer,
};

registry.category("views").add("mobile_task_kanban", MobileTaskKanbanView);
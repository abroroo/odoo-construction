/** @odoo-module **/

import { KanbanView } from "@web/views/kanban/kanban_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { registry } from "@web/core/registry";

export class PMKanbanController extends KanbanController {
    setup() {
        super.setup();
        this.rpc = this.env.services.rpc;
        this.notification = this.env.services.notification;
    }

    async moveTask(taskId, newStageId) {
        try {
            const result = await this.rpc("/pm_dashboard/move_task", {
                task_id: taskId,
                new_stage_id: newStageId
            });

            if (result.success) {
                this.notification.add(result.message, { type: "success" });
                await this.reload();
            } else {
                this.notification.add(result.message, { type: "danger" });
            }
        } catch (error) {
            console.error("Error moving task:", error);
            this.notification.add("Failed to move task", { type: "danger" });
        }
    }

    async updateTaskPriority(taskId, priority) {
        try {
            const result = await this.rpc("/pm_dashboard/update_task_priority", {
                task_id: taskId,
                priority: priority
            });

            if (result.success) {
                this.notification.add(result.message, { type: "success" });
                await this.reload();
            } else {
                this.notification.add(result.message, { type: "danger" });
            }
        } catch (error) {
            console.error("Error updating task priority:", error);
            this.notification.add("Failed to update priority", { type: "danger" });
        }
    }

    async assignTaskUser(taskId, userId) {
        try {
            const result = await this.rpc("/pm_dashboard/assign_task_user", {
                task_id: taskId,
                user_id: userId
            });

            if (result.success) {
                this.notification.add(result.message, { type: "success" });
                await this.reload();
            } else {
                this.notification.add(result.message, { type: "warning" });
            }
        } catch (error) {
            console.error("Error assigning user:", error);
            this.notification.add("Failed to assign user", { type: "danger" });
        }
    }

    async createQuickTask(projectId, name, stageId = null, userId = null) {
        try {
            const result = await this.rpc("/pm_dashboard/create_quick_task", {
                project_id: projectId,
                name: name,
                stage_id: stageId,
                user_id: userId
            });

            if (result.success) {
                this.notification.add(result.message, { type: "success" });
                await this.reload();
                return result.task_id;
            } else {
                this.notification.add(result.message, { type: "danger" });
                return null;
            }
        } catch (error) {
            console.error("Error creating task:", error);
            this.notification.add("Failed to create task", { type: "danger" });
            return null;
        }
    }
}

export class PMKanbanRenderer extends KanbanRenderer {
    setup() {
        super.setup();
        this.setupDragAndDrop();
        this.setupMobileHandlers();
    }

    setupDragAndDrop() {
        // Desktop drag and drop functionality
        if (this.isMobile()) return;

        $(document).on('dragstart', '.pm_task_card', (e) => {
            const taskId = $(e.currentTarget).data('task-id');
            e.originalEvent.dataTransfer.setData('text/plain', taskId);
            $(e.currentTarget).addClass('dragging');
        });

        $(document).on('dragend', '.pm_task_card', (e) => {
            $(e.currentTarget).removeClass('dragging');
        });

        $(document).on('dragover', '.pm_board_column', (e) => {
            e.preventDefault();
            $(e.currentTarget).addClass('drag-over');
        });

        $(document).on('dragleave', '.pm_board_column', (e) => {
            $(e.currentTarget).removeClass('drag-over');
        });

        $(document).on('drop', '.pm_board_column', (e) => {
            e.preventDefault();
            $(e.currentTarget).removeClass('drag-over');

            const taskId = parseInt(e.originalEvent.dataTransfer.getData('text/plain'));
            const newStageId = parseInt($(e.currentTarget).data('stage-id'));

            if (taskId && !isNaN(newStageId)) {
                this.controller.moveTask(taskId, newStageId);
            }
        });
    }

    setupMobileHandlers() {
        // Mobile touch handlers for task updates
        $(document).on('click', '.pm_mobile_status_btn', (e) => {
            e.preventDefault();
            const taskId = parseInt($(e.currentTarget).data('task-id'));
            const currentStage = $(e.currentTarget).data('current-stage');
            this.handleMobileStatusUpdate(taskId, currentStage);
        });

        $(document).on('click', '.pm_priority_btn', (e) => {
            e.preventDefault();
            const taskId = parseInt($(e.currentTarget).data('task-id'));
            const priority = $(e.currentTarget).data('priority');
            this.controller.updateTaskPriority(taskId, priority);
        });

        $(document).on('click', '.pm_assign_btn', (e) => {
            e.preventDefault();
            const taskId = parseInt($(e.currentTarget).data('task-id'));
            const userId = parseInt($(e.currentTarget).data('user-id'));
            this.controller.assignTaskUser(taskId, userId);
        });

        // Quick task creation
        $(document).on('click', '.pm_add_task_btn', (e) => {
            e.preventDefault();
            const stageId = parseInt($(e.currentTarget).data('stage-id'));
            this.showQuickTaskDialog(stageId);
        });
    }

    handleMobileStatusUpdate(taskId, currentStage) {
        // Determine next status based on current stage
        let nextStageId;
        const stageLower = currentStage.toLowerCase();

        if (stageLower.includes('todo') || stageLower.includes('new')) {
            // Move to progress stage
            nextStageId = this.findStageIdByName(['progress', 'doing', 'started']);
        } else if (stageLower.includes('progress') || stageLower.includes('doing')) {
            // Move to done stage
            nextStageId = this.findStageIdByName(['done', 'complete', 'finished']);
        } else {
            // Reset to todo
            nextStageId = this.findStageIdByName(['todo', 'new', 'draft']);
        }

        if (nextStageId) {
            this.controller.moveTask(taskId, nextStageId);
        }
    }

    findStageIdByName(stageNames) {
        // Find stage ID by matching stage names
        const stages = this.getStages();
        for (const stageName of stageNames) {
            const stage = stages.find(s => s.name.toLowerCase().includes(stageName));
            if (stage) return stage.id;
        }
        return null;
    }

    getStages() {
        // Get available stages from the current kanban data
        // This would need to be implemented based on how stages are stored
        return [];
    }

    showQuickTaskDialog(stageId) {
        const taskName = prompt("Enter task name:");
        if (taskName && taskName.trim()) {
            const projectId = this.getProjectId(); // Get current project ID
            this.controller.createQuickTask(projectId, taskName.trim(), stageId);
        }
    }

    getProjectId() {
        // Get project ID from context or URL
        return parseInt(this.env.searchModel.context.default_project_id) || null;
    }

    isMobile() {
        return window.innerWidth <= 768;
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount || 0);
    }

    formatDate(dateStr) {
        if (!dateStr) return '';
        return new Date(dateStr).toLocaleDateString();
    }

    getBudgetBarClass(percentage, isOverBudget) {
        if (isOverBudget) return 'pm_budget_over';
        if (percentage >= 80) return 'pm_budget_warning';
        return 'pm_budget_normal';
    }

    getPriorityClass(priority) {
        switch (priority) {
            case '1': return 'priority-high';
            case '0':
            default: return 'priority-normal';
        }
    }

    // Task card rendering helper
    renderTaskCard(task) {
        const priorityClass = this.getPriorityClass(task.priority);
        const budgetClass = this.getBudgetBarClass(task.budget_percentage, task.is_over_budget);
        const deadlineClass = task.is_overdue ? 'overdue' : '';

        return `
            <div class="pm_task_card ${priorityClass}"
                 data-task-id="${task.id}"
                 draggable="true">

                <div class="pm_task_title">${task.name}</div>

                ${task.description ? `<div class="pm_task_description">${task.description}</div>` : ''}

                <div class="pm_task_meta">
                    <div class="pm_task_assignees">
                        ${task.assignees.map(user => `
                            <img class="pm_assignee_avatar"
                                 src="/web/image/res.users/${user.id}/avatar_128"
                                 title="${user.name}"
                                 alt="${user.name}">
                        `).join('')}
                    </div>

                    ${task.deadline ? `
                        <div class="pm_task_deadline ${deadlineClass}">
                            <i class="fa fa-calendar"></i>
                            ${task.deadline_label || this.formatDate(task.deadline)}
                        </div>
                    ` : ''}
                </div>

                ${task.has_budget ? `
                    <div class="pm_task_budget">
                        <small>${this.formatCurrency(task.budget_spent)} / ${this.formatCurrency(task.budget_allocated)}</small>
                        <div class="pm_budget_bar">
                            <div class="pm_budget_fill ${budgetClass}"
                                 style="width: ${Math.min(task.budget_percentage, 100)}%"></div>
                        </div>
                    </div>
                ` : ''}

                ${this.isMobile() ? `
                    <div class="pm_mobile_controls">
                        <button class="btn btn-sm btn-outline-primary pm_mobile_status_btn"
                                data-task-id="${task.id}"
                                data-current-stage="${task.stage_name}">
                            <i class="fa fa-forward"></i> Next Stage
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }
}

export const PMKanbanView = {
    ...KanbanView,
    Controller: PMKanbanController,
    Renderer: PMKanbanRenderer,
};

registry.category("views").add("pm_kanban", PMKanbanView);
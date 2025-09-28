/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PMDashboard extends Component {
    setup() {
        this.state = useState({
            loading: true,
            currentProject: null,
            projects: [],
            dashboardData: {},
            lastRefresh: new Date(),
        });

        this.rpc = useService("rpc");
        this.notification = useService("notification");

        onMounted(() => {
            this.loadDashboard();
            // Auto-refresh every 5 minutes
            this.refreshInterval = setInterval(() => {
                this.refreshDashboard();
            }, 300000);
        });

        onWillUnmount(() => {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
        });
    }

    async loadDashboard(projectId = null) {
        this.state.loading = true;
        try {
            const data = await this.rpc("/pm_dashboard/data", {
                project_id: projectId
            });

            if (data.error) {
                this.notification.add(data.error, { type: "warning" });
                return;
            }

            this.state.projects = data.projects || [];
            this.state.currentProject = data.current_project || {};
            this.state.dashboardData = data;
            this.state.lastRefresh = new Date();

        } catch (error) {
            console.error("Error loading dashboard:", error);
            this.notification.add("Failed to load dashboard data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async refreshDashboard() {
        const projectId = this.state.currentProject?.id;
        try {
            const data = await this.rpc("/pm_dashboard/refresh", {
                project_id: projectId
            });

            if (!data.error) {
                this.state.dashboardData = data;
                this.state.currentProject = data.current_project || {};
                this.state.lastRefresh = new Date();

                this.notification.add("Dashboard refreshed", {
                    type: "success",
                    sticky: false
                });
            }
        } catch (error) {
            console.error("Error refreshing dashboard:", error);
        }
    }

    async onProjectChange(ev) {
        const projectId = parseInt(ev.target.value);
        if (projectId && projectId !== this.state.currentProject?.id) {
            await this.loadDashboard(projectId);
        }
    }

    onRefreshClick() {
        this.refreshDashboard();
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount || 0);
    }

    formatPercentage(percentage) {
        return `${(percentage || 0).toFixed(1)}%`;
    }

    formatDate(dateStr) {
        if (!dateStr) return 'No date';
        return new Date(dateStr).toLocaleDateString();
    }

    getProgressBarClass(percentage) {
        if (percentage >= 100) return 'pm_progress_danger';
        if (percentage >= 80) return 'pm_progress_warning';
        if (percentage >= 60) return 'pm_progress_info';
        return 'pm_progress_success';
    }

    getBudgetStatusClass(isOverBudget, percentage) {
        if (isOverBudget) return 'pm_progress_danger';
        if (percentage >= 90) return 'pm_progress_warning';
        return 'pm_progress_success';
    }
}

PMDashboard.template = "PMDashboard";

// Register the component
registry.category("actions").add("pm_dashboard", PMDashboard);
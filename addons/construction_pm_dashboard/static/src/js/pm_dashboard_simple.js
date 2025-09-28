// Simple PM Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Project selector change handler
    const projectSelector = document.getElementById('projectSelector');
    if (projectSelector) {
        projectSelector.addEventListener('change', function() {
            const projectId = this.value;
            if (projectId) {
                // Reload page with selected project
                window.location.href = `/pm_dashboard?project_id=${projectId}`;
            }
        });
    }

    // Refresh button handler
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            // Reload current page
            window.location.reload();
        });
    }

    // Auto-refresh every 5 minutes
    setInterval(function() {
        console.log('Auto-refreshing dashboard...');
        window.location.reload();
    }, 300000); // 5 minutes

    console.log('PM Dashboard loaded successfully');
});
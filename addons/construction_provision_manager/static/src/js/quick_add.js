/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

// Quick Add Dashboard Action
function quickAddMaterialAction(env, action) {
    const actionService = env.services.action;

    actionService.doAction({
        type: 'ir.actions.act_window',
        name: 'Quick Add Material',
        res_model: 'construction.material.delivery',
        view_mode: 'form',
        target: 'new',
        context: {
            default_state: 'draft',
            form_view_initial_mode: 'edit'
        }
    });
}

// Register the action
registry.category("actions").add("quick_add_material", quickAddMaterialAction);

// Mobile touch helpers
document.addEventListener('DOMContentLoaded', function() {
    // Add touch-friendly class to body on mobile devices
    if (window.innerWidth <= 767) {
        document.body.classList.add('mobile-touch');
    }

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 767) {
            document.body.classList.add('mobile-touch');
        } else {
            document.body.classList.remove('mobile-touch');
        }
    });

    // Add haptic feedback for touch devices (if supported)
    if ('vibrate' in navigator) {
        document.addEventListener('click', function(e) {
            if (e.target.matches('.btn, button, .o_kanban_card')) {
                navigator.vibrate(50); // Short vibration feedback
            }
        });
    }

    // Auto-focus first input in forms on mobile
    const forms = document.querySelectorAll('.o_form_view');
    forms.forEach(form => {
        const firstInput = form.querySelector('input[type="text"], input[type="number"], select');
        if (firstInput && window.innerWidth <= 767) {
            // Delay to ensure form is fully rendered
            setTimeout(() => {
                firstInput.focus();
            }, 300);
        }
    });
});
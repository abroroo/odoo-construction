/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart } from "@odoo/owl";

// Quick Add Material Widget
export class QuickAddMaterialWidget extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            commonMaterials: [],
            selectedProject: null,
            loading: false
        });

        onWillStart(async () => {
            await this.loadCommonMaterials();
        });
    }

    async loadCommonMaterials() {
        try {
            this.state.commonMaterials = await this.orm.searchRead(
                "construction.common.material",
                [["is_frequently_used", "=", true]],
                ["name", "category_id", "default_unit", "average_price"],
                { limit: 12 }
            );
        } catch (error) {
            console.error("Error loading common materials:", error);
        }
    }

    async quickAddMaterial(material) {
        if (!this.state.selectedProject) {
            this.notification.add("Please select a project first", { type: "warning" });
            return;
        }

        this.state.loading = true;

        try {
            const deliveryId = await this.orm.create("construction.material.delivery", [{
                project_id: this.state.selectedProject,
                material_name: material.name,
                category_id: material.category_id[0],
                unit: material.default_unit,
                unit_price: material.average_price || 0,
                quantity: 1,
                state: 'draft'
            }]);

            this.notification.add(`Added ${material.name} to project`, { type: "success" });

            // Open the created delivery for editing
            this.action.doAction({
                type: 'ir.actions.act_window',
                res_model: 'construction.material.delivery',
                res_id: deliveryId,
                view_mode: 'form',
                target: 'new'
            });

        } catch (error) {
            this.notification.add("Error adding material", { type: "danger" });
            console.error("Error creating material delivery:", error);
        } finally {
            this.state.loading = false;
        }
    }

    getCategoryClass(categoryName) {
        const categoryClasses = {
            'Construction Materials': 'category-construction',
            'Tools': 'category-tools',
            'Equipment': 'category-equipment',
            'Electrical': 'category-electrical',
            'Plumbing': 'category-plumbing',
            'Safety Equipment': 'category-safety'
        };
        return categoryClasses[categoryName] || 'category-default';
    }
}

QuickAddMaterialWidget.template = "construction_provision_manager.QuickAddMaterialWidget";

// Quantity Helper Widget
export class QuantityHelperWidget extends Component {
    setup() {
        this.state = useState({
            currentQuantity: this.props.initialQuantity || 0
        });
    }

    updateQuantity(increment) {
        const newQuantity = this.state.currentQuantity + increment;
        if (newQuantity >= 0) {
            this.state.currentQuantity = newQuantity;
            this.props.onQuantityChange(newQuantity);
        }
    }

    setQuantity(value) {
        if (value >= 0) {
            this.state.currentQuantity = value;
            this.props.onQuantityChange(value);
        }
    }
}

QuantityHelperWidget.template = "construction_provision_manager.QuantityHelperWidget";

// Register widgets
registry.category("public_components").add("QuickAddMaterialWidget", QuickAddMaterialWidget);
registry.category("public_components").add("QuantityHelperWidget", QuantityHelperWidget);
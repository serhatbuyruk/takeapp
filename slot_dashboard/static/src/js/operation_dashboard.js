/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useRef, useState } from "@odoo/owl";


export class OperationDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.rosterRef = useRef("roster");
        this.state = useState({
            loading: true,
            data: null,
            selectedDate: null,
            statusFilter: "all",
            shiftActionLineId: null,
            selectedRestaurantName: null,
        });
        onWillStart(() => this.loadDashboard());
    }

    get filteredRows() {
        const rows = this.state.data?.rows || [];
        if (this.state.statusFilter === "all") {
            return rows;
        }
        if (this.state.statusFilter === "attention") {
            return rows.filter((row) => ["missing", "late"].includes(row.status));
        }
        if (this.state.statusFilter === "arrived") {
            return rows.filter((row) => !["missing", "upcoming"].includes(row.status));
        }
        if (["on_time", "late", "missing"].includes(this.state.statusFilter)) {
            const seenCouriers = new Set();
            return rows.filter((row) => {
                if (
                    row.courier_status !== this.state.statusFilter
                    || seenCouriers.has(row.courier_id)
                ) {
                    return false;
                }
                seenCouriers.add(row.courier_id);
                return true;
            });
        }
        return rows.filter((row) => row.status === this.state.statusFilter);
    }

    get selectedRestaurantRows() {
        if (!this.state.selectedRestaurantName) {
            return [];
        }
        return (this.state.data?.rows || []).filter(
            (row) => row.restaurant_name === this.state.selectedRestaurantName
        );
    }

    async loadDashboard(date = this.state.selectedDate) {
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "slots.profile",
                "get_operation_dashboard_data",
                [date || false]
            );
            this.state.data = data;
            this.state.selectedDate = data.selected_date;
            if (
                this.state.selectedRestaurantName
                && !data.restaurants.some(
                    (restaurant) => restaurant.name === this.state.selectedRestaurantName
                )
            ) {
                this.state.selectedRestaurantName = null;
            }
        } catch (error) {
            this.notification.add(
                error.message || "Dashboard verileri yüklenemedi.",
                {type: "danger"}
            );
        } finally {
            this.state.loading = false;
        }
    }

    async refresh() {
        await this.loadDashboard();
        this.notification.add("Operasyon verileri yenilendi.", {
            type: "success",
        });
    }

    onDateChange(event) {
        const selectedDate = event.target.value;
        // Keep shortcut actions on the date shown in the input even while
        // the dashboard RPC is still refreshing.
        this.state.selectedDate = selectedDate;
        this.loadDashboard(selectedDate);
    }

    openToday() {
        this.loadDashboard(false);
    }

    setFilter(filter) {
        this.state.statusFilter = filter;
    }

    showRoster(filter) {
        this.setFilter(filter);
        requestAnimationFrame(() => {
            this.rosterRef.el?.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });
        });
    }

    openSlots() {
        this.action.doAction("slots.slots_list");
    }

    async openShiftImport() {
        await this.action.doAction("slot_dashboard.action_shift_import_wizard");
        await this.loadDashboard();
    }

    async openManualShift() {
        await this.action.doAction(
            "slot_dashboard.action_manual_shift_wizard",
            {
                additionalContext: {
                    default_shift_date: this.state.selectedDate,
                },
            }
        );
        await this.loadDashboard();
    }

    async openAttendanceAdjustment() {
        await this.action.doAction(
            "slot_dashboard.action_attendance_wizard",
            {
                additionalContext: {
                    default_attendance_date: this.state.selectedDate,
                },
            }
        );
        await this.loadDashboard();
    }

    async openAttendanceAdjustments() {
        const action = await this.orm.call(
            "slots.profile",
            "get_attendance_adjustment_action",
            [this.state.selectedDate || false]
        );
        this.action.doAction(action);
    }

    async openShiftPlan() {
        const action = await this.orm.call(
            "slots.profile",
            "get_shift_management_action",
            [this.state.selectedDate || false, "shifts"]
        );
        this.action.doAction(action);
    }

    async openShiftPackages() {
        const action = await this.orm.call(
            "slots.profile",
            "get_shift_management_action",
            [this.state.selectedDate || false, "packages"]
        );
        this.action.doAction(action);
    }

    openCourierEarnings() {
        this.action.doAction("slot_dashboard.action_courier_earning_wizard");
    }

    openReconciliations() {
        this.action.doAction("slots.action_package_reconciliations");
    }

    openRestaurants() {
        this.action.doAction("corders.action_restoran_contacts");
    }

    openRestaurantDetails(restaurant) {
        this.state.selectedRestaurantName = restaurant.name;
    }

    closeRestaurantDetails() {
        this.state.selectedRestaurantName = null;
    }

    async openCourierShiftLine(row) {
        try {
            const action = await this.orm.call(
                "slots.profile",
                "get_operation_shift_line_action",
                [row.line_id]
            );
            await this.action.doAction(action);
        } catch (error) {
            this.notification.add(
                error.message || "Kurye vardiya satırı açılamadı.",
                {type: "danger"}
            );
        }
    }

    async toggleCourierShift(row) {
        const stopping = row.can_stop_shift;
        const question = stopping
            ? `${row.courier_name} vardiyasını şimdi sonlandırmak istiyor musunuz?`
            : `${row.courier_name} vardiyasını yeniden başlatmak istiyor musunuz?`;
        if (!window.confirm(question)) {
            return;
        }
        this.state.shiftActionLineId = row.line_id;
        try {
            const result = await this.orm.call(
                "slots.profile",
                "action_operation_dashboard_toggle_shift",
                [row.line_id]
            );
            this.notification.add(result.message, {type: "success"});
            await this.loadDashboard();
        } catch (error) {
            this.notification.add(
                error.message || "Vardiya işlemi tamamlanamadı.",
                {type: "danger"}
            );
        } finally {
            this.state.shiftActionLineId = null;
        }
    }
}

OperationDashboard.template = "slot_dashboard.OperationDashboard";
registry.category("actions").add(
    "slot_dashboard.operation_dashboard",
    OperationDashboard
);

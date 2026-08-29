/** @odoo-module **/

const BATTERY_WARNING_TEXT = "Pil seviyesi %20'nin altında";

function removeBatteryWarning(root = document) {
    if (
        root.nodeType === Node.ELEMENT_NODE
        && root.childElementCount <= 6
        && root.textContent.includes(BATTERY_WARNING_TEXT)
    ) {
        root.remove();
        return;
    }

    const candidates = root.querySelectorAll
        ? root.querySelectorAll(".alert, [role='alert'], .toast, section, div")
        : [];

    for (const element of candidates) {
        if (
            element.childElementCount <= 6
            && element.textContent.includes(BATTERY_WARNING_TEXT)
        ) {
            element.remove();
        }
    }
}

function startBatteryWarningCleanup() {
    removeBatteryWarning();
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            for (const node of mutation.addedNodes) {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    removeBatteryWarning(node);
                }
            }
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startBatteryWarningCleanup, { once: true });
} else {
    startBatteryWarningCleanup();
}

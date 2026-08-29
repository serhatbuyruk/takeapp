/** @odoo-module **/

function rpc(url, params = {}) {
    return fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params,
            id: Date.now(),
        }),
    }).then(async (response) => {
        if (!response.ok) {
            throw new Error("Sunucuya ulaşılamadı. Lütfen tekrar dene.");
        }
        const payload = await response.json();
        if (payload.error) {
            throw new Error(
                payload.error.data?.message
                || payload.error.message
                || "İşlem tamamlanamadı."
            );
        }
        return payload.result;
    });
}

function setText(root, selector, value) {
    const element = root.querySelector(selector);
    if (element) {
        element.textContent = value || "";
    }
}

function showError(root, message) {
    const error = root.querySelector("[data-kt-package-error]");
    error.textContent = message;
    error.hidden = false;
}

function normalizeCount(input) {
    const raw = input.value.trim();
    if (!/^\d+$/.test(raw)) {
        return null;
    }
    const value = Number(raw);
    return Number.isSafeInteger(value) && value >= 0 ? value : null;
}

function activateGate(root, pending) {
    root.dataset.lineId = pending.line_id;
    setText(root, "[data-kt-package-slot-name]", pending.slot_name);
    setText(root, "[data-kt-package-restaurant]", pending.restaurant_name);
    setText(root, "[data-kt-package-slot-date]", pending.slot_date);
    setText(root, "[data-kt-package-time-range]", pending.time_range);
    root.classList.add("is-required");
    root.setAttribute("aria-hidden", "false");
    document.documentElement.classList.add("kt-package-gate-open");
    root.querySelector("[data-kt-package-count]")?.focus({preventScroll: true});
}

async function initializePackageReconciliation() {
    const root = document.getElementById("kt-package-reconciliation-root");
    if (!root || root.dataset.ready) {
        return;
    }
    root.dataset.ready = "1";

    const input = root.querySelector("[data-kt-package-count]");
    const form = root.querySelector("[data-kt-package-form]");
    const submit = root.querySelector("[data-kt-package-submit]");
    root.querySelector("[data-kt-package-minus]")?.addEventListener("click", () => {
        input.value = Math.max(0, (normalizeCount(input) || 0) - 1);
    });
    root.querySelector("[data-kt-package-plus]")?.addEventListener("click", () => {
        input.value = (normalizeCount(input) || 0) + 1;
    });
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const count = normalizeCount(input);
        if (count === null) {
            showError(root, "Lütfen sıfır veya daha büyük tam sayı gir.");
            input.focus();
            return;
        }
        submit.disabled = true;
        submit.innerHTML = '<i class="fa fa-circle-o-notch fa-spin"></i> Gönderiliyor';
        try {
            const result = await rpc("/courier/package-reconciliation/submit", {
                line_id: Number(root.dataset.lineId),
                package_count: count,
            });
            if (!result || result.status !== "success") {
                throw new Error(result?.message || "Paket sayısı gönderilemedi.");
            }
            submit.innerHTML = '<i class="fa fa-check"></i> Gönderildi';
            window.setTimeout(() => window.location.reload(), 500);
        } catch (error) {
            showError(root, error.message);
            submit.disabled = false;
            submit.textContent = "Restoran Onayına Gönder";
        }
    });

    const checkPending = async () => {
        if (root.classList.contains("is-required")) {
            return;
        }
        try {
            const pending = await rpc("/courier/package-reconciliation/pending");
            if (pending?.required) {
                activateGate(root, pending);
            }
        } catch (error) {
            // Geçici bağlantı sorununda kontrol bir sonraki periyotta yenilenir.
        }
    };
    await checkPending();
    window.setInterval(checkPending, 30000);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializePackageReconciliation, {
        once: true,
    });
} else {
    initializePackageReconciliation();
}

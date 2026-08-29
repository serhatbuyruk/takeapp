/** @odoo-module **/

function setStartFeedback(button, message, type = "info") {
    const container = button
        .closest(".kt-work-card")
        ?.querySelector("[data-kt-slot-start-feedback]");
    if (!container) {
        return;
    }
    container.textContent = message;
    container.className = `kt-slot-start-feedback is-${type}`;
    container.hidden = false;
}

async function requestSlotStart(button, position) {
    const response = await fetch("/courier/slot/start", {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params: {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
            },
            id: Date.now(),
        }),
    });
    if (!response.ok) {
        throw new Error("Sunucuya ulaşılamadı. Lütfen tekrar deneyin.");
    }
    const payload = await response.json();
    if (payload.error) {
        throw new Error(
            payload.error.data?.message
            || payload.error.message
            || "Vardiya başlatılamadı."
        );
    }
    return payload.result;
}

function handleSlotStart(button) {
    if (!navigator.geolocation) {
        setStartFeedback(
            button,
            "Telefonunuz anlık konum almayı desteklemiyor.",
            "error"
        );
        return;
    }

    const originalLabel = button.innerHTML;
    button.disabled = true;
    button.classList.add("is-loading");
    button.innerHTML = '<i class="fa fa-circle-o-notch fa-spin"></i> Konum alınıyor';
    setStartFeedback(
        button,
        "Restorana uzaklığınız kontrol ediliyor…",
        "info"
    );

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            try {
                const result = await requestSlotStart(button, position);
                if (!result || result.status !== "success") {
                    throw new Error(result?.message || "Vardiya başlatılamadı.");
                }
                setStartFeedback(
                    button,
                    `${result.message} Restorana uzaklığınız ${Math.round(result.distance)} metre.`,
                    "success"
                );
                window.setTimeout(() => {
                    window.location.assign("/kurye-anasayfa?slot_started=1");
                }, 700);
            } catch (error) {
                setStartFeedback(button, error.message, "error");
                button.disabled = false;
                button.classList.remove("is-loading");
                button.innerHTML = originalLabel;
            }
        },
        (error) => {
            const messages = {
                1: "Konum izni verilmedi. Vardiyayı başlatmak için konum izni vermelisiniz.",
                2: "Anlık konumunuz belirlenemedi. GPS'i açıp tekrar deneyin.",
                3: "Konum alınırken zaman aşımı oluştu. Lütfen tekrar deneyin.",
            };
            setStartFeedback(
                button,
                messages[error.code] || "Anlık konum alınamadı.",
                "error"
            );
            button.disabled = false;
            button.classList.remove("is-loading");
            button.innerHTML = originalLabel;
        },
        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0,
        }
    );
}

function initializeCourierSlotStart() {
    for (const button of document.querySelectorAll("[data-kt-slot-start]")) {
        if (button.dataset.ktSlotStartReady) {
            continue;
        }
        button.dataset.ktSlotStartReady = "1";
        button.addEventListener("click", () => handleSlotStart(button));
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeCourierSlotStart, {
        once: true,
    });
} else {
    initializeCourierSlotStart();
}

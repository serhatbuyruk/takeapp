console.log("Sound Script with JS Modal");

// Modal yapılarını ve stillerini oluşturuyoruz
function createModal() {
    // Modal HTML yapısını oluştur
    const modal = document.createElement("div");
    modal.id = "myModal";
    modal.style.display = "none"; // Modal başlangıçta gizli olacak
    modal.style.position = "fixed";
    modal.style.zIndex = "1"; // Üst katmanda göster
    modal.style.left = "0";
    modal.style.top = "0";
    modal.style.width = "100%";
    modal.style.height = "100%";
    modal.style.backgroundColor = "rgba(0, 0, 0, 0.5)"; // Koyu arkaplan

    // Modal içerik kutusunu oluştur
    const modalContent = document.createElement("div");
    modalContent.style.backgroundColor = "#fff";
    modalContent.style.margin = "15% auto"; // Ortaya yerleştir
    modalContent.style.padding = "20px";
    modalContent.style.width = "30%";
    modalContent.style.textAlign = "center";

    // Modal içeriğini ekle
    const message = document.createElement("p");
    message.innerText = "Yeni Siparişiniz Var.";
    modalContent.appendChild(message);

    // Kapatma butonu oluştur
    const closeButton = document.createElement("button");
    closeButton.innerText = "Tamam";
    closeButton.style.backgroundColor = "red";
    closeButton.style.color = "white";
    closeButton.style.padding = "10px 20px";
    closeButton.style.cursor = "pointer";
    modalContent.appendChild(closeButton);

    // Kapatma butonuna tıklama işlemi
    closeButton.onclick = function () {
        modal.style.display = "none"; // Modalı kapat
        stopSound(); // Müzik durdurulacak
    };

    // Modal ve içeriğini body'ye ekle
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
}

let audio;  // Audio nesnesi globalde tanımlanıyor, böylece her yerden erişilebilir

// Ses çalma fonksiyonu
async function playSound() {
    if (!audio) {
        // Eğer audio nesnesi yoksa yeni bir ses oluştur
        audio = new Audio('/web/content/1547');
        audio.loop = true;  // Ses sürekli tekrar etsin
    }

    // Ses çalmaya başla
    try {
        await audio.play();
        console.log("Sound playing");
    } catch (error) {
        console.error("Error playing sound: ", error);
    }
}

// Ses durdurma fonksiyonu
async function stopSound() {
    if (audio) {
        // Sadece ses çalıyorsa durdur
        audio.pause();  // Müziği durdur
        audio.currentTime = 0;  // Başlangıca sar
        console.log("Sound stopped");
    }
}

// Kullanıcı "Tamam" diyene kadar sesin çalmasını sağlayan fonksiyon
async function playSoundAndShowModal() {
    // Önce ses çalmaya başla
    await playSound();

    // Modalı göster
    const modal = document.getElementById("myModal");
    modal.style.display = "block";
}

// Sayısal değeri kontrol eden ve değişim varsa ses çalan fonksiyon
let previousValue = null;  // Önceki değeri tutmak için değişken

function checkValueChange() {
    console.log("checkValueChange");

    // "Yeni Siparişler" metnine sahip div'i seçiyoruz
    var orderElement = Array.from(document.querySelectorAll('div')).find(el => el.innerText.trim() === "Yeni Siparişler");

    // Eğer element bulunduysa, üzerindeki değeri alıyoruz
    if (orderElement && orderElement.previousElementSibling) {

        var valueElement = orderElement.previousElementSibling; // Üstteki div'i al
        var currentValue = parseFloat(valueElement.innerText.trim());  // Sayısal değeri al ve sayı formatına çevir

        console.log("valueElement", valueElement);
        console.log("currentValue", currentValue);

        // Eğer önceki değer null ise, başlatmak için currentValue'yu previousValue'ya atıyoruz
        if (previousValue === null) {
            previousValue = currentValue;
        }

        // Eğer önceki değer ile şimdiki değer farklıysa ses çal
        if (previousValue !== currentValue) {
            console.log("Yeni Siparişler üzerindeki değer değişti:", currentValue);

            // Kullanıcı "Tamam" diyene kadar ses çal
            playSoundAndShowModal();

            // Yeni değeri sakla
            previousValue = currentValue;
        } else {
            console.log("Değer değişmedi.");
        }
    }
}

// Target node bulma ve MutationObserver ile DOM değişikliklerini izleme fonksiyonu
function findTargetNode() {
    var targetNode = document.querySelector('.ks_dashboard_item_main_body_l5');
    
    if (targetNode) {
        console.log("Target node bulundu:", targetNode);

        // MutationObserver ile değişiklikleri izlemeye başla
        var config = { childList: true, subtree: true };
        var observer = new MutationObserver(function(mutationsList) {
            console.log("observer func");
            mutationsList.forEach(function(mutation) {
                console.log("Mutation detected: ", mutation);
                checkValueChange();
            });
        });
        observer.observe(targetNode, config);
        return true;  // Node bulundu, aramayı durdur
    } else {
        console.log("Target node hala bulunamadı. Tekrar denenecek.");
        return false; // Node bulunamadı, aramaya devam et
    }
}

// Sayfa yüklendikten sonra her 2 saniyede bir kontrol et
window.addEventListener('load', function() {
    // Modal yapısını oluştur
    createModal();

    var checkExist = setInterval(function() {
        if (findTargetNode()) {
            clearInterval(checkExist);  // Node bulunduğunda aramayı durdur

            // Her 15 saniyede bir checkValueChange fonksiyonunu çalıştır
            setInterval(function() {
                checkValueChange();
            }, 15000);  // 15 saniye aralıkla
        }
    }, 2000);  // 2 saniyede bir targetNode'u kontrol et
});

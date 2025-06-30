document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("shareLocationButton").addEventListener("click", function (event) {
        event.preventDefault();

        const whatsappPhone = this.getAttribute("data-whatsapp-phone");
        console.log("whatsappPhone ", whatsappPhone);

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;

                    const whatsappLink = `https://wa.me/90${whatsappPhone}?text=Anlık%20konum:%20https://www.google.com/maps?q=${latitude},${longitude}`;

                    window.open(whatsappLink, "_blank");
                },
                (error) => {
                    if (error.code === error.PERMISSION_DENIED) {
                        console.error("Kullanıcı konum iznini reddetti.");
                    } else {
                        console.error("Konum bilgisi alınamadı:", error.message);
                    }
                }
            );
        } else {
            console.log("Geolocation API tarayıcınız tarafından desteklenmiyor.");
        }
    });
});
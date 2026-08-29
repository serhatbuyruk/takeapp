
// Harita ve işaretleyici fonksiyonları
function myMap() {
    // Antalya'nın koordinatları
    var antalya = { lat: 36.8969, lng: 30.7133 };

    // Harita oluşturulması
    var map = new google.maps.Map(document.getElementById('googleMap'), {
        zoom: 10,
        center: antalya
    });

    // İşaretleyici oluşturulması
    var marker = new google.maps.Marker({
        position: antalya,
        map: map,
        title: 'Antalya, Turkey'
    });
}
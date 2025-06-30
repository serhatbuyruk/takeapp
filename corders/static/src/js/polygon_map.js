odoo.define('polygon_map.drawing_tool', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    const rpc = require('web.rpc');
    const Dialog = require('web.Dialog');

    function loadGoogleMapsAPI() {
        return new Promise((resolve, reject) => {
            if (typeof google !== 'undefined' && google.maps && google.maps.drawing) {
                resolve();
                return;
            }

            if (document.getElementById('google-maps-script')) {
                const interval = setInterval(() => {
                    if (google && google.maps && google.maps.drawing) {
                        clearInterval(interval);
                        resolve();
                    }
                }, 200);
                return;
            }

            const script = document.createElement('script');
            script.id = 'google-maps-script';
            script.src = 'https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=drawing';
            script.async = true;
            script.defer = true;

            script.onload = resolve;
            script.onerror = reject;

            document.head.appendChild(script);
        });
    }

    publicWidget.registry.PolygonDrawingMap = publicWidget.Widget.extend({
        selector: '#map_canvas',

        start: function () {
            const self = this;
            loadGoogleMapsAPI().then(() => {
                console.log('✅ Google Maps API başarıyla yüklendi.');
                self._initMap();
            }).catch((err) => {
                console.error('❌ Google Maps API yüklenemedi:', err);
            });
        },

        _initMap: function () {
            const style = [
                { featureType: "administrative.neighborhood", elementType: "labels", stylers: [{ visibility: "off" }] },
                { featureType: "poi", elementType: "labels", stylers: [{ visibility: "off" }] },
                { featureType: "road", elementType: "labels", stylers: [{ visibility: "off" }] },
                { featureType: "road.highway", elementType: "all", stylers: [{ visibility: "simplified" }] }
            ];

            let polygonArray = [];
            let lastPolygonCoords = '';

            const map = new google.maps.Map(document.getElementById("map_canvas"), {
                center: { lat: 41.0082, lng: 28.9784 },
                zoom: 13,
                scrollwheel: false,
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                styles: style
            });

            // Daha önce kaydedilen poligonları çiz
            rpc.query({
                model: 'zones.profile',
                method: 'search_read',
                args: [[], ['polygons_char', 'out_of_area', 'is_active']]
            }).then(records => {
                records.forEach(record => {
                    try {
                        const coords = eval(record.polygons_char);
                        const strokeColor = !record.is_active ? '#9E9E9E' : (record.out_of_area ? '#D32F2F' : '#2962FF');
                        const fillColor = !record.is_active ? '#E0E0E0' : (record.out_of_area ? '#FFCDD2' : '#64B5F6');
                        const polygon = new google.maps.Polygon({
                            paths: coords,
                            strokeColor: strokeColor,
                            strokeOpacity: 0.8,
                            strokeWeight: 2,
                            fillColor: fillColor,
                            fillOpacity: 0.2,
                            map: map
                        });
                        polygonArray.push(polygon);
                    } catch (e) {
                        console.warn('Geçersiz poligon verisi:', record.polygons_char);
                    }
                });
            });

            const drawingManager = new google.maps.drawing.DrawingManager({
                drawingMode: google.maps.drawing.OverlayType.POLYGON,
                drawingControl: true,
                drawingControlOptions: {
                    position: google.maps.ControlPosition.TOP_CENTER,
                    drawingModes: ['polygon']
                },
                polygonOptions: {
                    strokeColor: '#2962FF',
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: '#64B5F6',
                    fillOpacity: 0.2,
                    editable: true,
                    zIndex: 1
                }
            });

            drawingManager.setMap(map);

            function updatePolygon(polygon) {
                const info = document.getElementById("info");
                const coords = [];
                polygon.getPath().forEach(pt => {
                    coords.push({ lat: pt.lat(), lng: pt.lng() });
                });
                lastPolygonCoords = JSON.stringify(coords);
                info.innerHTML = `Copy this polygon path:<br><br>${lastPolygonCoords}<br><br>`;
            }

            google.maps.event.addListener(drawingManager, 'polygoncomplete', function (polygon) {
                polygonArray.push(polygon);
                updatePolygon(polygon);

                polygon.getPaths().forEach(path => {
                    google.maps.event.addListener(path, 'insert_at', () => updatePolygon(polygon));
                    google.maps.event.addListener(path, 'remove_at', () => updatePolygon(polygon));
                    google.maps.event.addListener(path, 'set_at', () => updatePolygon(polygon));
                });

                new Dialog(this, {
                    title: "Poligon Bilgilerini Kaydet",
                    size: 'medium',
                    buttons: [
                        {
                            text: "Kaydet",
                            classes: 'btn-primary',
                            close: true,
                            click: function (ev) {
                                ev.preventDefault();
                                const name = document.getElementById("polygon_name_input").value;
                                const basePrice = parseFloat(document.getElementById("polygon_base_price_input").value);
                                const perMilePrice = parseFloat(document.getElementById("polygon_per_mile_input").value);
                                const outOfArea = document.getElementById("polygon_out_of_area_input").checked;

                                if (name && lastPolygonCoords) {
                                    rpc.query({
                                        model: 'zones.profile',
                                        method: 'create',
                                        args: [{
                                            name: name,
                                            polygons_char: lastPolygonCoords,
                                            base_price: basePrice,
                                            per_mile_price: perMilePrice,
                                            out_of_area: outOfArea
                                        }]
                                    }).then(() => {
                                        console.log('📍 Poligon başarıyla kaydedildi');
                                        alert("Poligon başarıyla kaydedildi!");
                                    }).catch((error) => {
                                        console.error("Poligon kaydedilemedi:", error);
                                        alert("Bir hata oluştu. Lütfen tekrar deneyin.");
                                    });
                                }
                            }
                        },
                        { text: "İptal", close: true }
                    ],
                    $content: $(
                        `<div class="form-group">
                            <label>Poligon Adı:</label>
                            <input type="text" id="polygon_name_input" class="form-control" placeholder="Bölge ismi"/>
                            <label class="mt-2">Başlangıç Ücreti (Base Price):</label>
                            <input type="number" id="polygon_base_price_input" class="form-control" placeholder="Örn: 10.00" step="0.01"/>
                            <label class="mt-2">Mil Başı Ücret (Per Mile Price):</label>
                            <input type="number" id="polygon_per_mile_input" class="form-control" placeholder="Örn: 2.50" step="0.01"/>
                            <div class="form-check mt-2">
                                <input type="checkbox" class="form-check-input" id="polygon_out_of_area_input"/>
                                <label class="form-check-label" for="polygon_out_of_area_input">Servis dışı alan mı?</label>
                            </div>
                        </div>`
                    )
                }).open();
            });

            window.removeOverlay = function () {
                polygonArray.forEach(p => p.setMap(null));
                polygonArray = [];
                const info = document.getElementById("info");
                if (info) {
                    info.innerText = "Click to draw a polygon";
                }
            };
        }
    });
});

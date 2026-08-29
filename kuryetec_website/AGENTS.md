# Kuryetec Website — AI Geliştirme Rehberi

Bu dosya `kuryetec_website` modülünde çalışan geliştirici ve yapay zekâ araçları için kalıcı bağlamdır. Modül, daha önce Odoo Website/Technical ekranından elle oluşturulmuş Kuryetec sayfalarını, menüleri ve ekleri kodun kontrolüne alır. Kod artık kaynak gerçektir; canlı Website editöründe kalıcı tasarım değişikliği yapmayın.

## Güncel sistem özeti — 31 Temmuz 2026

- Canlı sürüm: `16.0.1.11.9`
- Bu modül sunum katmanıdır. Sipariş mutation'ı için
  `../corders/AGENTS.md`, slot/mutabakat için `../slots/AGENTS.md`,
  bildirim için `../notifier/AGENTS.md` dosyasını da okuyun.
- Admin dashboard bu dört ana modülden ayrı `slot_dashboard` modülündedir;
  website içine OWL dashboard kodu eklemeyin.
- `views/website_pages.xml` yaklaşık 6000 satırlık legacy ve yeni blokların
  birlikte bulunduğu büyük bir dosyadır. Route/XML ID ile hedefi bulmadan
  geniş çaplı formatlama veya mekanik yeniden yazım yapmayın.
- Teknik kodda `slot` adları geriye uyumluluk için korunur; kurye ve admin
  ekranlarında kullanıcıya görünen karşılık “Vardiya”dır.

Gemini/Codex başlangıç sırası: ilgili route/XML ID'yi `rg` ile bul; QWeb
butonunun çağırdığı controller/model metodunu ayrıca oku; form action,
parametre ve state koşullarını not et; yalnız tasarım isteniyorsa domain ve
mutation davranışını değiştirme; Website editöründe kalıcı düzeltme yapma.

## Modülün görevi

- Kurye mobil web uygulamasının QWeb sayfalarını sağlar.
- Website menülerini, anasayfayı ve görünürlük ayarlarını koddan yönetir.
- Tasarım CSS/JS dosyalarını ve eski `ir.attachment` varlıklarını modül içinde taşır.
- Önceden DB'de bulunan sayfa/view/menu kayıtlarını external ID'lerle sahiplenir.
- `corders`, `slots` ve `notifier` verisini görüntüler; iş mutation'ları ilgili Python controller'larına bırakır.

- Manifest: `__manifest__.py`
- Sayfalar: `views/website_pages.xml`
- Website/menu yapılandırması: `data/website_configuration.xml`
- Mevcut kayıtları sahiplenme hook'u: `hooks.py`
- CSS: `static/src/css/`
- JavaScript: `static/src/js/`
- Taşınmış ekler: `static/src/attachments/`

## Modüller arası sınırlar

- `corders`: siparişler, kurye durum route'ları, ödeme ve dış sistem işlemleri.
- `slots`: aktif/yaklaşan slot, kurye satırı ve çalışma saatleri.
- `notifier`: bildirim gönderimi.
- `kuryetec_website`: sunum, linkler, kullanıcı etkileşimi ve mobil tasarım.

QWeb içinde büyük `write/create/search` iş kuralları oluşturmayın. Buton mevcut controller route'una gider; yetki/doğrulama ve mutation Python tarafında yapılır. Yeni backend davranışı gerekiyorsa doğru modüle model/controller metodu ekleyin.

## Kod sahipliği ve mevcut DB kayıtları

`hooks.py` içindeki `pre_init_hook`, Website editöründen daha önce oluşturulmuş kayıtları bilinen DB ID'leriyle modül external ID'lerine bağlar ve `noupdate=False` yapar. Bu hook yalnızca ilk kurulumdan önce çalışır; normal `-u kuryetec_website` upgrade'inde tekrar çalışmaz.

Sonuç:

- Sayfa, view ve menü değişiklikleri XML/CSS/JS'den yapılmalıdır.
- Modül upgrade'i kodu veritabanına uygular ve UI'daki manuel değişiklikleri ezebilir.
- Yeni bir DB'ye kurulumda sabit eski ID'lerin bulunmayabileceğini hesaba katın.
- External ID'leri veya eski sahiplenme mantığını migration planı olmadan değiştirmeyin.

## Ana sayfalar

`views/website_pages.xml` büyük ve çok sayfalı bir dosyadır. Değişiklikten önce route veya XML ID ile hedef bloğu `rg` kullanarak bulun. Önemli sayfalar:

- `/anasayfa`: karşılama sayfası
- `/kurye-anasayfa`: kurye çalışma durumu ve aktif teslimatlar
- `/musait-saatler`: kayıtlı/planlanan slotlar
- `/gecmis`: teslimat geçmişi
- `/harita`
- `/odemeler`
- `/mola`
- `/destek-merkezi`
- `/duyurular`
- `/bildirimler`
- `/paket-sayilari`
- `/yeni-siparisler`
- Profil, gizlilik politikası ve açık rıza sayfaları

Menüler `data/website_configuration.xml` içindedir. Menü sırası, adı, route'u ve görünürlüğü burada değiştirilir. Anasayfa yönlendirmesi ve `/home` davranışı da bu yapılandırmayla ilişkilidir.

## Kurye ana sayfası

`/kurye-anasayfa` mobil uygulama benzeri arayüzdür:

- Kurye selamlama ve online durumu
- Çalışma durumu
- Mevcut/yaklaşan slot
- Kalan mola
- Aktif teslimatlar ve adım butonları
- Mobil alt navigasyon

Kurye slot saatini gösterirken şu öncelik korunmalıdır:

1. Kurye satırında hem `kurye_start_date` hem `kurye_end_date` varsa bunlar.
2. Aksi halde ana slotun `start_date` / `end_date` değerleri.

Bu mantık `/musait-saatler` ile tutarlı olmalıdır. “Yaklaşan slotlar” alanı aktif slotu yaklaşanmış gibi çoğaltmamalı; zaman ve aktiflik domain'i dikkatle korunmalıdır.

`/musait-saatler` kayıtlarını ve takvim noktalarını ana slotun ham UTC
başlangıcına göre aramaz; `skurye.profile.lines.get_courier_day_slots()`
metodunu kullanır. Böylece geceyi aşan Excel vardiyası kurye satırındaki
`shift_plan_date` gününde görünür ve UTC farkıyla önceki güne kaymaz.

Aktif teslimat kartlarının form action'ları `corders` route'larına gider. Görsel düzenleme yaparken `name`, `action`, query parametreleri, sipariş ID'si, CSRF davranışı ve durum koşullarını bozmayın.

“Vardiyayı Başlat” butonu `static/src/js/courier_slot_start.js` üzerinden her tıklamada taze telefon konumu ister ve teknik olarak adı korunan `POST /courier/slot/start` route'una gönderir. Cache'lenmiş konuma güvenmez. Butonun veri niteliğini veya asset kaydını kaldırmayın; mesafe kararı `slots` modelinde sunucu tarafında verilir.

Mola özelliği geçici olarak kurye menüsü ve ana sayfadaki yeni mola
başlatma aksiyonundan gizlidir. `/mola` route'u ve backend iş mantığı
silinmemiştir. Halihazırda molada kalmış kuryenin sıkışmaması için ana
sayfadaki koşullu “Devam Et” aksiyonu korunur.

Kurye sabit kuryeli bir slotu başlattıktan sonra “Slottaki İşi Sonlandır”
butonu gösterilmez; vardiya bitişi cron tarafından yönetilir. Bölge
tanımlamalı slotlarda mevcut manuel sonlandırma görünürlüğü korunur.

Çalışma durumu kartı `details/summary` yapısıyla açılıp kapanır. Kurye aktif
slot satırını henüz başlatmadıysa varsayılan açık; `start_date` doluysa
varsayılan kapalı gelir. Dropdown davranışı iş butonlarının koşullarını
değiştirmemelidir.

Ana sayfadaki “aktif paketiniz var” bağlantısı yalnız oturumdaki kuryeye
atanmış, final/iptal olmamış siparişlerin sayısını göstermelidir. Restoranın
tüm eski/boşta paketlerini bu sayıya katmayın. `/yeni-siparisler` sayfası da
aynı kurye sahipliği domain'ini korumalıdır; butonu geri getirirken tüm
restoran siparişlerini açan eski sorguyu geri getirmeyin.

### Paket sayısı zorunlu ekranı

`static/src/js/package_reconciliation.js`, oturumdaki kurye için
`/courier/package-reconciliation/pending` route'unu sayfa açılışında ve 30
saniyede bir kontrol eder. Çalışılmış sabit slotun etkin bitiş zamanı dolmuş
ve beyan verilmemişse kapatılamayan mobil form tüm arayüzü örter. Gönderim
`/courier/package-reconciliation/submit` üzerinden yapılır; güvenlik ve iş
kuralının kaynağı `slots` modelidir.

Kurye bir kez gönderdiği sayıyı revize edemez. Sonuçları
`/paket-sayilari` sayfasında restoran onayı bekliyor, onaylandı, reddedildi
veya otomatik onaylandı durumlarıyla görür. Popup'ın z-index, modal
zorunluluğu veya periyodik kontrolü kaldırılırsa kurye slot bitişinde beyanı
atlayabilir. Geçmiş satırları topluca zorunlu hale getirmeyin.

## Ödemeler sayfası

`/odemeler` artık `controllers/payments.py` tarafından hazırlanır; ağır hesapları tekrar QWeb içine taşımayın. Route yalnız oturumdaki kuryeyi kullanır ve query string ile gönderilen başka bir `partner_id` değerini dikkate almaz.

Sayfa aktiftir:

- `website_page_100.is_published=True`, `website_indexed=True`
- `menu_payments.parent_id=kuryetec_website.menu_root`
- Controller yayın durumu kapatılırsa doğrudan route'a `404` döndürür.

Filtreler:

- Dönem: `week:<offset>` veya `month:<offset>`
- Restoran onayı: `all`, `pending`, `approved`, `rejected`

Offset ve seçimler sunucuda whitelist ile doğrulanır. Ödeme durumu filtresi
kaldırılmıştır; `payment_status` query parametresi ürün davranışı değildir.
Sabit slot beyanlarında paket, saat, km, promosyon ve yüzde kalemleri
mutabakat değerlerinden gelir. Bekleyen tutar görünür fakat ayrı gösterilir;
onaylanan/otomatik onaylanan tutar kesinleşmiş toplama girer, reddedilen
tutar görünür toplamda sayılmaz. Mutabakata giren siparişler ayrıca bağımsız
sipariş kazancı olarak toplanmaz; bu çift sayımı önler.
Kurye garanti paket tabanı devreye girdiyse ödeme kartı gerçek beyanı ve
`mutabakat_hesaplanan_paket_sayisi` ücretlendirilen adedini birlikte gösterir;
toplamlar ücretlendirilen adet üzerinden kaydedilmiş mutabakat tutarlarından
gelir.

Legacy mutabakat dışı satırlar ve teslim edilmiş bağımsız siparişler mevcut
uyumluluk hesabında ayrıca yer alır. Dönem, mutabakat satırlarında bugün
parent slot bitişine göre seçilir. Para hesabını QWeb'e taşımayın.

HTTP regresyon testleri `tests/test_payments.py` içindedir; fakat dosyadaki
`payment_status=paid/not_paid` beklentileri kaldırılmış filtreye göre
eskidir. Testleri güncel restoran onayı filtrelerine çevirmeden bu dosyayı
yeşil/güncel güvence kabul etmeyin.

Hakedişin kaynak finansal borçları (tarife snapshot'ı, parent slot saat
penceresi ve onay durumunun admin raporuna etkisi)
`../slots/AGENTS.md` içinde belgelenmiştir.

## Geçmiş ve karşılama

`/gecmis` sayfası mobil kartlar, durum/ödeme özetleri ve alt navigasyon kullanır. Filtre/domain değişikliği görünüm değişikliği değildir; iş gereği olmadan teslim edilen/iptal edilen kayıt kapsamını değiştirmeyin.

Karşılama sayfası `welcome_home.css`, geçmiş `history_page.css`, kurye ana sayfası `courier_home.css` ile özelleştirilir. Pil seviyesi uyarısı `remove_battery_warning.js` ile kaldırılır. Eski markup değişirse JS selector'ünün hâlâ hedefi bulduğunu doğrulayın.

Menüdeki Mola, Destek Merkezi, Yetkili Firma, Duyurular, Bildirimler ile yasal metin sayfaları ortak `mobile_pages.css` tasarım sistemini kullanır. Bu sayfalarda `.kt-mobile-page`, `.kt-mobile-shell`, `.kt-mobile-header` ve `.kt-mobile-*` bileşenlerini koruyun. Görsel değişiklik yaparken:

- Mola sayfasındaki aktif sipariş aramasını ve `/mola_active` / `/mola_deactive` koşullarını değiştirmeyin.
- Yetkili Firma telefon bağlantısını yalnız firma ve telefon bilgisi varken gösterin.
- Bildirimler sayfası `controllers/notifications.py` üzerinden `notifier.delivery.log` kayıtlarını yalnız oturumdaki partner, son 12 saat ve en fazla 50 kayıt olarak okur. Bu partner sınırını kaldırmayın.
- Upgrade öncesi manuel kullanıcı bildirimleri `notifier.profile.x_user` üzerinden geçici fallback ile gösterilir; yeni gönderimler teslimat günlüğünden gelir.
- Duyuru metinlerinin operasyonel anlamını yalnız tasarım amacıyla değiştirmeyin.
- Yasal metinlerin içeriğini hukuki onay olmadan yeniden yazmayın; sadece okunabilirlik stillerini değiştirin.

## CSS ve mobil tasarım sözleşmesi

Yeni kurye ana sayfa bileşenlerinde mevcut `.kt-*` sınıf ailesini kullanın. Tasarım:

- Önce mobil ekran için hazırlanır.
- En dar cihazlarda yatay taşma üretmemelidir.
- Dokunma hedefleri yeterince büyük olmalıdır.
- Alt navigasyon fixed/sticky ise içerik altında güvenli boşluk bırakmalıdır.
- Durum yalnızca renkle anlatılmamalıdır.
- Odoo'nun genel `.container`, `.row`, `.card`, `.btn` sınıflarını global olarak ezmeyin.
- Sayfaya özel üst kapsayıcı altında selector kullanın.

Özellikle `<=575px` breakpoint'ini ve yaklaşık 360–430 px genişlikleri kontrol edin. Masaüstünde de form/listelerin kullanılabilir kaldığını doğrulayın.

Backend One2many kilometre tablolarının tam geniş görünümü ilgili `corders`/`slots` view'ları ve CSS'iyle sağlanır. Website CSS'ini backend form düzeltmesi için kullanmayın.

## Statik ekler

Eski `ir.attachment` dosyaları `static/src/attachments/` altında tutulur; eşleştirme `index.json` içindedir.

- Yeni görseli modül dizinine ekleyin ve `/kuryetec_website/static/...` yolu ile referanslayın.
- DB'ye elle attachment yükleyip onu tek kaynak yapmayın.
- Kullanılmayan dosyayı silmeden önce XML/CSS/JS ve `index.json` referanslarını arayın.
- Büyük JPG/PNG/GIF/APK/GLB dosyalarının mobil yükleme maliyetini değerlendirin.
- Görsel boyutunu yalnız CSS ile küçültmek ağ transferini küçültmez; uygun optimize edilmiş dosya üretin.

## QWeb ve veri sorguları

QWeb döngüsünün içinde aynı modele tekrar `search` yapmayın. Mümkünse controller/model önceden gerekli recordset'i hazırlasın. Eski sayfalar doğrudan `request.env[...]` sorguları içeriyorsa yeni sorgu eklemeden önce toplam sorgu sayısını değerlendirin.

Güncel büyük XML'de onlarca doğrudan ORM araması ve kullanılmayan eski
sayfa blokları vardır. Yeni özellikte QWeb araması eklemek yerine küçük bir
authenticated controller/model servisiyle değerleri önceden hazırlayın.
Legacy başka-proje (`hbookings`, cihaz/NFC vb.) bloklarını çalışıyor
varsaymayın; erişim ve DB kanıtı olmadan genişletmeyin.

- Domain'leri indexed durum, ilişki ve tarih alanlarıyla daraltın.
- Sınırsız geçmiş kaydı render etmeyin; limit veya pagination kullanın.
- Her sipariş kartında yeniden restoran/partner aramayın.
- External API çağrısını hiçbir zaman template render'ı sırasında yapmayın.

## Saat dilimi

Odoo Datetime alanları UTC saklanır. Eski şablonlarda Türkiye saati için elle `+3` eklenen ifadeler vardır. Yeni kodda bağlama duyarlı dönüşüm tercih edilir, fakat tek bir ekranı değiştirip aynı değeri iki kez çevirmeyin. Slot zamanlarıyla ilgili değişiklikte:

- `slots.profile` ana zamanını,
- `skurye.profile.lines` kurye özel zamanını,
- `/kurye-anasayfa`,
- `/musait-saatler`,
- cron aktiflik hesaplarını

birlikte kontrol edin.

`/musait-saatler` içinde hâlâ elle `+3`, `+27`, `+51` gibi dönüşümler
bulunur. Refactor sırasında kullanıcı timezone'u, UTC saklama ve Excel
importunun yerel gün sınırı için tek ortak dönüşüm kullanın; kısmi
düzeltmeyle bir ekranı üç saat kaydırmayın.

## Güvenlik ve erişim davranışı

Bu rehberin ana odağı kararlılık ve performanstır; yine de mevcut route görünürlüğünü yanlışlıkla genişletmeyin. Public ve authenticated sayfaları birbirine çevirmeden önce ilgili menu/view `groups`, website publish ve controller `auth` değerlerini inceleyin. Template içindeki `sudo()` kullanımını çoğaltmayın.

Butonun yalnız doğru kuryeye görünmesi sunucu yetkilendirmesi değildir.
`corders` içindeki bazı state-changing GET route'ları sipariş-kurye
sahipliğini eksik doğrular. Yeni UI aksiyonunda oturum partnerini
controller'da doğrulayın; URL'den gelen kullanıcı ID'sine güvenmeyin.

## Test ve doğrulama

Bu modülde tam tarayıcı/E2E paketi yoktur; `/odemeler` için HTTP testleri vardır. Her değişiklikte en az:

1. `website_pages.xml` ve `website_configuration.xml` dosyalarını XML parser ile doğrulayın.
2. Manifest asset yollarının var olduğunu kontrol edin.
3. Modülü upgrade edin ve loglarda QWeb/XPath/asset hatası arayın.
4. Public sayfalarda HTTP 200 kontrolü yapın.
5. Yetkili kurye hesabıyla `/kurye-anasayfa`, `/musait-saatler` ve değişen sayfayı açın.
6. 360/390/430 px mobil genişlikleri ile masaüstünü kontrol edin.
7. Butonların yalnız görünümünü değil gerçek controller isteğini doğrulayın.
8. Tarayıcı cache/asset bundle nedeniyle eski CSS görülürse yeni gizli pencere veya asset debug ile karşılaştırın.

Kurye verisiyle test ederken üretim sipariş durumunu yanlışlıkla değiştirmeyin. Mutation testi için geçici DB veya kontrollü test kaydı kullanın.

Mevcut test sayıları: bildirim `1`, paket popup/controller `2`, ödemeler `5`.
Ödemeler testlerinin filtre beklentisi güncel değildir. Tam mobil tarayıcı,
konum izni, fixed alt navigasyon, asset cache ve 360–430 px E2E kapsamı
yoktur; bunları ayrıca manuel regresyon olarak kontrol edin.

## Değişiklik kontrol listesi

1. Route/XML ID ile doğru template bloğunu bulun.
2. Form action, field name, ID ve koşullu QWeb ifadelerini not edin.
3. Yalnız markup/stil değişiyorsa domain ve iş akışına dokunmayın.
4. Yeni asset'i manifeste ekleyin ve manifest sürümünü artırın.
5. XML, dosya yolu ve responsive görünümü doğrulayın.
6. Upgrade sonrası `ir.ui.view` derleme hatalarını ve browser console'u kontrol edin.

## Dağıtım

Kaynak dizini `/odoo/odoo16/kuryetec-custom-addons`; eski `/odoo/odoo16/odoo-custom-addons` kopyasını kullanmayın.

- Config: `/etc/odoo16-kuryetec.conf`
- Database: `kuryetec`
- Service: `odoo16-kuryetec.service`
- Log: `/var/log/odoo/odoo16-kuryetec.log`
- HTTP port: `12791`

Kod/XML/CSS/JS/attachment değişikliğinde manifest sürümünü artırın:

```bash
systemctl stop odoo16-kuryetec.service
sudo -u odoo /odoo/odoo16/odoo-venv/bin/python3 /var/lib/odoo/odoo-bin \
  -c /etc/odoo16-kuryetec.conf -d kuryetec -u kuryetec_website \
  --stop-after-init --no-http
systemctl start odoo16-kuryetec.service
```

Ardından servis durumu, Odoo logu, HTTP yanıtı ve mobil görünüm kontrol edilir. Sadece `.md` dokümantasyonu değiştiyse restart, upgrade veya asset temizliği gerekmez.

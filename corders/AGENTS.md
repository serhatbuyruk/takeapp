# Corders — AI Geliştirme Rehberi

Bu dosya `corders` modülünde çalışan geliştirici ve yapay zekâ araçları için kalıcı bağlamdır. Bu dizin altındaki değişikliklerde bu kuralları izle. Hedef çalışan sipariş akışını korumak, gereksiz sorgu ve dış servis beklemelerini önlemek, Odoo 16 standartlarında değişiklik yapmaktır.

## Güncel sistem özeti — 31 Temmuz 2026

- Canlı sürüm: `16.0.2.3.4`
- Canlı kaynak: `/odoo/odoo16/kuryetec-custom-addons`
- Atama için `../slots/AGENTS.md`, kurye arayüzü için
  `../kuryetec_website/AGENTS.md`, bildirim için `../notifier/AGENTS.md`,
  vardiya importu ve yönetici raporları için
  `../slot_dashboard/AGENTS.md` dosyasını da okuyun.
- Kod tabanında şu anda Git deposu yoktur. Yetki verildiyse yeni
  geliştirmeden önce özel bir sürüm kontrolü ve geri dönüş süreci oluşturmak
  ciddi şekilde önerilir. Eski addon kopyasını kaynak gerçek kabul etmeyin.
- Bu belge mevcut davranış ile hedef davranışı ayırır. “Bilinen borç” olarak
  işaretlenen noktaları kaynakta görülmeden düzeltilmiş varsaymayın.

Gemini/Codex başlangıç sırası: önce en yakın `AGENTS.md` dosyasını tamamen
oku; manifest bağımlılıklarını ve veri yükleme sırasını kontrol et; Python
çağrılarını `rg` ile XML `code` alanları dahil tüm addonlarda ara; yalnız
sonra değişiklik yap. Canlı DB'deki action/view kaydını elle değiştirip kodu
geride bırakma.

## Modülün görevi

`corders`, Kuryetec'in sipariş ve kurye operasyonlarının ana veri katmanıdır:

- Siparişleri `corders.profile` modelinde tutar.
- Restoran, kurye ve firma ayarları için `res.partner` modelini genişletir.
- Kurye mobil ekranındaki durum değiştirme HTTP route'larını sağlar.
- Yeppos/Tazeyo, Sepettakip, Pagate ve Adisyo entegrasyonlarını yürütür.
- Sipariş durumları, ödeme/kurye hakedişi ve teknik otomasyonları yönetir.
- Otomatik kurye atamasını kendisi çalıştırır; algoritmanın asıl uygulaması bağımlı `slots` modülündedir.

- Manifest: `__manifest__.py`
- Ana modeller: `models/corders.py`, `models/respartner_inherit.py`
- HTTP controller: `controllers/controllers.py`
- Teknik aksiyonlar: `data/technical_actions.xml`, `data/courier_assignment_action.xml`
- Backend görünümleri: `views/`
- Testler: `tests/`

## Modüller arası sınırlar

- `corders`: sipariş, restoran/kurye profili, teslimat route'ları ve dış sipariş servisleri.
- `slots`: slotlar, vardiya satırları, kapasite ve otomatik kurye atama motoru.
- `notifier`: SMS, push ve sesli arama gönderimi.
- `kuryetec_website`: QWeb sayfaları, menüler ve görsel varlıklar.
- `slot_dashboard`: admin operasyon dashboardu, Excel vardiya importu ve
  kurye hakediş raporu. Ayrı modüldür fakat ana modelleri kullanır.

`operation_dashboard_enabled` alanı `res.partner` üzerinde görünse de
`corders` tarafından değil `slot_dashboard` tarafından eklenir. Aynı alanı
bu modülde yeniden tanımlamayın.

İş kuralını QWeb şablonuna taşımayın. Mobil ekrandaki butonlar bu modülün route'larını çağırabilir; asıl doğrulama ve mutation Python tarafında kalmalıdır.

`corders` içindeki bazı otomasyonlar `notifier.profile` çağırır fakat manifest doğrudan `notifier` bağımlılığı ilan etmez. Canlı kurulumda dört modül beraber vardır. Yeni/bağımsız kurulum senaryosunda bu örtük bağımlılığı özellikle kontrol edin; sessizce kaldırmayın.

## Temel veri modeli

### `corders.profile`

Ana sipariş kaydıdır ve `mail.thread`/`mail.activity.mixin` davranışlarını kullanır. Kritik alan grupları:

- Restoran, müşteri, adres ve teslimat koordinatları.
- Atanan kurye ve kurye telefonu.
- Sipariş tutarı, ödeme tipi ve kurye hakedişi.
- Restoran sipariş durumu: `onay_bekliyor`, `onaylandi`, `hazirlaniyor`, `yola_cikti`, `teslim_edildi`, `iptal_edildi`.
- Kurye akışı: yönlendirme, onay, restorana ulaşma, teslim alma, teslim etme ve iptal durumları.
- Dış sistem sipariş kimlikleri ve entegrasyon alanları.
- Atama senaryosu, mesafe ve yön bilgileri.

Durum selection anahtarlarını değiştirmek veri migrasyonu ve tüm otomasyonların birlikte güncellenmesini gerektirir. Sadece etiketi değiştirmek gerekiyorsa teknik anahtarı sabit tutun.

### `res.partner` genişletmeleri

Partner kaydı restoran, kurye veya kurye firması rolünde kullanılabilir. Burada:

- Rol ve firma ilişkileri,
- Restoran çalışma gün/saatleri,
- Sabit kurye tanımları,
- Koordinatlar ve adres,
- Kurye çalışma/mola durumu,
- OneSignal `player_id`,
- Sabit-kurye modelinin kurye ve platform kilometre ücret aralıkları

bulunur.

Sabit kurye modelinde iki bağımsız tarife vardır:

- Kuryeye ödenecek ücret: `corders.restoran.km.ucret.araligi`, `km_ucret_aralik_ids`, `get_distance_fee(distance_meters)`.
- Restoranın platforma ödeyeceği ücret: `corders.restoran.platform.km.ucret.araligi`, `platform_km_ucret_aralik_ids`, `get_platform_distance_fee(distance_meters)`.

Restoran kartında iki bağımsız garanti tabanı vardır. `garanti_paket_sayisi`
kuryenin paket hakedişinde, `restoran_garanti_paket_sayisi` restoranın
platform borcunda kullanılır. Değer `0` ise garanti kapalıdır; pozitifse
ücretlendirilen adet `max(gerçek/beyan, garanti)` olur. İki garanti birbirinin
yerine kullanılmaz ve negatif değerler constraint ile engellenir.

Her iki metot mesafeyi metre kabul eder. Aralıklar başlangıç dahil, bitiş hariç `[başlangıç, bitiş)` çalışır; eşleşmeyen mesafe veya hiç tarife olmaması `0` döndürür. Ücret kilometre başına çarpan değil, aralığın sabit ücretidir. Çakışan/geçersiz aralıklar constraint ile engellenmelidir. Eski `restoran_kmlik_ucret` alanı veri uyumluluğu için durur fakat yeni platform borcu hesabının kaynağı değildir.

Sabit kurye restoranlarında `sabit_slot_baslatma_yaricapi_m`, kuryenin slotu restoran koordinatından en fazla kaç metre uzakta başlatabileceğini belirler. Varsayılan `500` metredir ve değer pozitif olmalıdır.

Sabit kurye tipindeki restoran `kuryeler` alanı boşken kaydedilebilir.
Bu durumda günlük otomatik slot üretimi restoranı atlar. Operasyon vardiyası
`slot_dashboard` Excel aktarımıyla yüklenirse restoran günü yerel günün
tamamını kapsayan sabit slot olarak açılır. Kurye vardiyaları Excel'deki
saatleri taşır; başlangıç `00:00` ise `00:00:01`, bitiş `00:00` ise aynı gün
`23:59:59` kabul edilir. Dosyadaki kuryeler yalnız o slotun vardiya
satırlarına eklenir, restoranın kalıcı `Sabit Kuryeler` listesine yazılmaz.

İki plan kaynağı hâlâ aktiftir: `slots` içindeki `cron_57`, restoranın
haftalık çalışma ve `kuryeler` ayarından günlük sabit slot üretebilir;
`slot_dashboard` ise Excel'den sabit slot oluşturur/günceller. Her restoran
için hangi kaynağın kullanılacağı net olmalıdır. Excel ile yönetilen
restoranda kalıcı `kuryeler` listesini boş bırakmak eski cron'un ikinci plan
üretmesini önler.

## Sipariş ve teslimat akışı

Kurye uygulamasının başlıca route'ları `controllers/controllers.py` içindedir:

- Çalışma/mola: `/mola_active`, `/mola_deactive`, `/available`, `/busy`
- Kurye sipariş adımları: `/kurye/onay`, `/kurye/restorana-ulasti`, `/kurye/siparisi-teslim-al`, `/kurye/siparisi-teslim-et`
- Konum: `/update_location` ve dış uygulama konum/player-id çağrıları
- Nakit/kredi ödeme aksiyonları
- Pagate, Sepettakip ve Yeppos POS callback'leri

Teslim etme route'unda yerel durum önce kaydedilir ve dış servis hataları
olabildiğince yerel teslimatı HTTP 500'e çevirmeden loglanır. Bu dayanıklılık
eski ara-adım route'larının tamamında aynı seviyede değildir. Yeni
entegrasyon eklerken “yerel işlem başarılı, entegrasyon hatası loglanır”
ilkesini açıkça uygulayın.

### Controller bütünlüğüyle ilgili bilinen borç

Kurye sipariş/ödeme route'larının bir bölümü state değiştiren `GET`
istekleridir ve `sudo()` kullanır. Çoğu URL'deki `current_user_id` ile
oturumu karşılaştırır; fakat siparişin gerçekten
`request.env.user.partner_id` kuryesine atanmış olduğunu her route'ta
yeniden doğrulamaz. `/kurye/restorana-ulasti` içinde bağlantılı siparişlere
dokunan kodun bir bölümü oturum kontrolünden önce çalışır.

- Siparişi bulup `order.kurye == request.env.user.partner_id` doğrulamasını
  mutation'dan önce yapın.
- Yeni state-changing işlemleri mümkünse `POST` ve CSRF korumalı tasarlayın.
- Mevcut QWeb URL sözleşmesini migration olmadan tek taraflı kırmayın.
- Bu borcu yeni route'lara kopyalamayın.

`/busy` route'u oturumdaki kuryeyi esas alır. Kurye başlamış ve etkin bir
sabit slot içindeyken bu route durumunu `mesgul` yapmamalıdır; eski önbellek
veya yanlışlıkla açılan bağlantı sabit vardiyayı erken sonlandıramaz. Bölge
slotundaki eski manuel sonlandırma davranışı korunur.

Adisyo taraması eksik kimlik bilgisine sahip restoranları atlar. Ağ hataları tüm cron transaction'ını düşürmemelidir.

## Otomatik kurye atama

Sipariş oluşturma otomasyonu XML kimliği `automation_21` olup `data/courier_assignment_action.xml` tarafından `prepare_and_auto_assign_courier()` çağıracak şekilde güncellenir. Metot `slots` modülünün `corders.profile` inheritance'ından gelir.

Atama davranışını değiştirecekseniz öncelikle:

1. `slots/models/courier_assignment.py` dosyasını,
2. `slots/tests/test_courier_assignment.py` testlerini,
3. `automation_21` kaydının canlı veritabanında hangi external ID ve `active` değeriyle çalıştığını

inceleyin. Aynı isimdeki eski/inaktif otomasyonu yanlışlıkla değiştirmeyin.

`data/technical_actions.xml` içinde `automation_21` için büyük eski Python
kodu bulunabilir. Aktif kaydın son kodu, veri yükleme sırası nedeniyle daha
sonra gelen `data/courier_assignment_action.xml` tarafından
`prepare_and_auto_assign_courier()` çağrısına indirgenir. Atama değişikliğini
eski XML kod bloğunda değil `slots/models/courier_assignment.py` içinde
yapın ve external ID eşleşmesini upgrade sonrası doğrulayın.

## Teknik aksiyonlar

`data/technical_actions.xml`, eskiden Odoo Teknik menüsünden oluşturulmuş kayıtların kod karşılığıdır. Dosya büyük ve bazı eski/inaktif sürümler içerir. Önemli aktif otomasyonlar:

- `automation_14`: kurye sipariş durumu değişimi
- `automation_16`: “When Logging Created”
- `automation_17`: yeni kişi
- `automation_19`: adres
- `automation_21`: sipariş oluşturuldu
- `automation_23`: kişi güncellendi
- `automation_24`: kurye değişti
- `automation_25`: kişi silindi
- `automation_29`: sipariş durumu değişti/ücret hesaplama

Eski `automation_13`, `automation_15`, `automation_22` gibi kayıtlar inaktif yedek olabilir. İsim benzerliğine güvenmeyin; XML ID, model, trigger, sequence ve `active` alanlarını doğrulayın.

Başlıca cron'lar sipariş senkronizasyonu, çevrimdışı kurye kontrolü, onaysız sipariş uyarısı, mola durumları, paket sayacı sıfırlama ve log temizliğidir. Bir dakikalık cron'lara kayıt başına sorgu veya uzun dış servis beklemesi eklemeyin.

Server action'lar harita/log ekranları, manuel kurye atama, ödeme analizleri, hakediş raporları ve kurye ücretini yeniden hesaplamayı kapsar. `server_action_1296` manuel hakediş yeniden hesaplamasında aktif kilometre aralığı mantığıyla uyumlu kalmalıdır.

## Ücret hesaplama

- Bölge tanımlı slot: tarife `slots.profile.km_ucret_aralik_ids` üzerinden gelir.
- Sabit kurye/restoran: tarife restoranın `res.partner.km_ucret_aralik_ids` alanından gelir.
- Restoranın platforma kilometre borcu: slot tipinden bağımsız olarak restoranın `res.partner.platform_km_ucret_aralik_ids` alanından gelir.
- Aralık yoksa veya mesafe tanımsız aralığa düşerse kilometre ücreti `0` kabul edilir.
- Aralıklar düz/sabit ücret verir; mesafeyle tekrar çarpılmaz.
- Ücret türü seçimine bağlı ayrı bir hesap kapısı yoktur: paket, saat,
  kilometre, promosyon veya yüzde değeri `0`dan büyükse kendi kalemi hesaba
  katılır; değilse o kalem `0`dır.

Ücret mantığı değiştirilirse aktif `automation_29`, `server_action_1296`, nakit sıfırlama aksiyonu `server_action_1306`, model yardımcı metotları ve iki modülün testleri birlikte kontrol edilmelidir. Kurye hakedişinde `get_distance_fee`, restoran borcunda `get_platform_distance_fee` kullanın; iki tarifeyi birbirine karıştırmayın.

## Entegrasyon ve hata yönetimi

- Her HTTP çağrısında bağlantı ve okuma timeout'u kullanın; mevcut genel yaklaşım `(3, 15)` saniyedir.
- `requests` istisnalarını yakalayın, kimlik bilgilerini loglamayın.
- SMS/push/sesli bildirim başarısızlığı sipariş mutation'ını geri almamalıdır.
- Cron içinde bir restoranın hatası diğer restoranları engellememelidir.
- Sağlayıcı yanıtını doğrulamadan siparişin yerel durumunu geri çevirmeyin.
- Token, parola ve servis anahtarlarını yeni kaynak kod veya dokümana yazmayın.

Mevcut XML teknik aksiyonlarında sabit sağlayıcı anahtarları ve bazı
attachment ID'leri (`7895`, `10782`) vardır. Bunlar taşınabilir değildir;
yeni kod bu deseni çoğaltmamalıdır. Ayrı bir bakım işinde sırları ayar
modeline/`ir.config_parameter` yapısına, görselleri external ID veya modül
statik varlığına taşıyın.

## Performans kuralları

- Recordset döngüsünde tekrar tekrar `search`, `search_count` veya dış API çağrısı yapmayın.
- Uygun yerlerde toplu `search`, sözlük indeksleme, `mapped`, `read_group` ve batch `write/create` kullanın.
- Bir dakikalık cron'ları idempotent tutun; aynı kayıt ikinci kez işlendiğinde çift bildirim/ücret üretmemelidir.
- Yeni sık filtrelenen alanlarda index ihtiyacını ölçün; tahminle indis eklemeyin.
- Controller içinde ağır rapor sorguları çalıştırmayın.
- Atama motorundaki gerçek açık sipariş sayımı ve PostgreSQL satır kilidini kaldırmayın.

### Konum yazma yükü

`/update_location` her çağrıda `res.partner` yazar. Dış uygulama route'unda
14 saniyelik zaman filtresi bulunsa da kontrol ve yazma atomik değildir.
Canlı log geçmişinde `res.partner` üzerinde yoğun serialization conflict
görülmüştür. Yeni konum göndericisi veya ek partner write'ı eklemeyin.
İyileştirmede sunucu tarafı atomik throttling, idempotency ve tek konum
kaynağı tasarlayın; yalnız istemci interval'ini uzatmayı yeterli saymayın.

## Zaman ve saat dilimi

Odoo `Datetime` değerlerini veritabanında UTC saklar. Eski kod ve QWeb şablonlarında Türkiye saati için elle `+3` eklenen yerler vardır. Yeni kodda mümkünse `fields.Datetime.context_timestamp` kullanın; ancak eski akışı parça parça değiştirirken aynı saatin iki kez çevrilmemesine dikkat edin. Saat mantığı değişikliği slot ekranı, cron ve testlerle birlikte ele alınmalıdır.

## Test ve doğrulama

Mevcut restoran kilometre ve slot başlatma ayarı testleri:
`tests/test_restaurant_km_fee.py` (14 test metodu).

Değişikliğin kapsamına göre:

- Python: ilgili dosyaları `py_compile` ile doğrulayın.
- XML: bir XML parser ile bütün veri/view dosyalarını doğrulayın.
- Model/view alanlarının gerçekten yüklendiğini kontrol edin.
- Sipariş mutation'ı için pozitif, eksik veri, tekrar çağrı ve dış servis hata senaryolarını test edin.
- Otomatik atama değiştiyse `slots` içindeki 21 senaryoluk atama testlerini
  de çalıştırın. Ancak mevcut paket kurye özel vardiya saati dışında kalan
  Excel satırı senaryosunu kapsamamaktadır; test sayısını tam güvence
  kabul etmeyin.
- Entegrasyon testlerinde gerçek sağlayıcıya istek atmayın; HTTP çağrılarını mock'layın.

Üretim veritabanında Odoo testlerini çalıştırmayın. Gerekirse `kuryetec` veritabanının geçici bir klonunu oluşturup testi orada çalıştırın.

## Öncelikli teknik borçlar

1. Kurye route'larında sipariş sahipliği ve mutation sırası.
2. Konum update yarışları ve yoğun `res.partner` yazmaları.
3. XML action kodundaki hard-coded sağlayıcı anahtarları/attachment ID'leri.
4. Manifestte ilan edilmeyen `notifier` runtime bağımlılığı.
5. Sabit para birimi ID'si `32` kullanılan alanlar.
6. Büyüyen `ir.logging`, `mail_message`, `mail_tracking_value` ve
   `website_track` tabloları. Gürültülü dakikalık action'lara kayıt başına
   yeni log eklemeyin.

## Değişiklik ve dağıtım

Canlı kaynak dizini:

`/odoo/odoo16/kuryetec-custom-addons`

Eski `/odoo/odoo16/odoo-custom-addons` kopyasını bu dört modül için kaynak kabul etmeyin.

Canlı yapılandırma/veritabanı/servis:

- Config: `/etc/odoo16-kuryetec.conf`
- Database: `kuryetec`
- Service: `odoo16-kuryetec.service`
- Log: `/var/log/odoo/odoo16-kuryetec.log`
- HTTP port: `12791`

Kod, XML, security veya asset değişikliğinde manifest sürümünü anlamlı şekilde artırın. Güvenli upgrade sırası:

```bash
systemctl stop odoo16-kuryetec.service
sudo -u odoo /odoo/odoo16/odoo-venv/bin/python3 /var/lib/odoo/odoo-bin \
  -c /etc/odoo16-kuryetec.conf -d kuryetec -u corders --stop-after-init --no-http
systemctl start odoo16-kuryetec.service
```

Sonrasında servis durumunu, logları ve temel HTTP yanıtını kontrol edin. Sadece `.md` dokümantasyonu değiştiyse restart veya upgrade gerekmez.

## Değişiklik öncesi kontrol listesi

1. İlgili model, view, controller ve teknik aksiyonu `rg` ile birlikte bulun.
2. Aynı iş kuralının XML Python code alanında veya server action'da kopyası var mı kontrol edin.
3. Canlı DB kaydı söz konusuysa external ID ve aktif kaydı doğrulayın.
4. Mevcut selection anahtarlarını, route URL'lerini ve dış sistem kimliklerini koruyun.
5. Performans açısından sorgu sayısını ve dış servis çağrısını değerlendirin.
6. Testi ekleyin/çalıştırın, sonra upgrade ve log kontrolü yapın.

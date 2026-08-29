# Slots — AI Geliştirme Rehberi

Bu dosya `slots` modülünde çalışan geliştirici ve yapay zekâ araçları için kalıcı bağlamdır. Modül vardiya/slot yönetimini, kurye kapasitesini, hakedişi ve sistemin en kritik parçası olan otomatik kurye atama motorunu içerir. Küçük görünen bir değişiklik gerçek sipariş dağılımını etkileyebilir; test etmeden davranış değiştirmeyin.

## Güncel sistem özeti — 10 Ağustos 2026

- Canlı sürüm: `16.0.2.7.0`
- Önce bu dosyayı, sonra `../corders/AGENTS.md` ve
  `../slot_dashboard/AGENTS.md` dosyalarını okuyun. Mobil davranış
  `../kuryetec_website/AGENTS.md` içindedir.
- Atama motoru üretim operasyonunun beynidir. “Bilinen açık” maddelerini
  kaynakta görülmeden düzeltilmiş kabul etmeyin.
- Teknik model, alan, XML ID ve route adlarında geriye uyumluluk için
  `slot` sözcüğü korunur; kullanıcıya görünen etiketlerde bunun adı
  “Vardiya”dır. Sırf terminoloji için teknik anahtarları yeniden adlandırmayın.

Gemini/Codex başlangıç sırası: manifesti ve bu rehberi tamamen oku; çağrı
yerlerini Python ile sınırlamayıp `technical_actions.xml` dosyalarında da
ara; `sequence` ilişkisini Many2one sanma; üretim DB'sinde senaryo testi
çalıştırma; kod ve DB action'ını iki ayrı kaynak gerçeğe dönüştürme.

## Modülün görevi

- Bölge tanımlı ve sabit kurye slotlarını yönetir.
- Slot içindeki kurye satırlarını ve kurye bazlı çalışma saatlerini tutar.
- Aktif slotu, kapasiteyi, mesafeyi ve rota uyumunu kullanarak siparişi kuryeye atar.
- Bölge tanımlı modelin parçalı kilometre ücretlerini tutar.
- Slot başlatma/bitirme, aylık muhasebe ve hakediş otomasyonlarını sağlar.

- Manifest: `__manifest__.py`
- Ana slot modeli: `models/slots.py`
- Kurye slot satırı: `models/skurye.py`
- Atama motoru: `models/courier_assignment.py`
- Teknik aksiyonlar: `data/technical_actions.xml`
- Atama testleri: `tests/test_courier_assignment.py`
- Slot başlatma testleri: `tests/test_slot_start.py`
- Paket mutabakatı: `models/package_reconciliation.py`
- Paket mutabakatı testleri: `tests/test_package_reconciliation.py`
- Yönetici operasyon dashboardu ayrı `slot_dashboard` modülündedir.

`slots`, `corders` modülüne bağlıdır. Sipariş verisi `corders.profile`, restoran/kurye verisi `res.partner` üzerindedir. Bildirimler `notifier`, mobil görünüm `kuryetec_website` tarafından sağlanır.

## Yönetici operasyon dashboardu

Dashboard iş mantığı, OWL assetleri, action/menü ve testleri ayrı
`slot_dashboard` modülüne taşınmıştır. Slot tarihleri ile eski `sequence`
ilişkisindeki sorgu indeksleri veri modeline ait oldukları için bu modülde
kalır. Dashboard değişikliklerini yeniden `slots` içine eklemeyin.

Dashboard ve paket beyanı kısayolu yalnız
`res.partner.operation_dashboard_enabled=True` restoranların slotlarını
göstermelidir. Bir kurye hem tikli hem tiksiz restoranda çalışıyorsa yalnız
tikli restoran vardiyası kapsama girer; kurye tamamen global olarak
elenmez/dahil edilmez.

## Slot modelleri

### `slots.profile`

Ana vardiya/slot modelidir. Temel alan grupları:

- Slot tipi: `sabit` veya `bolge`
- Restoranlar
- Ana başlangıç/bitiş zamanı
- Başlangıç adresi ve koordinatları
- Aktiflik, çalışma ve hesap durumu
- Promosyon, paket başı ve saatlik ücretler
- Bölge kilometre fiyat aralıkları
- Slot içindeki kurye satırları

Sabit kurye modelinde slot genellikle restoranın çalışma gün/saat ve kurye ayarlarından günlük otomatik oluşturulur. Bölge tanımlı slotlar operasyon tarafından elle açılır. Bu ayrımı değiştiren işlerde restoran ayarları, günlük oluşturma aksiyonu ve mevcut kayıtların davranışı birlikte değerlendirilmelidir.

`cron_57` ile restoran haftalık ayarlarından üretim ve `slot_dashboard`
Excel importu aynı anda mevcut iki plan kaynağıdır. Excel yönetimli
restoranlarda kalıcı sabit kurye listesi boş bırakılır; aksi halde iki
kaynağın çakışma/çift plan etkisini değerlendirin. Excel importunun tam
sözleşmesi `../slot_dashboard/AGENTS.md` içindedir.

### `skurye.profile.lines`

Bir slot içindeki kurye vardiyasını temsil eder:

- Kurye
- Kurye bazlı planlanan `kurye_start_date` / `kurye_end_date`
- Gerçek `start_date` / `end_date`
- Aktif/çalışıyor durumları
- Paket sayacı, mola ve hakediş alanları

Önemli: Slot ilişkisi `skurye.profile.lines.sequence` adlı bir `Integer`
üzerinden kurulmuş One2many'dir; gerçek Many2one/foreign key değildir.
Veritabanı cascade veya referans bütünlüğü sağlamaz. Slot silinmesi/reimportu
yetim kurye satırları bırakabilir ve global cron aramaları bunları görebilir.
Canlı DB'de yetim kayıtlar görülmüştür. Yeni sorgularda parent slotun
`exists()` sonucunu doğrulayın. İlişkiyi migration, veri temizliği ve geri
dönüş planı olmadan dönüştürmeyin.

Kurye bazlı planlanan iki saat de doluysa ekranda ve aktiflik değerlendirmesinde bu saatler ana slot saatlerine tercih edilir. Alanlardan biri eksikse ana slot başlangıç/bitişini kullanın. `/kurye-anasayfa` ile `/musait-saatler` aynı etkin zaman mantığını göstermelidir.

`/musait-saatler` gün filtresi `get_courier_day_slots()` metodunu kullanır.
Excel vardiyalarında ana slotun UTC başlangıcı önceki güne düşebileceği için
önce `shift_plan_date`, eski kayıtlarda ise kurye başlangıcının yerel günü
esas alınır. Ana slotun ham `start_date` alanıyla yeniden filtreleme yapmak
gece vardiyalarını bir gün erken gösterir.

Takvim query string'i zaten Türkiye yerel tarihini taşır.
`convert_string_to_datetime()` bu değerden ayrıca UTC farkı düşmez; aksi
halde 00:00-03:00 arasındaki seçim bir önceki güne kayar.

Partner üzerindeki “Bugünün Vardiyaları” server action'ı da kullanıcının
yerel gün sınırlarını UTC'ye çevirir. Restoranı `magazalar`/`partner_id`,
kuryeyi ise `skurye_profile_lines.partner_id` üzerinden eşleştirir; Excel
vardiyalarında eski `kurye` alanına güvenmez.

## Kurye tarafından slot başlatma

İş kuralının tek kaynağı `slots.profile.start_courier_slot(courier, latitude, longitude, accuracy)` metodudur. Mobil arayüz `POST /courier/slot/start` JSON route'unu çağırır. Eski `/available/<kurye_id>` route'u uyumluluk için vardır ve aynı model metoduna yönlenir.

Başlatma sırası:

1. Tarayıcıdan yeni ve yüksek doğruluklu konum alınır.
2. Sunucu koordinat aralığını doğrular ve kuryenin konum/zaman/doğruluk alanlarını günceller.
3. Oturum kullanıcısının kendi aktif slot satırı bulunur; istemciden kurye kimliği kabul edilmez.
4. Kurye özel saatleri eksiksizse onlar, değilse slot saatleri doğrulanır.
5. Sabit slotta restoran koordinatı ve restoranın `sabit_slot_baslatma_yaricapi_m` değeri kullanılır.
6. Bölge slotunda eski `2000 m` başlangıç yarıçapı korunur.
7. Uygunsa satır idempotent biçimde başlatılır ve kurye `musait` yapılır.

Tarayıcı konumu için HTTPS ve konum izni gerekir. Mesafe/saati yalnız JavaScript'te kontrol etmeyin; sunucu doğrulaması zorunludur.

### Vardiya bitirme ve admin durdur/devam et

Sabit slotta kurye mobilindeki manuel “Slottaki İşi Sonlandır” butonu
gizlidir; planlanan bitiş ve cron yaşam döngüsü esastır. Bölge slotunun eski
manuel davranışı korunur.

Operasyon dashboardundaki admin aksiyonu
`action_operation_dashboard_toggle_shift()` üzerinden satırı
durdurur/devam ettirir. Durdurma gerçek çalışma süresini yazar. Devam
ettirme orijinal `start_date` değerini sıfırlamaz; duraklama saniyesini
biriktirir, `end_date` alanını açar ve sonraki hesap net süreden duraklamayı
düşer. Paket beyanı verilmiş, planlanan bitişi geçmiş veya parent slotu
kapanmış vardiya devam ettirilemez.

## Kilometre ücret aralıkları

Bölge slotunun tarife modeli `slots.km.ucret.araligi`, One2many alanı `slots.profile.km_ucret_aralik_ids` şeklindedir.

`slots.profile.get_distance_fee(distance_meters)`:

- Mesafeyi metre alır ve kilometreye çevirir.
- Aralığı `[başlangıç_km, bitiş_km)` olarak değerlendirir.
- Eşleşen satırdaki sabit ücreti döndürür; kilometreyle çarpmaz.
- Tarife yoksa veya arada boşluk varsa `0` döndürür.
- Çakışan, ters veya sıfır uzunluklu aralıklar kabul edilmemelidir.

Örnek: `0–10 km = 1 ₺`, `10–1000 km = 2 ₺` geçerli bir tanımdır. Tam `10.00 km` ikinci satıra girer. Bu miktarlar yalnızca örnektir; gerçek ücret işletme tarafından belirlenir.

Sabit kurye modelinin kilometre tarifesi burada değil, `corders` içindeki restoran formunda `res.partner.km_ucret_aralik_ids` alanındadır.

## Otomatik kurye atama motoru

Ana uygulama `models/courier_assignment.py` içindedir ve `corders.profile` modelini inherit eder. Sipariş oluşturma otomasyonu `corders/data/courier_assignment_action.xml` üzerinden `prepare_and_auto_assign_courier()` metodunu çağırır.

### Hazırlık

Hazırlık metodu manuel oluşturulan siparişte zorunlu restoran/müşteri/adres/konum verisini doğrular, gerekirse geocoding yapar ve sonra atamayı başlatır. Aynı sipariş ikinci kez işlenirse mevcut geçerli atamayı bozmayacak şekilde idempotent davranış korunmalıdır.

### Aktif slot seçimi

`_assignment_find_slot` sipariş zamanında aktif olan parent slotu arar. Birden
fazla kayıt varsa deterministik olarak en yeni başlangıç ve ID öncelenir
(`start_date desc, id desc`).

Bilinen kritik açık: mevcut `_assignment_find_slot` yalnız ana slot saatini
süzer. `_assignment_build_candidates`, kilit sonrası doğrulama ve zorunlu
fallback; satırın `kurye_start_date <= sipariş zamanı < kurye_end_date`
koşulunu veya gerçekten `start_date` almış olmasını doğrulamaz. Excel
importunda parent slot tam gün olduğu için, başka vardiya nedeniyle global
durumu `musait` olan bir kurye kendi restoran vardiya saati dışında aday
olabilir. Normal aday, kilit sonrası kontrol, tek-kurye yolu ve zorunlu
fallback aynı ortak “satır gerçekten çalışıyor” yardımcısına bağlanmalıdır.

### Aday filtreleri

Atama adayı:

- Aktif slot satırında olmalı.
- Mola durumunda olmamalı.
- `musait` veya `pakette` gibi kabul edilen çalışma durumunda olmalı.
- Geçerli enlem/boylama sahip olmalı.
- Kapasitesini doldurmamış olmalı.
- Kendi etkin planlanan saatinde ve gerçekten başlamış vardiyada olmalı
  (hedef kural; yukarıdaki açık bugün tam uygulanmış değildir).

Kapasite kararı yalnızca eski sayaç alanına dayanmaz. Son 24 saatteki gerçek açık siparişler sayılır; final/iptal durumları dışarıda tutulur. Sayaç, görüntüleme ve sıralama için yardımcıdır; gerçek açık iş sayısının yerine geçmemelidir.

### Rota ve seçim fazları

Sabit kurye senaryosunda mevcut paket rotasıyla yön açısı karşılaştırılır; yaklaşık `50°` tolerans kullanılır. Bölge senaryosunda restoran gruplama yakınlığı varsayılan olarak `1500 m` civarındadır.

Mevcut seçim sırası:

1. A1: Uygun rota, müsait kurye, `500 m`
2. A2: Uygun rota, müsait kurye, `1200 m`
3. A3: Uygun rota, paketli kurye, `750 m`
4. A4: Uygun rota, müsait kurye, `2000 m`
5. A5: Uygun rota, müsait/paketli kurye, mesafe sınırı olmadan
6. A7: Rota bulunamazsa adil müsait kurye fallback'i

Fallback sırası slot satırı paket sayısı, gerçek açık paket sayısı, mesafe ve ID kullanarak deterministik tutulur. Sabit eşikler veya faz sırası değiştirilecekse tüm senaryoların etkisi açıkça belgelenmeli ve test edilmelidir.

Normal fazlar aday bulamazsa `_assignment_force_working_courier()` işletme
kararı gereği paketi boşta bırakmamak için mevcut çalışanlardan birine
zorunlu atar. Bu yol kapasite limitini bilinçli olarak uygulamaz; açık iş,
sayaç, mesafe ve ID ile seçim yapar. “Her durumda ata” gereksinimini
kaldırmadan kapasite eklemek davranışı değiştirir. Kurye satırının gerçek
vardiya zamanı kontrolü ise zorunlu yolda da uygulanmalıdır.

### Eşzamanlılık

Atama sırasında PostgreSQL `FOR UPDATE` satır kilidi kullanılır. Kurye kilitlendikten sonra uygunluk ve kapasite yeniden doğrulanır. Bu mekanizma aynı anda gelen siparişlerin aynı son kapasiteyi aşarak tek kuryeye atanmasını engeller.

Kilidi, kilit sonrası yeniden kontrolü veya deterministik sırayı performans gerekçesiyle kaldırmayın. Gerekirse transaction kapsamını küçültün fakat yarış koşulunu geri getirmeyin.

Başarılı atamada siparişin kurye/telefon, yön, senaryo ve mesafe alanları yazılır; gösterim mesafesi mevcut davranışta en fazla `6000 m` ile sınırlandırılabilir. Slot satırı paket sayacı da güncellenir.

Mevcut 21 atama testi; faz, rota, kapasite, fallback, idempotency ve kilit
sonrası doğrulamayı kapsar. Tam gün parent slot + gelecekte başlayacak/bitmiş
Excel satırı, başka vardiya yüzünden global durumu müsait olan kurye ve
zorunlu fallback'in bu saat sınırları mevcut kapsamın açık noktalarıdır.

## Sabit slot paket mutabakatı

Özellik devreye alındıktan sonra oluşturulan sabit kurye slot satırları
`paket_mutabakat_gerekli=True` olur. Eski satırlar bilinçli olarak varsayılan
`False` kalır; geçmiş slotlar için kurye ekranını topluca kilitlemeyin.

Kurye, gerçekten başlattığı slotun etkin bitiş zamanı dolunca
`submit_courier_package_count()` ile bir kez beyan verir. Sıfır geçerli
değerdir; negatif ve kesirli değer kabul edilmez. Beyan alanları doğrudan
`skurye.profile.lines` üzerindedir. Restoran listesi için
`slots.package.reconciliation` kayıtları kullanılır:

- `pending`: restoranın 24 saatlik karar süresi devam eder.
- `approved`: restoran yetkilisi onaylamıştır.
- `rejected`: restoran yetkilisi reddetmiştir; kurye yeniden giriş yapamaz.
- `auto_approved`: süre dolunca cron otomatik onaylamıştır.

Restoran yetkisi `res.partner.yetkili_users` üzerinden doğrulanır. Restoran
sayısı değiştiremez; onaylayabilir veya zorunlu gerekçe yazarak reddedebilir.
Ret gerekçesi vardiya satırında saklanır ve mutabakat formunda gösterilir.
Slot admini ve
sistem yöneticisi sayıyı revize edebilir, revizyon kullanıcı/zamanı satırda
tutulur. Kurye veya restoranın korumalı alanları doğrudan `write()` ile
değiştirmesine izin vermeyin.

`cron_auto_approve_package_reconciliations` her 10 dakikada yalnız süresi
dolmuş `pending` kayıtları işler. Cron sorgusundaki durum ve son tarih
indekslerini kaldırmayın.

### Mutabakat kazanç hesabının mevcut davranışı

- Kuryenin gerçek beyanı `kurye_beyan_paket_sayisi` alanında değişmeden
  saklanır. Ücretlendirilen adet `mutabakat_hesaplanan_paket_sayisi` alanına
  yazılır ve `max(kurye beyanı, restoran.garanti_paket_sayisi)` olarak
  hesaplanır. Garanti `0` ise doğrudan beyan kullanılır.
- Paket başı ve slot promosyonu ücretlendirilen paket sayısından hesaplanır.
- Restoranın platform borcu ayrı
  `restoran_garanti_paket_sayisi` tabanını kullanır; kurye garantisi restoran
  borcuna, restoran garantisi kurye ödemesine karıştırılmaz.
- Saatlik ücret gerçek çalışma süresini kullanır; dashboard durdur/devam et
  araları net süreden düşülür.
- Kilometre ve yüzde kalemleri gerçek teslim edilmiş siparişlerden gelir.
- Her kalem yalnız tarifesi `0`dan büyükse eklenir; ayrı bir ücretlendirme
  tipi seçimine bağlı değildir.

Bilinen finansal borçlar:

1. `_package_reconciliation_orders()` kurye satırının özel vardiya saatini
   değil parent slot başlangıç/bitişini kullanır. Tam günlük Excel slotunda
   vardiya dışı sipariş mutabakata karışabilir.
2. Tarife snapshot'ı yoktur. Kazanç beyan, restoran onayı ve otomatik onay
   sırasında o anki restoran/slot fiyatlarıyla yeniden hesaplanır. Tarife
   arada değişirse tarihsel tutar değişebilir.
3. `slot_dashboard` hakediş wizardı beyan edilmiş toplamı onay durumundan
   bağımsız toplayabilir. Bekleyen/reddedilen tutarın resmi hakedişe girip
   girmeyeceği netleştirilip açık bir domain ile uygulanmalıdır.

## Teknik aksiyonlar ve cron'lar

`data/technical_actions.xml`, DB'de elle oluşturulmuş aksiyonların kod karşılığıdır. Başlıca otomasyonlar:

- `automation_10`: slot oluşturma
- `automation_11`: slot oluşturma/güncelleme
- `automation_18`: adresten koordinat bulma
- `automation_20`: doğrulama ve türetilmiş hesaplar
- `automation_27`: kurye slot satırları
- `automation_28`: silme işlemleri

`automation_20`; restoran, kurye satırı, tarih, adres ve fiyat doğrulamalarını yapar. Bölge slotu fiyatlandırma ister; sabit slot tek restoranla sınırlandırılır; restoranın slot tipiyle uyum aranır; süre ve satır hakedişleri hesaplanır.

Başlıca cron'lar:

- `cron_57`: slotları otomatik başlat/bitir, her dakika
- `cron_62`: kurye satırını başlat/bitir, her dakika
- `cron_70`: aylık muhasebe kontrolü

Bir dakikalık cron'larda N+1 sorgu, kayıt başına geocoding veya sınırsız HTTP beklemesi oluşturmayın.

### Cron yaşam döngüsüyle ilgili bilinen açık

Aktif XML kodunda `cron_57`, biten slot satırlarının kuryesini doğrudan
`mesgul` yapabilir. `cron_62` de `kurye_end_date` geçmiş satırı kapatıp
kuryeyi `mesgul` yapar; satırın gerçekten başladığını ve kuryenin başka
başlamış aktif vardiyasını yeterince doğrulamaz. Aynı kurye çakışan/ardışık
restoran vardiyalarında çalışabildiği için bir satır diğer vardiyanın global
kurye durumunu bozabilir. Parent slot, gerçek `start_date`, kurye özel etkin
zaman ve başka aktif başlamış vardiya kontrolünü ortak model metoduna
taşıyın; XML Python kodunu büyütmeyin.

İlk 10 dakika operasyonel gecikme sayılmaz. Hakedişte 20 dakikaya kadar
(20 dahil) planlanan başlangıç korunur; 20 dakikayı aşan girişlerde çalışma
süresi kuryenin gerçek girişinden hesaplanır. Bu kuralın merkezi uygulaması
`skurye.profile.lines.calculate_worked_hours_until()` metodudur.

`slots.puantaj.duzeltme`, yönetici tarafından eklenen saat ve paketleri ana
vardiya verisini ezmeden denetim iziyle saklar. Satırdaki
`puantaj_ek_saat`/`puantaj_ek_paket_sayisi` toplamları paket mutabakatına,
kurye hakedişine ve restoran borcuna eklenir. Mevcut beyan değeri değişmez.

Server action'lar bugünkü slotlar, hakedişler, harita ve saatlik ücretli/ücretsiz analizleri kapsar. Aynı isimli eski/inaktif kayıt olabileceği için XML ID ve `active` alanını doğrulayın.

## Test paketi

`tests/test_courier_assignment.py` gerçek ORM kayıtlarıyla atama motorunu doğrulayan 21 senaryo içerir. Kapsam:

- Aktif slot bulunması/bulunmaması
- Kurye çalışma, mola ve konum uygunluğu
- Sabit/bölge rota seçimleri
- Mesafe fazları ve fallback
- Paket kapasitesi ve gerçek açık sipariş sayısı
- Deterministik sıralama
- Eksik sipariş verileri
- Aynı siparişin tekrar işlenmesi
- Eşzamanlı atamaya temel oluşturan yeniden doğrulama

Atama algoritmasına dokunan her değişiklikte mevcut testleri çalıştırın ve yeni iş kuralına en az bir pozitif, bir negatif, bir sınır ve mümkünse yarış koşulu testi ekleyin. “Test kodu derleniyor” yeterli değildir; Odoo test runner ile geçici DB üzerinde gerçekten çalıştırın.

Kilometre tarifesi değişikliklerinde başlangıç, bitiş, tam sınır, boşluk, çakışma ve hiç satır olmaması test edilmelidir.

`tests/test_slot_start.py`; sabit ve bölge yarıçapı, sınır dışı konum, kurye özel saati, pasif satır ve tekrar çağrı davranışını gerçek ORM kayıtlarıyla doğrular.

`tests/test_package_reconciliation.py`; sabit/bölge ayrımını, etkin bitiş
zamanını, çalışılmamış slotu, sıfır/negatif/kesirli sayıları, tek seferlik
beyanı, restoran yetkisini, gerekçeli onay/red, 24 saat cron'u ve admin revizyonunu
gerçek ORM kayıtlarıyla doğrular.

Üretim `kuryetec` DB'sinde test çalıştırmayın. Geçici klon kullanın ve test bittikten sonra yalnızca doğrulanmış klonu kaldırın.

Test dosyasının varlığı güncel/yeşil olduğu anlamına gelmez.
`slot_dashboard/tests/test_shift_import.py` içindeki gece yarısını ertesi
güne taşıyan eski beklenti, güncel `00:00 -> aynı gün 23:59:59` kuralıyla
çelişebilir. Ürün kuralı ve test beklentisini eşitlemeden test paketini tam
güvence kabul etmeyin.

## Performans kuralları

- Aday kuryeleri ve açık siparişleri toplu alın; aday döngüsünde `search_count` çalıştırmayın.
- Mesafe hesabı CPU tarafında hafiftir; asıl maliyet ORM sorguları ve geocoding/HTTP'dir.
- Koordinatı eksik adayları erken eleyin.
- Aynı request içinde restoran/kurye ilişkilerini tekrar tekrar okumayın.
- Cron sorgularında zaman ve durum domain'lerini dar tutun.
- Toplu kayıtlar için `mapped`, `read_group` ve ID tabanlı sözlükler kullanın.
- SQL kilitlerini kısa tutun; kilit altındayken dış servise çağrı yapmayın.

## Zaman ve saat dilimi

Odoo Datetime alanları UTC saklanır. Eski action ve şablonlarda elle `+3` dönüşümü bulunabilir. Yeni kodda `fields.Datetime.context_timestamp` tercih edilir; mevcut akışı topluca incelemeden tek bir yerde dönüşüm değiştirip slotları üç saat kaydırmayın.

## Güvenli geliştirme kuralları

1. Atama değişikliğinde model, `automation_21` ve 21 testi birlikte inceleyin.
2. `sequence` ilişkisinin eski veri uyumluluğunu koruyun.
3. Selection teknik anahtarlarını migration olmadan değiştirmeyin.
4. Satır kilidi, kapasite yeniden kontrolü ve gerçek açık sipariş sayımını koruyun.
5. İş kuralını QWeb veya JavaScript içine kopyalamayın.
6. Teknik action Python kodunu değiştirirken canlı external ID/aktif kayıt eşleşmesini doğrulayın.
7. Yeni bildirim hatasının atama transaction'ını geri almasına izin vermeyin.
8. Kurye satırını parent slotu doğrulamadan global cron/rapora dahil etmeyin.
9. Hakedişte parent slot saati ile kurye özel vardiya saatini karıştırmayın.

## Dağıtım

Kaynak dizini `/odoo/odoo16/kuryetec-custom-addons`; eski `/odoo/odoo16/odoo-custom-addons` kopyasını kullanmayın.

- Config: `/etc/odoo16-kuryetec.conf`
- Database: `kuryetec`
- Service: `odoo16-kuryetec.service`
- Log: `/var/log/odoo/odoo16-kuryetec.log`

Kod/XML/security/asset değişikliğinde manifest sürümünü artırın. Bağımlılık sırası nedeniyle gerekirse `corders,slots` birlikte upgrade edilir:

```bash
systemctl stop odoo16-kuryetec.service
sudo -u odoo /odoo/odoo16/odoo-venv/bin/python3 /var/lib/odoo/odoo-bin \
  -c /etc/odoo16-kuryetec.conf -d kuryetec -u corders,slots \
  --stop-after-init --no-http
systemctl start odoo16-kuryetec.service
```

Upgrade sonrası loglarda traceback, invalid field/view ve cron hatası arayın; ardından slot ve kurye ana sayfasını kontrol edin. Sadece `.md` değişikliğinde restart/upgrade gerekmez.

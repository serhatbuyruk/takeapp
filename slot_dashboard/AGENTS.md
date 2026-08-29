# Slot Dashboard — AI Geliştirme Rehberi

Bu modül Kuryetec yöneticilerinin günlük slot ve kurye operasyonunu tek
ekranda izlemesini sağlar. Ayrı bir backend uygulamasıdır; ana menü sırası
`4` olduğu için canlıdaki `Corders` uygulamasından (`5`) önce görünür.

Canlı sürüm `16.0.1.7.4`'tür. Teknik model/alan adlarında `slot`
korunur; kullanıcıya görünen arayüz terminolojisi “Vardiya”dır.

## Mimari

- Manifest: `__manifest__.py`
- Veri servisi: `models/operation_dashboard.py`
- Client action: `static/src/js/operation_dashboard.js`
- OWL template: `static/src/xml/operation_dashboard.xml`
- İzole stiller: `static/src/scss/operation_dashboard.scss`
- Action ve ana menü: `views/dashboard_views.xml`
- Admin başlangıç action ayarı: `hooks.py`
- Senaryo testleri: `tests/test_operation_dashboard.py`
- Excel vardiya aktarımı: `models/shift_import.py`
- Aktarım ve paket durum viewları: `views/shift_management_views.xml`
- Aktarım testleri: `tests/test_shift_import.py`
- Manuel vardiya popup'ı: `models/manual_shift.py`

Modül `web`, `slots` ve `corders` bağımlılıklarını doğrudan bildirir.
Dashboard metrikleri `slots.profile`, `skurye.profile.lines` ve
`res.partner` kayıtlarını raporlar. Yalnız Excel yükleme geçmişi için
`slot.dashboard.shift.import.batch` denetim kaydı oluşturulur.

## Güvenlik ve metrik kuralları

Menü yalnız sistem yöneticileri ile Slots/Corders admin veya tam erişim
gruplarına görünür. Client action doğrudan çağrılsa bile
`get_operation_dashboard_data()` aynı grup kontrolünü sunucu tarafında
yeniden yapar.

Rapor günü kullanıcının saat dilimine göre hesaplanır. Kurye satırında hem
`kurye_start_date` hem `kurye_end_date` doluysa bunlar, aksi halde ana slot
saatleri kullanılır. `10 dakika` ve üzeri geç giriş kabul edilir. Giriş
oranının paydası yalnız başlangıç zamanı gelmiş vardiyalardır. Teknik
`Boş` kurye gerçek vardiya olarak sayılmaz; bu kayıt kuryesiz slot olarak
raporlanır.

Ana kurye KPI'ları vardiya satırı değil tekil kurye sayar. Bir kuryenin gün
içinde birden fazla satırı varsa durumu tekilleştirilir: başlangıç zamanı
gelen satırlardan biri eksikse `giriş yapmayan`, aksi halde biri geçse
`geç giriş`, aksi halde `zamanında giriş` sayılır. Yalnız gelecekte vardiyası
olan kurye `vardiya saati gelmedi` sayılır. Böylece zamanında + geç + gelmedi
toplamı, başlangıç zamanı gelen tekil kurye toplamına daima eşittir.
Restoran bazlı özet de aynı tekil kurye ve durum önceliğini kullanır.
Dashboard yalnız `res.partner.operation_dashboard_enabled` alanı işaretli
restoranlara bağlı slot ve kuryeleri raporlar. Hiçbir restoran işaretli
değilse dashboard operasyon verisi göstermez. Uyum Oranı yalnız giriş zamanı gelmiş
tekil kuryelerde `(zamanında + geç giriş) / zamanı gelen` olarak hesaplanır.
Restoran Bazlı Durum satırları tıklanabilir; OWL modalı seçilen restoranın
aynı dashboard günündeki `rows` verisini kullanarak kurye, planlanan saat,
gerçek giriş ve zamanında/geç/gelmedi/bekliyor durumunu gösterir. Modal için
ayrı RPC çalıştırılmaz; restoran adı `restaurants[].name` ile
`rows[].restaurant_name` arasında birebir anahtardır.
Günün Kurye Vardiyaları tablosundaki satır oku parent `slots.profile`
kaydını açmaz. `get_operation_shift_line_action(line_id)` erişim ve dashboard
kapsamını doğruladıktan sonra `view_operation_shift_line_form` ile doğrudan
ilgili `skurye.profile.lines` kaydını açar. Bu formdaki Sil işlemi yalnız
personel satırını kaldırır; ana vardiya ve diğer kurye satırları korunur.

## Excel vardiya planı

Dashboard kısayolları beyaz içerik alanında üç operasyona ayrılır: vardiya
planı yükleme, yüklenen vardiyaları görme ve paket beyan durumlarını izleme.
Yükleme dosyasının ilk sayfasında başlıklar sırasıyla `TARİH`, `BÖLGE`,
`PROJE`, `ŞUBE`, `KURYE`, `VARDİYA GİRİŞ`, `VARDİYA ÇIKIŞ` olmalıdır.
Saatler kullanıcının saat diliminde okunur; çıkış saati girişe eşit veya
daha erkense vardiya ertesi gün biter. Tek istisna, vardiya çıkışının
`00:00` olmasıdır; bu değer aynı gün `23:59:59` olarak kaydedilir. Vardiya
başlangıcı `00:00` ise aynı gün `00:00:01` olarak kaydedilir.

Aktarım iki aşamalıdır: `Planı Kontrol Et` hiçbir operasyon kaydı yazmadan
geçerli satır sayısını ve satır numaralı hata/çakışma raporunu gösterir.
Hata varsa yönetici `Geçerli Satırları Yine de İçeri Aktar` ile yalnız temiz
satırları uygular. Dosya biçimi/başlığı gibi dosyanın tamamını okunamaz yapan
hatalar yine işlemi durdurur. Gerçek aktarım PostgreSQL transaction advisory
lock ile eşzamanlı yüklemelere karşı seri çalışır.

Kurye adı normalize edilmiş tam adla; restoran önce `PROJE + ŞUBE`, sonra
proje tam adı, son olarak proje ve şube kelimeleriyle eşleştirilir. Eksik veya
birden fazla eşleşen partner, dosya içi kurye çakışması ya da mevcut başka
restoran/kurye vardiyasıyla çakışan satır raporlanıp atlanır; diğer satırlar
etkilenmez.
Yeni gruplar restoran/gün bazında yerel günün tamamını kapsayan
`00:00:00–23:59:59` tek sabit slot ve her Excel satırı için dosyadaki gerçek
giriş/çıkış saatlerini taşıyan ayrı `skurye.profile.lines` kaydı oluşturur.
Sonraki Excel aynı restoran ve güne birleşir: Excel'de daha önce bulunmayan
kuryeler mevcut vardiyaya eklenir; aynı kurye tekrar gelirse son satırın
saatleri ve Excel bilgileri mevcut satırın üstüne yazılır. Yeni dosyada yer
almayan eski kuryeler kesinlikle silinmez. Paket taşımış/beyan vermiş kuryenin
saatleri değiştirilmeye çalışılırsa yalnız o satır atlanır ve raporlanır;
aynı vardiyaya yeni kurye eklenmesine engel olmaz. Sadece vardiyaya giriş
yapılmış olması revizyon engeli değildir.
Elle açılmış slotlar otomatik değiştirilmez; çakışma uyarısı verir.
Bölge tipindeki eşleşmiş restoran sabit modele alınır; dosyadaki kuryeler
restoranın `Sabit Kuryeler` listesine yazılmaz. Böylece günlük eski slot
otomasyonu bu restoran için sonraki günlerde kendiliğinden plan üretmez.

Paket görünümü doğrudan `skurye.profile.lines` kayıtlarını açar; yalnız
mutabakat oluşmuş satırları tutan `slots.package.reconciliation` modeli bu
liste için kullanılmaz. Böylece gelecekteki veya beyanı henüz oluşmamış
vardiya personeli de listelenir. `dashboard_package_state` anlık hesaplanır: vardiya
bitmeden standart, bitip beyan verilmediyse kırmızı, beyan verildiyse yeşil.
Dashboarddaki paket beyanı kısayolu yalnız
`operation_dashboard_enabled=True` restoranların slot satırlarını açar.
`Vardiyaları Gör` kısayolu seçilen yerel günü `shift_plan_date` alanında da
doğrudan filtreler. Tarih inputu değiştiğinde OWL state RPC tamamlanmadan önce
güncellendiği için kullanıcı hemen karta bassa bile önceki gün açılmaz.

## Manuel vardiya ekleme

Dashboarddaki `Manuel Vardiya Ekle` kısayolu
`slot.dashboard.manual.shift.wizard` popup'ını açar. Tarih, restoran, kurye,
giriş/çıkış saatleri ile isteğe bağlı bölge/şube bilgisi alınır. Seçilen
restoran/günde tek ana sabit vardiya varsa kurye bu vardiyaya eklenir. Aynı
kurye ve aynı saat aralığı varsa paket faaliyeti başlamadığı sürece satır
güncellenir; aynı gün içindeki çakışmayan ikinci vardiya ayrı satır açar.
Ana vardiya yoksa Excel importuyla aynı yerel günlük parent vardiya açılır.
Yeni ana vardiya ile ilk kurye satırı aynı `create()` çağrısında atomik olarak
oluşturulur; `Vardiya Oluşturulduğunda ve Güncellendiğinde` otomasyonunun boş
kurye kontrolü nedeniyle parent kaydı önce tek başına oluşturmayın.
Başka vardiyayla kurye saat çakışması, birden fazla ana vardiya, eksik restoran
koordinatı veya aktif kullanıcı hesabı olmayan kurye kaydı engellenir. Var olan
boş parent vardiyada kurye satırı parent write işleminden önce oluşturulur;
böylece `automation_20` boş kurye doğrulamasına hatalı biçimde takılmaz.
Manuel kayıt import batch denetim izi taşır; bu nedenle Vardiyaları Gör,
dashboard ve Personel Paket Beyanları ekranlarında Excel kaydıyla aynı şekilde
yer alır. Dashboarddan manuel vardiya eklenen restoran otomatik olarak
`operation_dashboard_enabled=True` kapsamına alınır.

## Kurye ve restoran hakediş raporu

Dashboarddaki `Kurye / Restoran Hakedişleri` kısayolu
`slot.dashboard.earning.wizard` modelini açar. Yönetici tarih aralığını ve
tüm/belirli/dedike kurye filtresini veya restoran raporu modunda
tüm/belirli/dashboard restoranı filtresini seçer. `Dedike Kuryeler` yalnız
operasyon dashboardu tiki açık restoranlarda ilgili dönemde gerçekten vardiya
başlatmış kuryeleri kapsar. Kurye modunda kayıtlar tekil kurye, restoran
modunda tekil restoran olarak gruplanır.
`grouping_type=combined` dönemin tamamını kişi/restoran başına tek satırda,
`grouping_type=daily` ise kişi/restoran + kullanıcının yerel vardiya tarihi
başına ayrı satırda toplar. Günlük görünüm ekranda tarih, kişi/restoran, paket
ve toplamı gösterir; Excel aynı günlük grupların tüm ücret kırılımlarını taşır.

Restoran borcu restoran kartındaki `restoran_paket_basi_ucret`,
`restoran_saatlik_ucret`, platform kilometre aralıkları ve
`restoran_yuzdelik_kar_orani` ile hesaplanır. Paket beyanı varsa beyan edilen
paket ve mutabakat çalışma saati, yoksa vardiya satırındaki mevcut sayaçlar
kullanılır. Teslim edilen siparişlerde kuryenin müşteriden tahsil ettiği nakit
ve kapıda kart tutarı brüt hizmet bedelinden düşülerek restoranın net borcu
üretilir. Excel çıktısında bu mahsup ayrıca gösterilir.

Paket adedinde iki ayrı garanti tabanı uygulanır. Kurye raporu
`garanti_paket_sayisi`, restoran borcu raporu
`restoran_garanti_paket_sayisi` kullanır. Her raporda paket adedi
`max(gerçek/beyan, ilgili garanti)` olur; garanti `0` ise mevcut davranış
aynen korunur. Kurye beyanı denetim amacıyla değiştirilmez,
`mutabakat_hesaplanan_paket_sayisi` ücretlendirilen adedi taşır.

Ekrandaki özet listede yalnız dönem, kurye/restoran ve toplam gösterilir;
çalışma saati, paket adedi, vardiya, onay ve ücret kırılımları Excel çıktısında
yer alır. `action_export_xlsx()` aktif rapor türü ve filtreleri yeniden
hesaplayarak `.xlsx` indirir. Geçici rapor satırları
`slot.dashboard.earning.line` modelinde tutulur.
Bir grupta birden fazla paket mutabakat durumu varsa teknik değer `mixed`
kalır, kullanıcı etiketi “Birden Fazla Onay Durumu” olur ve Excel hücresinde
mevcut durumlar (`Restoran Onayladı + Restoran Onayı Bekleniyor` gibi) açıkça
yazılır.

Dashboarddaki `Vardiya Puantaj Ekle` kısayolu
`slot.dashboard.attendance.wizard` sihirbazını açar. Tarih varsayılan olarak
dashboard tarihidir. Yalnız operasyon dashboardu işaretli restoranların o
günkü kurye vardiyaları seçilebilir. Girilen ek saat/paket kalıcı olarak
`slots.puantaj.duzeltme` kaydında tutulur ve hakediş ile Excel raporunda ayrı
kolonlarda gösterilir; kurye beyanı ve gerçek giriş/çıkış alanları ezilmez.
`Puantajları Gör` kısayolu dashboardda seçili tarihin ve yalnız dashboard
işaretli restoranların puantaj kayıtlarını liste/form görünümünde açar.

## Ana sayfa davranışı

Kurulum sonrası hook mevcut aktif admin kullanıcıların standart Odoo
`res.users.action_id` alanını dashboard actionına ayarlar. Modül kaldırılırsa
yalnız bu actiona bağlı kullanıcıların alanı temizlenir. Normal kullanıcıların
başlangıç actionı değiştirilmez. Eski `slots` dashboard action ve menüsü de
yalnız ilk kurulum hookunda varsa temizlenir; XML upgrade sırasında eksik
kayıt silme uyarısı üretmeyin.

## Asset kuralları

Template adı `slot_dashboard.OperationDashboard`, action registry etiketi
`slot_dashboard.operation_dashboard` olmalıdır. Global JavaScript
fonksiyonlarını (`parseInt` gibi) OWL template içinde doğrudan çağırmayın;
gösterim değerlerini Python/JS tarafında hazırlayın. Stiller
`.kt-ops-dashboard` altında izole kalmalıdır.

Dashboard root elementi ActionContainer tarafından verilen `o_action`
classını `props.className` üzerinden taşımalı ve
`o_action_delegate_scroll` sınıfını korumalıdır. Action manager tarafından
iletilen `props.className` dıştaki `.kt-ops-action` köküne uygulanır. Odoo ve
tema action taşmasını gizlediği için dikey scroll, bu kökün kalan yüksekliğini
dolduran iç `.kt-ops-dashboard` katmanında yönetilir.

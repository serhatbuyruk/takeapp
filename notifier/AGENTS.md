# Notifier — AI Geliştirme Rehberi

Bu dosya `notifier` modülünde çalışan geliştirici ve yapay zekâ araçları için kalıcı bağlamdır. Modül SMS, push ve sesli arama gibi yardımcı bildirimleri gönderir. En önemli mimari kural: bildirim servisi arızası sipariş, teslimat, slot veya kurye atama transaction'ını bozmamalıdır.

## Güncel sistem özeti — 31 Temmuz 2026

- Canlı sürüm: `16.0.1.8.0`
- Sipariş çağrıları için `../corders/AGENTS.md`, kurye bildirim ekranı için
  `../kuryetec_website/AGENTS.md`, slot uyarıları için
  `../slots/AGENTS.md` dosyasını da okuyun.
- Bildirim yardımcı yan etkidir. Gönderim veya teslimat günlüğü başarısız
  olduğunda ana operasyon transaction'ı mümkün olduğunca devam etmelidir.
- Sağlayıcı anahtarlarını veya gerçek telefon/player ID değerlerini Gemini
  sohbetine, Markdown'a, loga ya da yeni test fixture'ına kopyalamayın.

Gemini/Codex başlangıç sırası: `notifier.profile` metot çağrılarını tüm
addonların Python ve XML action kodlarında ara; dış HTTP'yi mock'lamadan
test çalıştırma; bildirim sonucunu ana sipariş/slot başarısının ön koşulu
yapma; canlı credential'ı kaynak veya çıktıya taşıma.

## Modülün görevi

- Netgsm üzerinden SMS gönderir.
- OneSignal üzerinden tek cihaza push ve sesli push gönderir.
- Netgsm sesli arama isteği oluşturur.
- Gönderim/kallback olaylarını `notifier.profile` üzerinde kaydeder.
- Sipariş ve slot otomasyonları tarafından yardımcı servis olarak çağrılır.

- Manifest: `__manifest__.py`
- Ana model: `models/notifier.py`
- Controller: `controllers/controllers.py`
- Teknik aksiyonlar: `data/technical_actions.xml`

## Modüller arası ilişki

- `corders` sipariş durumu, kurye ataması ve uyarılarda notifier çağırır.
- `slots` slot/kurye operasyonlarında notifier çağırabilir.
- `res.partner.player_id`, OneSignal abonelik/oynatıcı kimliğidir.
- `kuryetec_website` bildirim sayfalarını gösterebilir; gönderim mantığı QWeb'e taşınmamalıdır.

Canlı sistem dört modülü birlikte kullanır. `corders` manifestinde notifier açık bağımlılığı bulunmadığı halde teknik action kodunda `notifier.profile` çağrısı olabilir. Taze kurulum veya test DB'sinde modül yükleme sırasını kontrol edin.

Bu döngüsel bağımlılık nedeniyle `corders -> notifier` doğrudan manifest
bağımlılığı eklemek kolay bir çözüm değildir; `notifier` zaten `corders`a
bağlıdır. Uzun vadeli çözüm ortak bir servis modülü veya opsiyonel çağrı
adaptörüdür. Kapsam dışı bir işte bağımlılığı sessizce değiştirmeyin.

## `notifier.profile`

Temel alanlar ad, açıklama, sıra, enlem ve boylamdır. Model bildirim gönderen yardımcı metotları içerir:

- `_send_http_request`: ortak güvenli HTTP katmanı
- `send_Sms`: Netgsm SMS ve başarılı kayıt oluşturma
- `send_Push_Notification_With_Playerid`: OneSignal push
- `send_Push_Notification_With_Playerid_V1`: başlıklı OneSignal push
- `send_Push_Notification_With_Playerid_Voice`: ses/kanal ayarlı push
- `send_basic_voice_call`: Netgsm sesli arama

Metot imzalarını değiştirmeden önce tüm dört modülde çağrı yerlerini `rg` ile bulun. Eski server/automated action kodu Python dosyalarında görünmeyebilir; `data/technical_actions.xml` dosyalarını da arayın.

## Kurye bildirim teslimat günlüğü

Başarılı OneSignal push çağrıları `notifier.delivery.log` modelinde alıcı kurye bazında kaydedilir. `player_ids`, tek toplu ORM sorgusuyla `res.partner.player_id` alanına eşleştirilir; eşleşen her partner için başlık, içerik, kanal, gönderim zamanı ve player ID anlık değeri tutulur.

- Dış servis isteği başarısızsa teslimat günlüğü oluşmaz.
- Bilinmeyen bir player ID için kurye günlüğü oluşmaz.
- Sesli push `voice_push`, diğer push'lar `push` kanalıyla kaydedilir.
- Manuel `notifier.profile` bildirimi `notifier_source_id` context'iyle kaynak kayda bağlanır.
- Günlük oluşturma hatası savepoint içinde tutulur ve ana sipariş/slot transaction'ını bozmamalıdır.
- Yalnız başarılı OneSignal isteği loglanır; bu kayıt cihazın bildirimi
  gerçekten gösterdiğine dair provider delivery receipt değildir.

`kuryetec_website` `/bildirimler` ekranı bu modeli yalnız oturumdaki partner ve son 12 saat için okur. Website controller dar bir `sudo()` kullanır; partner filtresini kaldırmayın.

## Hata yönetimi sözleşmesi

`_send_http_request` bounded timeout kullanır; mevcut genel değer bağlantı/okuma için `(3, 15)` saniyedir. `requests` kaynaklı bağlantı, timeout ve HTTP hatalarını yakalar, uyarı loglar ve `False` döndürür.

Bilinen teknik borç: mevcut hata logu tam URL'yi yazar ve eski `send_Sms` metodu kimlik bilgilerini query string içinde gönderir. Bu nedenle Netgsm hata anında parola loga düşebilir. Yeni kod bu deseni kopyalamamalı; bu alan düzenlenirken URL/parametreler redakte edilmeli ve sağlayıcının desteklediği güvenli taşıma yöntemi doğrulanmalıdır.

Aktif `notifier/data/technical_actions.xml`, `slots/data/technical_actions.xml`
ve `corders/data/technical_actions.xml` içinde sabit OneSignal/sağlayıcı
değerleri vardır. Bunları bu rehbere taşımayın. Planlı bir migrasyonda
credential'ları şirket/ayar kaydına alın, rotasyonu koordine edin ve XML
action'ları test edilebilir model metoduna indirgeyin.

Yeni veya değişen her bildirim metodu:

- Dış servis hatasında Odoo transaction'ını abort etmemeli.
- Kontrollü timeout kullanmalı.
- Başarı/başarısızlığı açık bir boolean veya belgeli sonuçla bildirmeli.
- Token, parola, SMS şifresi veya tam kişisel veriyi loglamamalı.
- Retry eklenecekse sınırlı ve idempotent olmalı; çift SMS/push üretmemeli.
- Bir cron döngüsünde tek alıcının hatası kalan alıcıları engellememeli.

Siparişin iş durumu, bildirimin başarılı gönderilmesine bağlanmamalıdır. Bildirim “yan etki”dir; ana işlem değildir.

## Sağlayıcılar

### OneSignal

Alıcı kimliği çoğunlukla `res.partner.player_id` üzerinden gelir. Boş veya geçersiz kimlikte servis çağrısı yapmadan başarısız sonuç dönün. HTTP yanıt kodu ve güvenli hata özeti loglanabilir; auth header loglanamaz.

### Netgsm

SMS ve sesli arama farklı payload/endpoint kullanır. XML/URL içeriğini oluştururken telefon formatını doğrulayın. Sağlayıcı kimlik bilgileri bazı eski action/call-site kodlarında sabit bulunabilir. Bunları dokümana veya yeni loglara kopyalamayın. İleride `ir.config_parameter`/ayar modeli migrasyonu yapılabilir; ancak kapsam dışı değişiklikte canlı anahtarı sessizce taşımayın.

## Controller'lar

`/netgsmcallback` public JSON POST callback'idir. Olayı `ir.logging` ve `notifier.profile` üzerinde kaydeder. Public callback değişikliklerinde:

- Sağlayıcının gerçek content type/payload biçimini koruyun.
- Beklenmeyen veya eksik payload'da kontrollü yanıt verin.
- Büyük/zararlı payload'ı olduğu gibi loglamayın.
- Aynı callback tekrar geldiğinde çoğaltma etkisini değerlendirin.

`/notifier/<card_id>` eski bir route'tur ve mevcut olmayan `notifiers.profile`/`qidgenerator` referansları içerebilir. Çalışan temel akış olarak varsaymayın. Kullanıldığı kanıtlanmadan genişletmeyin; düzenlenecekse önce erişim logu, çağrı yeri ve model varlığını doğrulayın.

## Teknik aksiyonlar

`data/technical_actions.xml` içinde aktif `automation_26` (“Bildirim Creation”) bulunur. Test amaçlı cron kayıtları (`cron_45`, `cron_60`, `cron_71`) inaktiftir. Aynı isimli veya eski kopyalara güvenmeyin; external ID ve `active` alanını doğrulayın.

`automation_26`, manuel `notifier.profile` kaydının hedef kullanıcılarını
`x_user` üzerinden player ID'lere çevirir ve push gönderir. Website
`/bildirimler` sayfası yeni gönderimleri `notifier.delivery.log` üzerinden,
geçiş dönemi eski kayıtlarını ise sınırlı fallback ile gösterebilir.

Teknik action içindeki Python kodu normal model metodu kadar üretim kodudur. Karmaşık yeni mantığı action code alanına eklemek yerine test edilebilir model metoduna taşıyın; action yalnızca metodu çağırsın.

## Performans kuralları

- Request başına yeni HTTP oturumu/retry fırtınası üretmeyin.
- Çoklu alıcı gönderiminde ORM kayıtlarını toplu alın; döngüde partner `search` yapmayın.
- Dış çağrıyı SQL kilidi altında yapmayın.
- Cron batch boyutunu sınırlayın ve işlendi işaretini idempotent tutun.
- Sağlayıcı gecikmesini kullanıcıya açık HTTP route'larda zincirlemeyin; iş gereği zorunlu değilse transaction sonrası/cron tabanlı akış düşünün.
- Log tablosunu sınırsız büyütecek debug payload'larından kaçının.

Canlı DB'de `ir_logging` ve ileti/chatter tabloları büyüktür. Bir dakikalık
slot/sipariş cron'larında alıcı başına başarı logu veya ham provider payload'ı
eklemeyin. Teslimat günlüğünün saklama süresi ayrıca ürün kararı olarak
belirlenmelidir; kurye ekranının yalnız son 12 saati göstermesi eski
kayıtların DB'den otomatik silindiği anlamına gelmez.

## Test yaklaşımı

Teslimat günlüğü testleri `tests/test_delivery_log.py` içindedir. Yeni testlerde tüm dış HTTP çağrılarını mock'layın.

Mevcut dosyada 5 test metodu vardır; delivery receipt, retry/idempotency ve
uzun süreli retention senaryoları kapsam dışıdır. Test sayısını eksiksiz
sağlayıcı garantisi olarak yorumlamayın.

Asgari senaryolar:

- Başarılı SMS/push
- Timeout
- Bağlantı hatası
- 4xx/5xx yanıtı
- Geçersiz JSON
- Boş `player_id`
- Eksik telefon/kimlik bilgisi
- Aynı callback'in tekrarı
- Bildirim başarısızken ana sipariş işleminin devam etmesi

Gerçek Netgsm veya OneSignal hesabına test mesajı göndermeyin. Üretim DB'sinde Odoo test runner çalıştırmayın; geçici klon kullanın.

## Güvenli geliştirme kontrol listesi

1. Metot çağrılarını Python ve tüm `technical_actions.xml` dosyalarında arayın.
2. Bildirim hatasının caller'a exception taşımadığını test edin.
3. Timeout olduğunu ve credential'ın loglanmadığını doğrulayın.
4. Public callback'in eksik/verimsiz payload'a dayanıklı olduğuna bakın.
5. XML, Python ve security dosyalarını doğrulayın.
6. Kod/XML değişikliğinde manifest sürümünü artırın.

## Dağıtım

Kaynak dizini `/odoo/odoo16/kuryetec-custom-addons`; eski `/odoo/odoo16/odoo-custom-addons` kopyasını kullanmayın.

- Config: `/etc/odoo16-kuryetec.conf`
- Database: `kuryetec`
- Service: `odoo16-kuryetec.service`
- Log: `/var/log/odoo/odoo16-kuryetec.log`

```bash
systemctl stop odoo16-kuryetec.service
sudo -u odoo /odoo/odoo16/odoo-venv/bin/python3 /var/lib/odoo/odoo-bin \
  -c /etc/odoo16-kuryetec.conf -d kuryetec -u notifier \
  --stop-after-init --no-http
systemctl start odoo16-kuryetec.service
```

Upgrade sonrası loglarda traceback ve HTTP provider hatalarını ayırarak inceleyin. Bildirim sağlayıcısının geçici hatası modül upgrade hatası değildir. Sadece `.md` değişikliğinde restart/upgrade gerekmez.

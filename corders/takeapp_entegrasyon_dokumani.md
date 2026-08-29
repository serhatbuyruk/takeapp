# Takeapp - Odoo Sipariş ve Kurye Entegrasyon Dokümantasyonu

Bu doküman, Odoo `corders` modülü içerisinde Takeapp sistemi için kurgulanmış olan sipariş ve kurye durum güncellemeleri entegrasyonu hakkında teknik bilgileri içermektedir. Doküman, Takeapp tarafındaki yazılım mühendislerine iletilmek üzere hazırlanmıştır.

## 1. Sistem Yapılandırması ve Kimlik Doğrulama
Odoo tarafında Takeapp entegrasyonunun aktif olması için ilgili mağazanın (veya genel şirket ayarlarının) yapılandırılmış olması gerekir. Odoo arayüzü üzerinden mağaza veya şirket ayarlarında aşağıdaki bilgiler girilir:

* **Pos Entegrasyon Firması (`pos_entegrasyon_firmasi`):** Entegrasyonun devreye girmesi için bu alan "Takeapp" olarak seçilmelidir.
* **Takeapp Bayi Id (`takeapp_bayi_id`):** Takeapp sisteminde mağazayı tanımlayan benzersiz ID. (Örn: `tdm07`)
* **Takeapp Url (`takeapp_url`):** Odoo'nun kurye durum güncellemelerini göndereceği hedef Takeapp API URL'si. (Örn: `https://www.tazeyo.com.tr/courier/api`)
* **Takeapp Api Key (`takeapp_api_key`):** İsteklerde kimlik doğrulaması (Authentication) için kullanılacak olan, `x-api-key` header'ına eklenecek gizli anahtar. (Örn: `e27b42f6547db8a35871a5bb53453ffff`)

**İşleyiş Mantığı:**
Odoo'dan Takeapp'a istek atılırken yukarıda girilen mağazaya özel değerler kontrol edilir. 
* Eğer mağazanın formunda özel bir `takeapp_url` girilmişse, bu URL hedef alınır *(Örn: https://www.tazeyo.com.tr/courier/api)*.
* Şayet mağazanın özel bir `takeapp_url`'i tanımlanmamışsa (boş geçilmişse), sistem varsayılan olarak Odoo şirket ayarlarında (Company) kayıtlı olan genel URL ve API Key'i `x_takeapp_url` ile kullanarak şu şekilde dinamik bir yol oluşturur: `{COMPANY_TAKEAPP_URL}/v1/couries/{TAKEAPP_ORDER_ID}`

---

## 2. Takeapp'dan Odoo'ya Sipariş Gönderimi (Odoo API Uç Noktaları)

Takeapp sistemi, Odoo sistemine sipariş oluşturma veya iptal bildirimlerini aşağıdaki uç noktalara (endpoint) **HTTP POST** metoduyla ve JSON formatında gönderir.

### 2.1. Yeni Sipariş Oluşturma
* **URL:** `{ODOO_BASE_URL}/takeapp-order`
* **HTTP Metodu:** `POST`
* **Content-Type:** `application/json`
* **Gövde (Body):** Siparişin tüm detaylarını içeren JSON verisi. *(İpucu: Odoo doğrudan request raw datasını `json.loads` ile okumaktadır)*
* **İşleyiş:** Odoo, gelen isteği işleyip veritabanındaki `ir.logging` tablosuna `takeapp_send_order` (veya hata çıkarsa `takeapp_send_order_error`) etiketiyle kayıt eder. Odoo içerisindeki diğer asenkron süreçler/zamanlanmış görevler bu loglara bakarak siparişin detaylarını ayrıştırıp asıl sipariş kayıtlarını oluşturur.
* **Başarılı Yanıt:** `{"message": "Order Created Successfully"}` (HTTP 200)

### 2.2. Sipariş İptali
* **URL:** `{ODOO_BASE_URL}/takeapp-cancel-order`
* **HTTP Metodu:** `POST`
* **Content-Type:** `application/json`
* **Gövde (Body):** İptal edilen sipariş verisini veya ID'sini içeren JSON.
* **İşleyiş:** İlgili iptal isteği log tablosuna `takeapp_cancel_order` kaydı olarak aktarılır.
* **Başarılı Yanıt:** `{"message": "Status Created Successfully"}` (HTTP 200)

---

## 3. Odoo'dan Takeapp'a Sipariş Durum Bildirimleri (Takeapp API İstekleri)

Kurye, mobil cihazındaki kurye arayüzü üzerinden işlem yaptığında (Siparişi Teslim Aldı veya Siparişi Teslim Etti), Odoo sistemi Takeapp sistemine doğru HTTP POST isteği başlatır.

### İstek Hedef URL (Endpoint) Kuralları:
Takeapp'a yapılacak isteklerde URL dinamik olarak oluşturulur.
* Eğer mağazada özel bir URL tanımlanmışsa (Örn: `siparis.magaza.takeapp_url` verisi `https://custom.takeapp.api/v2/update` gibi): **Doğrudan bu URL kullanılır.**
* Eğer mağazada özel URL tanımlanmamışsa Odoo şirket ayarlarındaki ana URL ele alınır ve dinamik yol oluşturulur: `{COMPANY_TAKEAPP_URL}/v1/couries/{TAKEAPP_ORDER_ID}`

### İstek Başlıkları (Headers)
İki durum bildirimi için de Odoo aşağıdaki header değerlerini gönderir:
* `x-api-key`: {Sisteme tanımlanmış olan Takeapp API Key}
* `Content-Type`: `application/json`

### 3.1. Kurye Siparişi Teslim Aldı (Picked Up)
Kurye restorandan paketi teslim aldığını onayladığında tetiklenir.
* **HTTP Metodu:** `POST`
* **Payload (JSON):**
```json
{
    "order_status": 3
}
```

### 3.2. Kurye Yola Çıktı (Out for Delivery)
Kurye paketi alıp teslimata başladığında gönderilen durum bilgisidir. (Odoo içerisinde sipariş durumu "yola_cikti" vb. olduğunda gönderilecek değerdir).
* **HTTP Metodu:** `POST`
* **Payload (JSON):**
```json
{
    "order_status": 2
}
```
*(Not: 2 kodu örnek olarak verilmiştir, Takeapp'un kendi sisteminde kabul ettiği statü numarası ne ise Odoo o sayıyı gönderir veya Takeapp tarafı gelen bu numaraları kendi altyapısına göre eşleştirmelidir.)*

### 3.3. Kurye Siparişi Teslim Etti (Delivered)
Kurye paketi müşteriye teslim ettiğini onayladığında tetiklenir.
* **HTTP Metodu:** `POST`
* **Payload (JSON):**
```json
{
    "order_status": 4
}
```

---

## 4. Takeapp Tarafında (Karşı Tarafta) Controller Nasıl Olmalı?

Takeapp tarafındaki yazılım mühendisleri, Odoo'dan atılacak olan durum güncellemelerini (Teslim Alındı / Yola Çıktı / Teslim Edildi) alabilmek için kendi sistemlerinde yukarıdaki payloada uygun bir uç nokta tasarlamalıdır.

**Örnek bir Takeapp Endpoint Beklentisi:**

* Odoo yukarıdaki örnekteki gibi tanımlanmış URL'ye (veya şablona uygun ID ile: `/v1/couries/TAKEAPP_ORDER_ID`) `POST` isteği atar.
* İstek yapıldığında Odoo `header` içinde `x-api-key` gönderir. Sistemde kimlik doğrulama bu gizli anahtarla kontrol edilmelidir.
* Gelen JSON içerisindeki `order_status` parametresi ayrıştırılmalı ve Takeapp sistemindeki ilişkili kurye/sipariş verisi güncellenmelidir. Olası durumlar:
  * **2** : Sipariş Yola Çıktı (Kuryede)
  * **3** : Sipariş Restorandan Teslim Alındı
  * **4** : Sipariş Müşteriye Teslim Edildi
* *(Önemli)* Odoo'nun bu işlem için bekleme süresi **5 saniyedir** (Timeout). Eğer Takeapp 5 saniye içerisinde cevap vermezse, Odoo isteği kopararak loglara hata (timeout) yazacaktır. Bu yüzden Takeapp tarafındaki endpoint işlemlerini asenkron yürütüp (message queue vb.) isteğe hızlıca HTTP 200 dönmelidir.

**Örnek (Node.js/Express) Controller Mantığı:**

Bu örnek kodda, Odoo'dan gönderilen `/v1/couries/{orderId}` uç noktasını ele aldık:

```javascript
app.post('/v1/couries/:orderId', (req, res) => {
    const apiKey = req.headers['x-api-key'];
    const { orderId } = req.params;
    
    // 1. Kimlik Doğrulama
    if (apiKey !== "Beklenen_Gizli_Anahtar") {
        return res.status(401).json({ error: "Unauthorized" });
    }

    // 2. Odoo'dan gelen payloadı ayrıştırma
    const { order_status } = req.body;
    
    // 3. Sipariş Durumlarına (Status) Göre Senaryolar
    switch (order_status) {
        case 2:
            // Siparişi "Kurye Yola Çıktı / Teslimata Başladı" olarak güncelle
            console.log(`[Order: ${orderId}] Status: Out for delivery`);
            break;
        case 3:
            // Siparişi "Kurye Restorandan Paketi Teslim Aldı" olarak güncelle
            console.log(`[Order: ${orderId}] Status: Picked up`);
            break;
        case 4:
            // Siparişi "Kurye Müşteriye Paketi Teslim Etti" olarak güncelle
            console.log(`[Order: ${orderId}] Status: Delivered`);
            break;
        default:
            console.warn(`[Order: ${orderId}] Status: Bilinmeyen bir durum geldi (${order_status})`);
            break;
    }

    // 4. Timeout'a düşmemek için beklemeden yanıt dönme!
    return res.status(200).json({ code: "ok", message: "Status handled successfully" });
});
```

*(Ek Not: Müşteriye ve Odoo altyapısına giden tüm kurye durum istekleri `ir.logging` (Scheduled Actions & Server Logs) altında kayıt edilmektedir. Olası bir entegrasyon hatasında Odoo panelinden bu loglar incelenerek gönderilen data görülebilir.)*

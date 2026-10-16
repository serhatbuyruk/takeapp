# Kurye Görüşmesi TURN Kurulumu

Bu modül, Odoo Discuss/WebRTC altyapısını kullanır. Ses ve goruntu normalde iki
cihaz arasında dogrudan akar. Mobil operatör NAT'ı, kurumsal Wi-Fi veya WebView
kısıtları dogrudan bağlantıyı bozabilir ya da tek yönlü sese neden olabilir.

Bu doküman, medya trafigini gerektiginde röleleyen `coturn` servisini ve Odoo
16 ICE ayarlarını yeni bir sunucuya tasımak içindir.

## Ag Gereksinimleri

Sunucunun genel IP'si ve bir DNS adı olmalıdır. Asagıdaki portları hem sunucu
güvenlik duvarında hem de sağlayıcının harici güvenlik duvarında açın:

| Protokol | Portlar | Amaç |
| --- | --- | --- |
| UDP, TCP | `3478` | TURN/STUN baglantısı |
| UDP | `49160-49200` | TURN medya rölesi |

TLS destekli TURN gerekirse ayrıca `5349` TCP/UDP ve geçerli bir sertifika
yapılandırılır. Mevcut kurulum UDP/TCP 3478 ile çalısır.

## Coturn Kurulumu

Ubuntu/Debian üzerinde:

```bash
apt-get update
apt-get install -y coturn
```

`/etc/turnserver.conf` dosyasını asagıdaki gibi olusturun. Yer tutucuları yeni
sunucunun genel IP'si, alan adı ve güçlü bir parola ile degistirin.

```ini
listening-port=3478
listening-ip=<PUBLIC_IP>
relay-ip=<PUBLIC_IP>
external-ip=<PUBLIC_IP>

fingerprint
lt-cred-mech
realm=<TURN_DOMAIN>
server-name=<TURN_DOMAIN>
user=<TURN_USERNAME>:<STRONG_TURN_PASSWORD>

min-port=49160
max-port=49200
total-quota=120
user-quota=8

no-loopback-peers
no-multicast-peers
no-cli
stale-nonce
simple-log
```

Servisi etkinlestirip baslatın:

```bash
systemctl enable --now coturn
systemctl restart coturn
systemctl is-active coturn
ss -lunpt | grep 3478
```

Sunucu NAT arkasındaysa `external-ip` alanını
`<PUBLIC_IP>/<PRIVATE_IP>` biçiminde yazın. Genel IP'li sunucularda yalnızca
`<PUBLIC_IP>` yeterlidir.

## Odoo 16 ICE Sunucuları

Odoo'da gelistirici modu ile su menüden kayıtları girin:

`Ayarlar > Teknik > Discuss > ICE Servers`

Alternatif olarak `Ayarlar > Genel Ayarlar > Discuss > Custom ICE server list`
baglantısı kullanılabilir.

En fazla bes kayıt kullanın. Asagıdaki dört kayıt önerilir:

| Tür | URI | Kullanıcı adı | Parola |
| --- | --- | --- | --- |
| `stun` | `stun1.l.google.com:19302` | Bos | Bos |
| `stun` | `stun2.l.google.com:19302` | Bos | Bos |
| `turn` | `<TURN_DOMAIN>:3478?transport=udp` | `<TURN_USERNAME>` | TURN parolası |
| `turn` | `<TURN_DOMAIN>:3478?transport=tcp` | `<TURN_USERNAME>` | TURN parolası |

Odoo URI'nin basına türü kendisi ekler. Bu nedenle URI alanına `turn:` veya
`stun:` yazmayın.

Bu kayıtlar veritabanında `mail.ice.server` modelinde tutulur ve her yeni
görüsme baslatılırken tarayıcıya gönderilir. Odoo servisini yeniden baslatmak
gerekmez; açık görüsme sayfalarını kapatıp yeni görüsme baslatmak gerekir.

## Dogrulama

TURN kimlik dogrulamasını sunucudan deneyin:

```bash
turnutils_uclient -v \
  -u <TURN_USERNAME> -w '<STRONG_TURN_PASSWORD>' \
  -p 3478 -n 1 -e 1.1.1.1 -r 53 <PUBLIC_IP>
```

Çıktıda `allocate response received` ve `Received relay addr` görülmelidir.
Ardından iki telefonda yeni kurye görüsmesi baslatın. Dogrudan bağlantı uygun
degilse WebRTC TURN rölesine düser.

## Güvenlik ve Bakım

- Bu dosyaya, Git'e veya Odoo modül koduna gerçek TURN parolası yazmayın.
- Statik kullanıcı/parola, görüsmeye katılan istemcilere WebRTC ayarı olarak
  gönderilir. Üretimde düzenli parola degisikligi yapın.
- Daha yüksek güvenlik ve büyük kullanım için coturn TURN REST API ile kısa
  ömürlü kimlik bilgisi üretilecek ayrı bir Odoo uzantısı tercih edilmelidir.
- `journalctl -u coturn -f` ile aktif röle tahsislerini izleyebilirsiniz.
- Odoo tarafında `mail.ice.server` kayıtları silinirse sistem yalnızca varsayılan
  Google STUN sunucularına döner; TURN rölesi kullanılmaz.

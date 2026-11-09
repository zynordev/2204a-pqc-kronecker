<p align="center">
  <img src="docs/assets/banner.svg" alt="PQC-Drop" width="100%">
</p>

<p align="center">
  <a href="https://github.com/zynordev/2204a-pqc-kronecker/releases/latest"><img src="https://img.shields.io/github/v/release/zynordev/2204a-pqc-kronecker?style=for-the-badge&color=EF4444&labelColor=0A0A0A" alt="release"></a>
  <img src="https://img.shields.io/badge/NIST-FIPS%20203%20ML--KEM-FAFAFA?style=for-the-badge&labelColor=0A0A0A" alt="FIPS 203">
  <img src="https://img.shields.io/badge/testler-1884%20ge%C3%A7ti-FAFAFA?style=for-the-badge&labelColor=0A0A0A" alt="tests">
  <img src="https://img.shields.io/badge/Linux%20%C2%B7%20Raspberry%20Pi-FAFAFA?style=for-the-badge&labelColor=0A0A0A" alt="platform">
</p>

<p align="center"><b>Aynı ağdaki cihazlara dosya gönder. Şifreleme, bir kuantum bilgisayar geldiğinde de dayansın.</b></p>

<p align="center">
  <a href="https://github.com/zynordev/2204a-pqc-kronecker/releases/latest"><b>⬇ İndir (kurulum yok)</b></a> ·
  <a href="#nasıl-çalışır">Nasıl çalışır</a> ·
  <a href="#kanıt-şifreli-mi-gerçekten">Kanıt</a> ·
  <a href="#dürüst-sonuçlar">Dürüst sonuçlar</a>
</p>

---

## Neden var?

Bugün şifrelenip kaydedilen trafik, yıllar sonra yeterince büyük bir kuantum bilgisayarla çözülebilir.
Buna **"şimdi topla, sonra çöz"** (harvest now, decrypt later) deniyor. Bugünkü anahtar değişimi yöntemlerinin çoğu (RSA, X25519) kuantumda kırılır.
NIST 2024'te bunun için **ML-KEM**'i (FIPS 203) standartlaştırdı.

**PQC-Drop**, bu standardı gerçek bir işe koyar: yakındaki cihazı otomatik bulur, tek tıkla dosya yollar ve **şifrelemenin gerçekten çalıştığını ekranda canlı gösterir**.

## 30 saniyede dene

```bash
# 1. İndir ve aç (Python / kütüphane kurulumu gerekmez)
tar -xzf pqc-drop-v1.0.0-linux-x86_64.tar.gz && cd pqc-drop-v1.0.0-linux-x86_64

# 2. Başlat — iki cihazda da çalıştır, birbirini kendisi bulur
./run-gui.sh      # masaüstü arayüzü
./run-tui.sh      # terminal / SSH arayüzü (Raspberry Pi'de de çalışır)
```

> Güvenlik duvarı: **UDP 8766** (keşif) ve **TCP 8787–8802** (aktarım) açık olmalı.
> Paket Linux x86_64 içindir. Diğer platformlarda kaynaktan çalıştır ([aşağıda](#kaynaktan-çalıştır)).

## Ne yapar?

| | |
|---|---|
| 📡 **Otomatik keşif** | Aynı ağdaki cihazlar birbirini bulur. Her cihazın bir adı var, istersen **görünmez** olursun. |
| 🔐 **Kuantuma dayanıklı** | ML-KEM-768 anahtar değişimi + AES-256-GCM + SHA-256 bütünlük doğrulaması. |
| 🔬 **Canlı denetçi** | Wireshark tarzı paket listesi, 16 baytlık hex/ASCII dökümü ve Shannon entropi ölçer. |
| 🖥️ **İki arayüz** | Siyah-beyaz, keskin köşeli masaüstü GUI ve headless cihazlar için ASCII terminal arayüzü. |
| 🎓 **Anlatan arayüz** | "Nasıl çalışır?" sekmesinde lise düzeyinde küçük simülatörler. |

## Nasıl çalışır?

```mermaid
sequenceDiagram
    participant A as Gönderen
    participant B as Alıcı
    A-->>B: UDP 8766 · "ben buradayım" (keşif)
    B-->>A: UDP 8766 · "ben de" (BEACON_REPLY)
    A->>B: TCP 8787 · bağlan
    B->>A: ML-KEM-768 açık anahtar (1184 bayt)
    A->>B: ML-KEM kapsülü (1088 bayt)
    Note over A,B: iki taraf aynı gizli anahtarı türetir
    A->>B: AES-256-GCM ile 64 KB parçalar
    B->>A: SHA-256 doğrulama
```

Ağdan geçen her bayt şifreli parçalardır. Anahtar hiç ağa çıkmaz, yalnızca KEM kapsülü gider.

## Kanıt: şifreli mi gerçekten?

Aynı 16 KB'lık içerik üç şekilde gerçek TCP soketiyle yollandı ve `.pcap` olarak kaydedildi ([deney 05](experiments/05-ag-analizi/sonuc.md)):

| | Düz HTTP | TLS 1.3 | **PQC-Drop** |
|---|:---:|:---:|:---:|
| Shannon entropisi (maks. 8) | 4,130 | 7,989 | **7,992** |
| Wireshark'ta düz metin araması | ⚠️ ifşa | ✅ 0 eşleşme | ✅ 0 eşleşme |
| Açık anahtar boyutu | — | 32 bayt | 1184 bayt |
| Kuantuma karşı (Shor) | yok | ❌ kırılır (X25519) | 🛡️ dirençli (kafes tabanlı) |
| Toplam trafik | 16 493 B | 16 435 B | 18 684 B |

Entropi 8'e ne kadar yakınsa veri o kadar rastgele görünür, yani okunabilir bir şey sızmıyor. Bedeli: TLS 1.3'e göre ~2,2 KB ek trafik (1184 baytlık açık anahtar + 1088 baytlık kapsül).
Kendin de bakabilirsin: `tcpdump -r experiments/05-ag-analizi/pqcdrop_gercek.pcap`

## Altındaki fikir: Kronecker ikamesi

ML-KEM'in en sık yaptığı iş polinom çarpımıdır. Biz bunu klasik NTT yerine **Kronecker ikamesiyle** yapıyoruz:
polinomun tüm katsayılarını tek bir dev tamsayıya paketle, tek seferde çarp, sonucu geri aç.

Kilit nokta, katsayıların **ne kadar yer kapladığı**:

- Klasik paketleme katsayı başına **32 bit** ayırır.
- ML-KEM'de çarpanlardan biri hep küçüktür (gizli vektör). Katsayıları sıfırın çevresinde (işaretli) tutunca ayrılması gereken alan **22 bite** iner (η=3; η=2'de 21 bit).
- Gereken genişlik kesin bir formülle ispatlandı: `ℓ_min = bitlen(n·A·η) + 1`. Bir bit eksik olursa çarpım bozulur ([docs/04-teori.md](docs/04-teori.md)).

Yeni bir şifreleme algoritması icat etmedik. NIST standardının içindeki çarpımı, literatürdeki bir yöntemin merkezlenmiş varyantıyla inceledik.

## Dürüst sonuçlar

Bu bölüm bilerek abartısızdır:

| Ölçüm | Sonuç |
|---|---|
| Sadece büyük tamsayı çarpımı (32→22 bit) | **2,05× daha hızlı** (20,35 → 9,94 µs) |
| Tek polinom çarpımı, saf Python | Kronecker, Python NTT'den **2,2× hızlı** |
| Tam ML-KEM-768 (KeyGen+Encaps+Decaps) | Kronecker **0,85×**, yani standart NTT daha hızlı |
| ESP32 (gerçek donanım, 100 çalıştırma) | Kronecker/Comba okul yöntemine göre **0,81×**; sonuçlar %100 doğru |
| Bellek | Paketlenen alan 8192 → 5632 bit (%31 küçük); ama Python'da tepe tahsis **%56,9 arttı** |

**Yani:** yöntem matematiksel olarak doğru ve çarpma adımı gerçekten hızlanıyor. Ancak veriyi NTT alanına/alanından dönüştürmek bu kazancı yiyor, bu yüzden ML-KEM'in tamamında standart yöntem hâlâ önde. Bunu saklamıyoruz.

Bir bulgu daha: sınırın **altına** inmek sadece hata değil, güvenlik açığı. Seçilmiş girdilerle çarpımın bozulup bozulmaması gizli anahtarın normuna bağlı hâle geliyor ([deney 03](experiments/03-guvenlik/sonuc.md)). Kısaca: bit sayısı keyfî seçilemez.

## Güvenlik notu

PQC-Drop bir **araştırma prototipidir**: bağımsız güvenlik denetiminden geçmedi. Önemli veriler için denetlenmiş araçları kullan. ML-KEM kısmı NIST'in resmî test vektörlerinin hepsini (225/225) geçer, ancak bu bütün sistemin güvenli olduğunu kanıtlamaz.

## Kaynaktan çalıştır

```bash
git clone https://github.com/zynordev/2204a-pqc-kronecker.git && cd 2204a-pqc-kronecker
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
pytest                 # 1884 test
./pqcdrop-gui.sh       # PyQt6 gerekir; yoksa TUI'ye düşer
./pqcdrop-tui.sh
```

Kendi paketini derlemek için: `pip install pyinstaller && pyinstaller --onefile --paths src src/pqc/gui.py`

## Depo haritası

```
src/pqc/        ML-KEM, çarpım yöntemleri ve PQC-Drop (engine · discovery · gui · tui)
tests/          NIST ACVP vektörleri dahil otomatik testler
experiments/    00 ön ölçüm · 01 doğruluk · 02 teori · 03 güvenlik · 04 performans
                05 ağ analizi (.pcap) · 06 IoT benchmark · 07 ESP32 donanım
docs/           teori, literatür, raporlar, kararlar (ADR)
```

Daha derin okumak için: [teori ve ispatlar](docs/04-teori.md) · [sadeleştirilmiş rapor](docs/rapor-sade.md) · [literatür](docs/02-literatur.md) · [IoT mimarisi](docs/mimari-iot.md)

---

<sub>Bu çalışma bir **TÜBİTAK 2204-A** lise araştırma projesi olarak başladı; proje dokümanları [`docs/`](docs/) ve [`danisman/`](danisman/) altında duruyor. Yazar: Halil Erdem Yanık · [ZynorDev](https://github.com/zynordev)</sub>

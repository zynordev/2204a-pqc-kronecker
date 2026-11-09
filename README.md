# PQC-Kronecker — Kuantum Sonrası Anahtar Kapsüllemede Merkezlenmiş Kronecker İkamesi

[![Release](https://img.shields.io/github/v/release/zynordev/2204a-pqc-kronecker?style=flat-square)](https://github.com/zynordev/2204a-pqc-kronecker/releases/latest)
![Testler](https://img.shields.io/badge/pytest-1884%20ge%C3%A7ti-brightgreen?style=flat-square)
![NIST](https://img.shields.io/badge/NIST%20FIPS%20203-ML--KEM-black?style=flat-square)

TÜBİTAK 2204-A Lise Öğrencileri Araştırma Projeleri Yarışması projesi.

**Güncel okunabilir rapor:** [docs/rapor-sade.md](docs/rapor-sade.md) (danışman geri bildirimiyle sadeleştirilmiş; ispatlar ve ayrıntılı tablolar [teknik taslakta](docs/taslakfable.md) korunur).

## ⬇️ İndir (kurulum gerektirmez)

**[PQC-Drop v1.0.0 — Releases](https://github.com/zynordev/2204a-pqc-kronecker/releases/latest)** · Linux x86_64 · `.tar.gz` veya `.zip` (~132 MB)

```bash
tar -xzf pqc-drop-v1.0.0-linux-x86_64.tar.gz && cd pqc-drop-v1.0.0-linux-x86_64
./run-gui.sh    # masaüstü arayüzü (VoiceBox tasarımı)
./run-tui.sh    # terminal / SSH arayüzü (ör. Raspberry Pi)
```

Python veya PyQt6 kurulumu gerekmez (PyInstaller ile paketlenmiştir). Aynı ağdaki iki cihazda çalıştırınca birbirini otomatik bulur.
Güvenlik duvarında **UDP 8766** (keşif) ve **TCP 8787–8802** (aktarım) açık olmalıdır.

## Problem ve yaklaşım

**Problem.** Bugün şifrelenip kaydedilen veriler, ileride yeterince büyük bir kuantum bilgisayarla çözülebilir
("şimdi topla, sonra çöz"). NIST bu yüzden 2024'te kuantum sonrası anahtar kapsülleme standardı
**FIPS 203 (ML-KEM)**'i yayımladı. ML-KEM'in temel işlemi, `Z_3329[X]/(X^256+1)` halkasında polinom çarpımıdır.

**Ne yapıyoruz.** Bu çarpımı, polinomları tek bir büyük tamsayıya paketleyip tek seferde çarpan
**Kronecker ikamesi** ile yapıyoruz. ML-KEM'de çarpanlardan biri hep küçük katsayılı (gizli vektör)
olduğundan katsayıları merkezlenmiş (işaretli) tutarak paketleme genişliğini 32 bitten **22 bite** (η=3) indirebiliyoruz.
Gereken genişlik: **ℓ_min = bitlen(n·A·η) + 1** (Teorem 1, [docs/04-teori.md](docs/04-teori.md)); n=256, A=1664, η=3 için 22, η=2 için 21 bit.

> Yeni bir şifreleme algoritması icat etmiyoruz. NIST standardını temel alıyor, standardın içindeki
> çarpım işlemini literatürdeki bir yöntemin merkezlenmiş varyantıyla inceliyoruz.

## Bulgular (ölçülmüş, dürüst özet)

| Konu | Sonuç | Kayıt |
|---|---|---|
| Genişlik sınırı | 22 bit yeterli ve keskin (21 bit yetmez); 200.000 denemeyle doğrulandı | [E2](experiments/02-teori-deney/) |
| Doğruluk | 8 varyantın hepsi 10.000 örnekte ve 225 NIST vakasında doğru | [E1](experiments/01-dogruluk/) |
| Yalnız bigint çarpımı | 32→22 bit: 20,35 → 9,94 µs (**2,05×**) | [E3](experiments/04-performans/sonuc.md) |
| Uçtan uca ML-KEM-768 (x86, Python) | Kronecker NTT'den **yavaş: 0,85×** (dönüşüm maliyeti) | [E7 IoT](experiments/06-iot-benchmark/sonuc.md) |
| ESP32 (gerçek donanım, 100 çalıştırma) | Kronecker/Comba okul yöntemine göre **0,81×**; sonuç %100 doğru | [ESP32](experiments/07-esp32-donanim/sonuc.md) |
| Sınırın altı (H4) | Hata, gizli anahtarın normuna bağlı → yalnız hata değil **güvenlik açığı** | [E4](experiments/03-guvenlik/sonuc.md) |

Kısaca: yöntem matematiksel olarak doğru ve paketleme küçülüyor, ancak ML-KEM'in tamamında standart NTT hâlâ daha hızlı. Python'daki %56,9 tepe bellek artışı da bellek tasarrufu anlamına gelmiyor; 768 bayt çalışma alanı kuramsal modeldir.

## PQC-Drop — güvenli dosya aktarım prototipi

ML-KEM-768 el sıkışması + AES-256-GCM (64 KB parçalar) + SHA-256 bütünlük doğrulaması. Varsayılan motor: `isaretli24-bayt-negmod`.

- **Otomatik keşif:** UDP 8766, tüm alt ağlara broadcast + doğrudan `BEACON_REPLY`; cihaz adı ve **görünür / gizli** modu.
- **Canlı paket denetçisi:** Wireshark benzeri 16 baytlık hex/ASCII dökümü ve Shannon entropisi.
- **İki arayüz:** PyQt6 GUI (VoiceBox tasarım sistemi, keskin köşeler, siyah/beyaz + `#EF4444`) ve curses ASCII TUI (headless Raspberry Pi / SSH).
- **GUI sekmeleri:** Aktarım & ağ denetimi · literatür/rakip kıyası · "Nasıl çalışır?" (9. sınıf düzeyi simülatörler).
- **Gerçek ağ kanıtı:** 16 KB aynı yükle HTTP / TLS 1.3 / PQC-Drop karşılaştırması, `.pcap` dosyalarıyla ([E5](experiments/05-ag-analizi/sonuc.md)):

| | Düz HTTP | TLS 1.3 | PQC-Drop |
|---|---|---|---|
| Shannon entropisi | 4,130 | 7,989 | 7,992 |
| Wireshark'ta düz metin | açık | yok | yok |
| Kuantum (Shor) | yok | kırılır (X25519) | dirençli (M-LWE) |

CLI sürümü: `pqcdrop` (`python -m pqc.pqcdrop`).

## Durum

**Başvuru son tarihi: 4 Ocak 2027, 17.30** · hedef yükleme: 2 Ocak 2027

| Aşama | Konu | Durum |
|---|---|---|
| 0 | Repo, plan, dokümanlar, ön ölçüm | 🟡 iskelet + CI hazır, danışman toplantısı bekliyor |
| 1 | Literatür + teori (ispat) | 🟡 Lemma 1 / Teorem 1 yazıldı, B'nin kontrolü ve künye doğrulama bekliyor |
| 2 | Referans ML-KEM (NTT) + NIST vektörleri | 🟡 225/225 geçti, kod okuma bekliyor |
| 3 | Kronecker motorları + ML-KEM entegrasyonu | 🟡 8 varyant, her biri 225/225, kod okuma bekliyor |
| 4 | Deneyler (H2–H4) | 🟢 Tamamlandı |
| 5a | PQC-Drop prototip (CLI) | 🟢 Tamamlandı |
| 5b | GUI + TUI + ağ keşfi + canlı denetçi | 🟢 **v1.0.0 yayında** (9 Kasım 2026) |
| 6 | Rapor | 🟡 [rapor-sade](docs/rapor-sade.md) güncel; kaynak doğrulama ve YZ beyanı bekliyor |
| 7 | IoT/Edge benchmark + gerçek ESP32 ölçümü | 🟢 Tamamlandı (8 Kasım) |
| — | Poster, sunum | ⏳ |

Ayrıntı: [docs/01-calisma-plani.md](docs/01-calisma-plani.md)

## Dokümanlar

- [00 — Proje özeti](docs/00-proje-ozeti.md) · [01 — Çalışma planı](docs/01-calisma-plani.md) · [02 — Literatür](docs/02-literatur.md)
- [03 — Hipotezler ve deneyler](docs/03-hipotez-ve-deneyler.md) · [04 — Teori](docs/04-teori.md) · [05 — Hata kontrolü](docs/05-hata-kontrol.md) · [06 — Açık sorular](docs/06-acik-sorular.md)
- [Sadeleştirilmiş rapor](docs/rapor-sade.md) · [Teknik taslak](docs/taslakfable.md) · [Repo eleştirisi](docs/analiz-fable.md) · [IoT mimarisi](docs/mimari-iot.md) · [Örnek raporlar](docs/ornekler/)
- [Aşama kayıtları](docs/kayit/) · [Kararlar (ADR)](docs/kararlar/) · [Kod okuma rehberleri](docs/kod-okuma/) · [Danışman klasörü](danisman/)
- Öğrenim / jüri PDF'leri: [`docs/`](docs/) içinde `*_OGRENIM_*` ve `*JURI*` dosyaları

## Kaynaktan çalıştırma

```bash
git clone https://github.com/zynordev/2204a-pqc-kronecker.git && cd 2204a-pqc-kronecker
python3 -m venv .venv && . .venv/bin/activate   # fish: . .venv/bin/activate.fish
pip install -e '.[dev]'
pytest                 # 1884 test
ruff check .           # kod stili
./pqcdrop-gui.sh       # GUI (PyQt6 gerekir; yoksa TUI'ye düşer)
./pqcdrop-tui.sh       # terminal arayüzü
python araclar/mutasyon_kontrolu.py              # testlerin hata yakalama gücü (~5 dk)
python experiments/01-dogruluk/calistir.py       # 10.000 örnek doğruluk deneyi
```

Taşınabilir paketi kendin derlemek için: `pip install pyinstaller && pyinstaller --onefile --paths src src/pqc/gui.py`.

## Klasörler

```
docs/          plan, teori, literatür, kayıtlar, kararlar, raporlar
src/pqc/       ML-KEM, çarpım yöntemleri, PQC-Drop (engine, discovery, gui, tui)
tests/         otomatik testler (NIST ACVP vektörleri dahil)
araclar/       yardımcı araçlar (mutasyon kontrolü)
experiments/   00 ön ölçüm · 01 doğruluk · 02 teori · 03 güvenlik · 04 performans
               05 ağ analizi · 06 IoT benchmark · 07 ESP32 donanım
danisman/      danışman öğretmen için rapor taslakları ve özetler
```

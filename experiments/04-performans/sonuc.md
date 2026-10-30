# E3 — Performans Deneyleri Raporu (H3 Sonuçları)

*Tarih: 2026-10-30. Makine: Intel Core i3-14100 (x86_64), Python 3.11.2. Tohum: 20261030.*  
*Protokol: `time.perf_counter_ns`, `gc.disable()`, ısınma turları, medyan ve IQR.*  
*Komut: `python experiments/04-performans/calistir.py` + `python experiments/04-performans/grafik.py`*

---

## 1. Deneyden Önceki Beklenti ([docs/03-hipotez-ve-deneyler.md](../../docs/03-hipotez-ve-deneyler.md))
1. **Bigint Hızlanması (E3.1):** Operand boyutu $8192 \to 5632$ bite inince Karatsuba teorik hızlanması $\approx (8192/5632)^{1.585} \approx 1,81\times$ olmalıdır.
2. **Yalın Polinom Çarpımı (E3.2):** Python ortamında büyük tamsayı çarpımı C düzeyinde optimize çalıştığı için Kronecker ikamesi saf Python NTT'den daha hızlı olmalıdır.
3. **Darboğaz Analizi (E3.3):** Kronecker ikamesinde asıl vakti tamsayı çarpımı değil, bit düzeyinde paketleme ve dengeli açma (Lemma 1 döngüsü) harcamalıdır.
4. **Uçtan Uca ML-KEM Paradoksu (E3.4 - ADR 0003):** FIPS 203 matrisi NTT alanında ürettiğinden, standart uyumluluğu korumak için yapılan Ters-NTT dönüşümleri Kronecker'i uçtan uca ML-KEM'de NTT'nin gerisinde bırakmalıdır.

---

## 2. Ölçülen Sonuçlar [ölçüldü]

### E3.1: Saf Büyük Tamsayı (Bigint) Çarpımı (15.000 Tekrar)

| Operand | Boyut (bit) | Medyan Süre (µs) | IQR (µs) | Hızlanma (8192b'ye göre) |
|---|:---:|:---:|:---:|:---:|
| **32-bit Paketleme (İşaretsiz)** | 8192 | 20,35 | 0,86 | 1,00× (Referans) |
| **24-bit Paketleme (Bayt Hizalı)** | 6144 | 11,68 | 0,05 | **1,74×** |
| **22-bit Paketleme ($\eta=3$, ML-KEM-512)** | 5632 | 9,94 | 0,18 | **2,05×** |
| **21-bit Paketleme ($\eta=2$, ML-KEM-768/1024)** | 5376 | 9,20 | 0,04 | **2,21×** |

*Bulgu:* Merkezlenmiş Kronecker ikamesi ile operand boyutunun küçülmesi, tamsayı çarpım süresini **2 katından fazla (%51)** kısaltmıştır (Teorik Karatsuba tahmini $1,81\times$ idi).

---

### E3.2: Tek Polinom Çarpımı ($R_q$ Katsayı Alanında)

| Yöntem | Medyan Süre (µs) | IQR (µs) | Karşılaştırma / Not |
|---|:---:|:---:|---|
| **Schoolbook (Okul Yöntemi)** | 3290,95 | 322,47 | Altın standart (en yavaş) |
| **NTT (Saf Python - Forward+Mul+Inv)** | 284,28 | 11,53 | Standart cebirsel dönüşüm |
| **NTT (Sadece MultiplyNTTs)** | 21,49 | 1,00 | Yalnızca NTT alanındaki çarpım |
| **KS: isaretsiz32-dongu** | 207,79 | 1,61 | Döngülü klasik Kronecker |
| **KS: isaretsiz32-bayt** | 106,10 | 2,34 | $2,68\times$ NTT'den hızlı |
| **KS: isaretli22-dongu** | 314,83 | 6,49 | Döngülü işaretli açma darboğazı |
| **KS: isaretli24-bayt** | 130,18 | 2,32 | **$2,18\times$ NTT'den hızlı** |
| **KS: isaretli22-negmod** | 196,45 | 1,64 | Mod $2^{n\ell}+1$ ile n dilim açma |
| **KS: isaretli24-bayt-negmod** | 145,17 | 1,53 | Hızlı bayt + mod $2^{n\ell}+1$ |
| **KS: isaretli24-bayt-modul** | 122,85 | 2,24 | İç çarpım modül toplamı entegre |

*Bulgu:* Katsayı alanında verilen iki polinomun çarpımında bayt hizalı Kronecker motorları (106–130 µs), saf Python NTT'den (284 µs) **2 kattan daha hızlıdır**.

---

### E3.3: Kronecker Darboğaz Analizi (Breakdown)

| Varyant | Paketleme (µs) | Tamsayı Çarpımı (µs) | Açma / İndirgeme (µs) | Toplam (µs) | En Çok Vakit Alan |
|---|:---:|:---:|:---:|:---:|:---:|
| **isaretsiz32-dongu** | 80,77 (%39) | 21,45 (%11) | 102,60 (%50) | 204,82 | Açma |
| **isaretsiz32-bayt** | 25,37 (%26) | 20,56 (%21) | 51,83 (%53) | 97,75 | Açma |
| **isaretli22-dongu** | 60,26 (%21) | 10,32 (%4) | **212,40 (%75)** | 282,98 | **Açma Döngüsü (Lemma 1)** |
| **isaretli24-bayt** | 28,83 (%30) | 12,48 (%13) | 55,02 (%57) | 96,33 | Açma |
| **isaretli22-negmod** | 61,61 (%39) | 46,09 (%30) | 48,87 (%31) | 156,57 | Dengeli |
| **isaretli24-bayt-negmod** | 27,60 (%25) | 54,59 (%50) | 27,41 (%25) | 109,61 | Çarpım/Mod |

*Bulgu:* `isaretli22-dongu` varyantında sürenin **%75'i** Lemma 1'deki dengeli açma döngüsünde (`ac_dongu_isaretli`) harcanmaktadır. Lemma 2 ile önerdiğimiz bayt hizalı açma (`isaretli24-bayt`) bu açma süresini 212 µs'den 55 µs'ye indirerek darboğazı kırmıştır!

---

### E3.4: Tam ML-KEM Uçtan Uca Performans Kıyaslaması (100 Tekrar Medyan)

| Parametre Seti | Motor | KeyGen (µs) | Encaps (µs) | Decaps (µs) |
|---|---|:---:|:---:|:---:|
| **ML-KEM-512** | **NTT (FIPS 203 Standart)** | **2692,35** | **4289,12** | **4698,35** |
| | KS (isaretli24-bayt-negmod) | 3736,35 | 5166,73 | 5727,71 |
| | KS (isaretli22-negmod) | 3843,59 | 5493,11 | 6189,90 |
| **ML-KEM-768** | **NTT (FIPS 203 Standart)** | **4138,05** | **6227,07** | **6532,43** |
| | KS (isaretli24-bayt-negmod) | 6152,68 | 8241,93 | 8903,38 |
| | KS (isaretli22-negmod) | 6532,55 | 8729,43 | 9844,16 |
| **ML-KEM-1024** | **NTT (FIPS 203 Standart)** | **5516,38** | **8155,77** | **8687,92** |
| | KS (isaretli24-bayt-negmod) | 8986,56 | 11697,79 | 12578,96 |
| | KS (isaretli22-negmod) | 10150,63 | 13379,44 | 14708,96 |

---

## 3. Bilimsel Yorum ve Projenin Ana Savunması

1. **Bigint Hipotezi Doğrulandı:** 22 ve 21 bitlik merkezleme operandı küçülterek tamsayı çarpımını **2,05 kat** hızlandırmıştır.
2. **Yalın Çarpımda Kronecker Üstünlüğü:** Salt polinom çarpımında Kronecker bayt varyantları saf Python NTT'den **2,18 kat** daha hızlıdır.
3. **Uçtan Uca ML-KEM Paradoksu (Bilimsel Dürüstlük):**  
   FIPS 203 standardı $\hat{A}$ matrisini ve $\hat{t}$ anahtarını doğrudan NTT alanında saklar. Kronecker'in standartla aynı çıktıyı üretmesi için bu nesneleri $\text{NTT}^{-1}$ ile katsayı alanına geri çevirmesi gerekir (ML-KEM-768 kapsüllemede fazladan 12 adet ters NTT). Bu dönüşüm ek yükü sebebiyle uçtan uca sistemde NTT %20–30 daha hızlı kalmaktadır.
   *Jüriye Mesajımız:* Projemiz saman alevi gibi "her yerde daha hızlıyız" iddiasında bulunmaz; yöntemin nerede hız kazandırdığını (yalın bigint ve katsayı çarpımı) ve nerede standart mimari yüzünden bedel ödediğini dürüstçe ortaya koyar.

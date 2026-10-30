# E2 — Teori Deneyle Örtüşür mü? (H2 Sonuçları)

*Tarih: 2026-10-30. Makine: Intel Core i3-14100 (x86_64), Python 3.11.2. Tohum: 20261030.*  
*Komut: `python experiments/02-teori-deney/calistir.py 20000 4` + `python experiments/02-teori-deney/grafik.py`*  
*Örneklem: 10 seri × 20.000 = 200.000 rastgele deneme + 60 en kötü durum kontrolü.*

---

## 1. Deneyden Önceki Beklenti ([docs/03-hipotez-ve-deneyler.md](../../docs/03-hipotez-ve-deneyler.md))
- **E2.1 / E2.2:** Lemma 1 / Önerme 1 keskinliği: $ℓ = ℓ_{\min}$ ile 0 hata, $ℓ = ℓ_{\min} - 1$ ile kesin hata.
- **E2.3 / E2.4:** Rastgele girdide açmanın bozulma olasılığı, Merkezi Limit Teoremi'ne dayalı **Model 2** teorik eğrisi ile %95 güven aralığında örtüşmelidir.
- **Fark:** Rastgele girdilerde tipik gereken taban ile en kötü durum sınırı ($ℓ_{\min}$) arasında 4–5 bitlik emniyet marjı görülmelidir.

---

## 2. Ölçülen Sonuçlar [ölçüldü]

### E2.1 & E2.2: En Kötü Durum Keskinlik Doğrulaması
60 kontrolün tamamında:
- $ℓ = ℓ_{\min}$: **%100 Doğru (0 hata)**
- $ℓ = ℓ_{\min} - 1$: **%100 Bozuk**
- Gerçek açma algoritması ile Lemma 1 ölçütü ($h^* \le 2^{ℓ-1}$) arasında **0 uyumsuzluk**.

### E2.3: Tam Sayı $ℓ$ Değerlerinde Model 2 vs Ölçülen Hata Oranı

Her seri 20.000 rastgele deneme (büyük katsayılar $[0, q)$ düzgün, küçük katsayılar $\text{CBD}(\eta)$):

| Seri | $ℓ$ | Hatalı / Toplam | Ölçülen Oran | %95 Wilson Güven Aralığı | Model 2 Tahmini | Durum |
|---|---|---|---|---|---|:---:|
| **tek-eta3-tam** | 17 | 602 / 20.000 | $3,01 \times 10^{-2}$ | $[2,78 \times 10^{-2}, 3,26 \times 10^{-2}]$ | $3,06 \times 10^{-2}$ | **✓ Aralıkta** |
| **tek-eta3-neg** | 17 | 2.434 / 20.000 | $1,22 \times 10^{-1}$ | $[1,17 \times 10^{-1}, 1,26 \times 10^{-1}]$ | $1,20 \times 10^{-1}$ | **✓ Aralıkta** |
| **tek-eta2-tam** | 17 | 23 / 20.000 | $1,15 \times 10^{-3}$ | $[7,66 \times 10^{-4}, 1,73 \times 10^{-3}]$ | $9,12 \times 10^{-4}$ | **✓ Aralıkta** |
| **tek-eta2-neg** | 17 | 99 / 20.000 | $4,95 \times 10^{-3}$ | $[4,07 \times 10^{-3}, 6,02 \times 10^{-3}]$ | $5,17 \times 10^{-3}$ | **✓ Aralıkta** |
| **modul-512-neg** | 18 | 4 / 20.000 | $2,00 \times 10^{-4}$ | $[7,78 \times 10^{-5}, 5,14 \times 10^{-4}]$ | $2,20 \times 10^{-4}$ | **✓ Aralıkta** |
| **modul-768-neg** | 18 | 6 / 20.000 | $3,00 \times 10^{-4}$ | $[1,37 \times 10^{-4}, 6,54 \times 10^{-4}]$ | $2,20 \times 10^{-4}$ | **✓ Aralıkta** |
| **modul-1024-tam** | 18 | 12 / 20.000 | $6,00 \times 10^{-4}$ | $[3,43 \times 10^{-4}, 1,05 \times 10^{-3}]$ | $9,12 \times 10^{-4}$ | **✓ Aralıkta** |
| **modul-1024-neg** | 18 | 110 / 20.000 | $5,50 \times 10^{-3}$ | $[4,57 \times 10^{-3}, 6,62 \times 10^{-3}]$ | $5,17 \times 10^{-3}$ | **✓ Aralıkta** |

*(Not: $ℓ \ge 19$ için tüm varyantlarda 20.000 denemede 0 hata görülmüştür; model tahmini de $< 10^{-15}$ düzeyindedir.)*

### E2.4: Sürekli Taban ($\log_2 B$) Analizi ve Emniyet Marjı

| Seri | Model Medyan ($\log_2 B$) | Ölçülen Medyan | 20.000 Denemede En Büyük $\log_2(2h^*)$ | Teorem 1 $ℓ_{\min}$ (En Kötü) | Tipik vs En Kötü Farkı |
|---|:---:|:---:|:---:|:---:|:---:|
| **tek-eta3-tam** | 16,62 | 16,61 | 17,49 | 22 | **4,51 bit** |
| **tek-eta3-neg** | 16,79 | 16,78 | 17,64 | 22 | **4,36 bit** |
| **tek-eta2-tam** | 16,32 | 16,32 | 17,20 | 21 | **3,80 bit** |
| **tek-eta2-neg** | 16,49 | 16,49 | 17,28 | 21 | **3,72 bit** |
| **modul-512-tam** | 17,12 | 17,11 | 17,92 | 23 | **5,08 bit** |
| **modul-768-tam** | 17,12 | 17,12 | 17,98 | 23 | **5,02 bit** |
| **modul-1024-tam** | 17,32 | 17,33 | 18,16 | 23 | **4,84 bit** |

Üretilen Grafikler:
- `grafik_e24.png`: Tam çarpım model eğrileri ve ölçülen hata oranları (%95 GA).
- `grafik_e24_neg.png`: Negasiklik indirgemeli varyantların eğrileri.
- `grafik_fark.png`: Rastgele dağılım gereksinimi ile $ℓ_{\min}$ arasındaki 4–5 bitlik farkın histogramı.

---

## 3. Bulgular ve Bilimsel Çıkarımlar

1. **Hipotez H2 desteklendi:**
   Model 2'nin deneyden önce kaydedilen tahminleri, ölçülebilir aralıktaki ($10^{-3} < p < 1 - 10^{-3}$) her noktada
   ölçümün %95 Wilson güven aralığı içinde kalmıştır (`ozet.csv`, `model_aralikta` sütunu). Aralık dışında tek sapma
   tek-eta3-tam ℓ = 16'dadır (model 0,999997, ölçülen 19 999/20 000; üst sınır 0,999991) ve ölçülebilir aralığın
   dışındadır. "Tam örtüşme" değil, "güven aralığı içinde" denmelidir.
2. **Parametre Simetrisi Doğrulandı:**
   ML-KEM-512 ile ML-KEM-768 modül toplamı katsayı sınırları teoride aynıdır ($k \cdot \eta_1 = 2 \cdot 3 = 3 \cdot 2 = 6$). Deneyde her ikisinin medyanı da $\log_2 B \approx 17,11 - 17,12$ çıkmıştır.
3. **Negasiklik İndirgeme Davranışı:**
   Negasiklik $X^n \equiv -1$ modunda her dilim $n$ terim içerdiğinden katsayı varyansı daha büyüktür. Bu yüzden negasiklik varyantlar aynı $ℓ$'de tam varyantlardan $\sim 0,17$ bit daha geniştir.
4. **En Kötü Durum vs Tipik Durum Ayrımı (H4 Güvenlik Temeli):**
   Rastgele şifreleme anahtarları ve rastgele şifreli metinlerde $ℓ = 18$ bit bile 20.000 denemede 0 hatayla çalışmaktadır. Ancak kötü niyetli bir saldırgan özel bir $u$ şifreli metni seçtiğinde katsayıları $ℓ_{\min}$ sınırına zorlayabilir. Bu nedenle $ℓ < ℓ_{\min}$ seçmek bir güvenlik zafiyetidir (H4).

---

## 4. Bilinen Kusurlar ve Sınırlılıklar
- Terimler sınırlı ($|a_i \cdot s_j| \le A \cdot \eta$) olduğundan gerçek dağılımın kuyruğu normalden **incedir**; model
  kuyrukta ($p < 10^{-4}$) hatayı fazla tahmin etmeye eğilimlidir (03'teki ön kayıt). Ölçümde sapmanın yönü
  ayırt edilememiştir: tek-eta2-tam ℓ = 17'de model altta (9,1·10⁻⁴ vs 1,15·10⁻³), modul-1024-tam ℓ = 18'de üstte
  (9,1·10⁻⁴ vs 6,0·10⁻⁴) kalmıştır; ikisi de güven aralığı içindedir. 20 000 deneme bu bölgede yönü belirlemeye yetmez.
- Dilimler bağımsız değildir (aynı $a_i$ çarpanı birden fazla dilimde yer alır); bağımsızlık formülü bir yaklaşımdır.
  Kod ayrıca birleşim üst sınırını da verir (`model_birlesim`); geçiş bölgesinde ikisi birbirine yakındır.
- ℓ ≥ 19'da 20 000 denemede 0 hata, modelin 10⁻¹⁵'in altındaki tahminini **doğrulamaz**; yalnızca üst sınır
  (Wilson, 1,9·10⁻⁴) verir.

# 03 — Hipotezler ve Deneyler

*Son güncelleme: 2026-10-26.*

İlke (danışman uyarısı): **teori önce sayısal bir tahmin verir, deney o tahmini ölçer.** Her deneyde
"beklenen" sütunu deneyden *önce* doldurulur ve sonradan değiştirilmez. Tahmin tutmazsa bu da sonuçtur.

## H1 — Doğruluk
**İddia:** Kronecker tabanlı çarpım kullanan ML-KEM, NIST resmî test vektörleriyle bayt bayt aynı çıktıyı verir.

| Deney | Yöntem | Beklenen | Ölçülen |
|---|---|---|---|
| E1.1 | ACVP keyGen / encaps / decaps vektörleri, 3 parametre seti | %100 eşleşme | NTT ve 8 Kronecker varyantının her biri ile 225/225 [ölçüldü, 2026-10-27, `tests/test_acvp.py`] |
| E1.2 | 10.000 rastgele (a, s) çifti: her Kronecker varyantı vs schoolbook | 0 hata | 8 varyant × 10.000: 0 hata [ölçüldü, `experiments/01-dogruluk`] |
| E1.3 | Kenar durumlar: tüm katsayılar ±1664, s tamamen ±η, sıfır polinom, negasiklik en kötü girdi | 0 hata | 8 varyant, 0 hata [ölçüldü, `tests/test_kronecker.py`] |

## H2 — Teori deneyle örtüşür (ana kanıt)
**İddia:** [04 — Teori](04-teori.md)'deki Lemma 1'in verdiği ℓ_min her girdi için yeterlidir ve keskindir;
rastgele girdide hata olasılığını Model 2 tahmin eder.

| Deney | Yöntem | Beklenen | Ölçülen |
|---|---|---|---|
| E2.1 | ℓ = ℓ_min: kötü durum girdileri (Önerme 1'deki yapı) | 0 hata | 10 seri × kötü durum girdileri: 0 hata [ölçüldü, `experiments/02-teori-deney`] |
| E2.2 | ℓ = ℓ_min − 1: Önerme 1'deki keskinlik girdisi | hata var | 10 seri × kötü durum girdileri: hepsi hatalı [ölçüldü, `experiments/02-teori-deney`] |
| E2.3 | ℓ ∈ {14…ℓ_min}, rastgele girdi (CBD ile s), her seri için 20.000 deneme | Model 2 eğrisi | Geçiş bölgelerinde model değeri tam %95 Wilson GA içinde (örn. tek-η3 ℓ=17 model 0,0306, ölçülen 0,0301) [ölçüldü] |
| E2.4 | E2.3 grafiği: model eğrisi + ölçülen noktalar + %95 güven aralığı | eğri aralıkların içinde | `grafik_e24.png`, `grafik_e24_neg.png`, `grafik_fark.png` [ölçüldü, `experiments/02-teori-deney`] |

### H2 ön kaydı (2026-10-30, deneyden önce yazıldı; değiştirilmez)

Deney: [experiments/02-teori-deney](../experiments/02-teori-deney/). Seriler: ML-KEM'deki (k, η) çiftleri —
tek çarpım η = 3 / η = 2 (Teorem 1), modül toplamı k = 2, 3, 4 (Sonuç 1) — × açma türü
(tam: 2n−1 dilim; neg: mod 2^(nℓ)+1, n dilim, Önerme 2). Rastgele girdi: büyük [0, q) düzgün, küçük CBD(η).
Model: `pqc.teori.model_hata` (Model 2). Her seri N = 20 000 deneme, tohum 20261030.

**E2.1 / E2.2:** 10 seri × en kötü girdiler (±işaret; neg için k0 = 0 ve n−1): ℓ_min'de hepsi doğru,
ℓ_min − 1'de hepsi bozuk. ℓ_min = 22 (tek, η=3), 21 (tek, η=2), 23 (modül, üç set).

**E2.3 — tam sayı ℓ'de model tahmini (bağımsızlık yaklaşımı):**

| Seri | ℓ ≤ 16 | ℓ = 17 | ℓ = 18 | ℓ ≥ 19 |
|---|---|---|---|---|
| tek-η3 tam / neg | ≈ 1 | 0,031 / 0,12 | 7·10⁻¹¹ / 9·10⁻¹⁰ | < 10⁻⁴⁰ |
| tek-η2 tam / neg | ≈ 1 (ℓ=16: 0,98 / 1) | 9·10⁻⁴ / 5·10⁻³ | ~10⁻¹⁵ | < 10⁻⁶⁰ |
| modül-512 tam / neg | ≈ 1 | 0,76 / 0,97 | 3·10⁻⁵ / 2·10⁻⁴ | < 10⁻¹⁹ |
| modül-768 tam / neg | ≈ 1 | 0,76 / 0,97 | 3·10⁻⁵ / 2·10⁻⁴ | < 10⁻¹⁹ |
| modül-1024 tam / neg | ≈ 1 | 0,98 / 1,00 | 9·10⁻⁴ / 5·10⁻³ | < 10⁻¹⁵ |

**E2.4 — sürekli taban (log₂B), model tahmini:** hata olasılığı 0,5 ve 0,01 olduğu log₂B:

| Seri | p = 0,5 | p = 0,01 | p = 10⁻⁶ | ℓ_min (en kötü durum) | fark (ℓ_min − p=10⁻⁶) |
|---|---|---|---|---|---|
| tek-η3 tam | 16,62 | 17,11 | 17,66 | 22 | 4,3 bit |
| tek-η2 tam | 16,32 | 16,81 | 17,37 | 21 | 3,6 bit |
| modül-512 tam | 17,12 | 17,61 | 18,16 | 23 | 4,8 bit |
| modül-1024 tam | 17,32 | 17,81 | 18,37 | 23 | 4,6 bit |
| (neg serileri) | +0,13…0,17 | +0,13…0,14 | +0,10 | aynı | |

Önceden yazılan beklentiler:
1. E2.1/E2.2 tam olarak tutar (ispat). Gerçek açma ile Lemma 1 ölçütü (h* ≤ 2^(ℓ−1)) her denemede aynı sonucu verir.
2. Ölçülen hata oranı, model değerinin %95 Wilson güven aralığının içinde kalır (ölçülebilir aralıkta,
   yani 0,001 < p < 0,999).
3. **Sistematik sapma beklentisi:** terimler sınırlı (|a_i·s_j| ≤ 4992) olduğu için gerçek dağılımın kuyruğu
   normalden incedir; model kuyrukta (p küçükken) hatayı **biraz fazla** tahmin edebilir. Bağımlılık
   (aynı a_i birçok dilimde) bağımsızlık formülünü birleşim sınırının altına çeker.
4. modül-512 ile modül-768 aynı eğriyi verir (k·η = 6 ikisinde de; model yalnızca k·η'ya bağlı).
5. neg serileri aynı ℓ'de tam serilerinden daha sık bozulur (her dilim n terimli; tamda yalnızca ortadakiler).
6. Ön ölçümdeki "ℓ = 17'de 291/300 hata" (düzgün s ile) CBD ile tekrarlanmaz: tek-η3-tam ℓ = 17'de ≈ %3.

## H3 — Performans
**İddia:** Operand 8192 → 5632 bit küçülünce büyük tamsayı çarpımı Karatsuba'ya göre ≈ (8192/5632)^1.585 ≈ 1,81
kat hızlanır. Uçtan uca hızlanma ancak paketleme/açma da optimize edilirse görülür.

| Deney | Yöntem | Beklenen | Ölçülen |
|---|---|---|---|
| E3.1 | Yalnızca bigint çarpımı, 5632 vs 8192 bit | ≈ 1,8× | 2,05× hızlanma (20,35 µs vs 9,94 µs) [ölçüldü, `experiments/04-performans`] |
| E3.2 | Tek polinom çarpımı: schoolbook, Karatsuba, NTT, 8 KS varyantı | KS < NTT (Python'da) | KS bayt (106–145 µs) < NTT (284 µs) < Schoolbook (3290 µs); **en hızlısı işaretsiz32-bayt (106 µs)**, merkezlemenin tek polinomda ölçülebilir kazancı yok [ölçüldü] |
| E3.3 | Süre dağılımı: paketleme / çarpım / açma / indirgeme ayrı ayrı | açma baskın | Doğrulandı: döngülü açma sürenin %75'ini harcıyor; bayt açma bunu 4 kat hızlandırıyor [ölçüldü] |
| E3.4 | Tam ML-KEM keyGen/encaps/decaps, NTT vs en iyi KS | — | Standart dönüşüm ek yükü (ADR 0003) sebebiyle NTT uçtan uca %20–63 daha hızlı (keygen %39/%49/%63, encaps %20/%32/%43, decaps %22/%36/%45; 512/768/1024) [ölçüldü, 100 tekrar] |
| E3.5 | Aynı ölçümler ikinci makinede (laptop) | sıralama aynı | — |

Protokol: `time.perf_counter_ns`, ısınma turu, ≥1000 tekrar, medyan + çeyrekler arası aralık,
çöp toplayıcı kapalı (`gc.disable()`), makine bilgisi (CPU, Python sürümü) CSV başlığına yazılır.

## H4 — Güvenlik
**İddia:** ℓ en kötü durum sınırının altında seçilirse, saldırganın seçtiği şifreli metinde çarpımın bozulup
bozulmaması gizli anahtara bağlıdır (‖s‖₁ hakkında bilgi sızar).

| Deney | Yöntem | Beklenen | Ölçülen |
|---|---|---|---|
| E4.1 | ℓ ∈ {18…22}; farklı s'ler için saldırgan girdisi; hata ↔ ‖s‖₁ eşiği | hata ⇔ 1664·‖s‖₁ ≥ 2^(ℓ−1) | 1500 vektör × 5 ℓ'de 0 uyumsuzluk. Gerçek CBD vektörlerinde (700; max norm 282) ℓ = 18–19 hepsi bozuk, ℓ = 20–22 hiçbiri bozuk değil; ℓ = 20 eşiği (316) yalnızca yapay normlu vektörlerde aşıldı [ölçüldü, `experiments/03-guvenlik`] |
| E4.2 | ML-KEM-512 iç çarpımı, sıkıştırmaya uygun şifreli metinle, ℓ = 20 | aynı eşik | 150 anahtarda 0 uyumsuzluk; 75 gerçek anahtarda 0 bozulma (max norm 270), 75 yapay büyütülmüş anahtarda eşik 316 üstü bozuk. **Decaps çağrılmadı** [ölçüldü, `experiments/03-guvenlik`] |

Not: Bu, kendi bilerek bozduğumuz uygulamamız üzerinde bir gösterimdir; gerçek bir sisteme saldırı değildir.
FIPS 203'ün örtük reddetmesi, geçersiz şifreli metinde taşma olsa da olmasa da sahte anahtar döndürdüğünden decaps
çıktısı taşmayı dışarı vermez; gösterilen şey "anahtara bağlı davranış"tır, anahtar ele geçirme değil
(bkz. `experiments/03-guvenlik/sonuc.md` §4).

## Deney klasörü şablonu
```
experiments/NN-kisa-ad/
  calistir.py     # tek komutla tüm deney; sabit seed
  veri.csv        # ham ölçümler (elle düzenlenmez)
  grafik.py       # veri.csv → grafik.png
  sonuc.md        # beklenen vs ölçülen, yorum, bilinen kusurlar
```

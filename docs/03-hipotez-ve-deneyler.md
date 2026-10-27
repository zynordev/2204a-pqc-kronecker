# 03 — Hipotezler ve Deneyler

*Son güncelleme: 2026-10-26.*

İlke (danışman uyarısı): **teori önce sayısal bir tahmin verir, deney o tahmini ölçer.** Her deneyde
"beklenen" sütunu deneyden *önce* doldurulur ve sonradan değiştirilmez. Tahmin tutmazsa bu da sonuçtur.

## H1 — Doğruluk
**İddia:** Kronecker tabanlı çarpım kullanan ML-KEM, NIST resmî test vektörleriyle bayt bayt aynı çıktıyı verir.

| Deney | Yöntem | Beklenen | Ölçülen |
|---|---|---|---|
| E1.1 | ACVP keyGen / encaps / decaps vektörleri, 3 parametre seti | %100 eşleşme | NTT ile 225/225 [ölçüldü, 2026-10-27]; Kronecker ile Aşama 3 |
| E1.2 | 10.000 rastgele (a, s) çifti: her Kronecker varyantı vs schoolbook | 0 hata | — |
| E1.3 | Kenar durumlar: tüm katsayılar ±1664, s tamamen ±η, sıfır polinom | 0 hata | — |

## H2 — Teori deneyle örtüşür (ana kanıt)
**İddia:** [04 — Teori](04-teori.md)'deki Lemma 1'in verdiği ℓ_min her girdi için yeterlidir ve keskindir;
rastgele girdide hata olasılığını Model 2 tahmin eder.

| Deney | Yöntem | Beklenen | Ölçülen |
|---|---|---|---|
| E2.1 | ℓ = ℓ_min: kötü durum girdileri (Önerme 1'deki yapı) | 0 hata | — |
| E2.2 | ℓ = ℓ_min − 1: Önerme 1'deki keskinlik girdisi | hata var | — |
| E2.3 | ℓ ∈ {16…22}, rastgele girdi (CBD ile s), her ℓ için N deneme | Model 2 eğrisi | — |
| E2.4 | E2.3 grafiği: model eğrisi + ölçülen noktalar + %95 güven aralığı | eğri aralıkların içinde | — |

## H3 — Performans
**İddia:** Operand 8192 → 5632 bit küçülünce büyük tamsayı çarpımı Karatsuba'ya göre ≈ (8192/5632)^1.585 ≈ 1,81
kat hızlanır. Uçtan uca hızlanma ancak paketleme/açma da optimize edilirse görülür.

| Deney | Yöntem | Beklenen | Ölçülen |
|---|---|---|---|
| E3.1 | Yalnızca bigint çarpımı, 5632 vs 8192 bit | ≈ 1,8× | ön ölçüm: 1,93× |
| E3.2 | Tek polinom çarpımı: schoolbook, Karatsuba, NTT, 5 KS varyantı | KS < NTT (Python'da) | — |
| E3.3 | Süre dağılımı: paketleme / çarpım / açma / indirgeme ayrı ayrı | açma baskın | — |
| E3.4 | Tam ML-KEM keyGen/encaps/decaps, NTT vs en iyi KS | — | — |
| E3.5 | Aynı ölçümler ikinci makinede (laptop) | sıralama aynı | — |

Protokol: `time.perf_counter_ns`, ısınma turu, ≥1000 tekrar, medyan + çeyrekler arası aralık,
çöp toplayıcı kapalı (`gc.disable()`), makine bilgisi (CPU, Python sürümü) CSV başlığına yazılır.

## H4 — Güvenlik
**İddia:** ℓ en kötü durum sınırının altında seçilirse, saldırganın seçtiği şifreli metinde çarpımın bozulup
bozulmaması gizli anahtara bağlıdır (‖s‖₁ hakkında bilgi sızar).

| Deney | Yöntem | Beklenen | Ölçülen |
|---|---|---|---|
| E4.1 | ℓ = ℓ_min − 1; farklı s'ler için saldırgan girdisi; hata ↔ ‖s‖₁ eşiği | hata ⇔ 1664·‖s‖₁ ≥ 2^(ℓ−1) | — |
| E4.2 | Aynı şey tam decaps üzerinde: paylaşılan sır doğru/yanlış | aynı eşik | — |

Not: Bu, kendi bilerek bozduğumuz uygulamamız üzerinde bir gösterimdir; gerçek bir sisteme saldırı değildir.

## Deney klasörü şablonu
```
experiments/NN-kisa-ad/
  calistir.py     # tek komutla tüm deney; sabit seed
  veri.csv        # ham ölçümler (elle düzenlenmez)
  grafik.py       # veri.csv → grafik.png
  sonuc.md        # beklenen vs ölçülen, yorum, bilinen kusurlar
```

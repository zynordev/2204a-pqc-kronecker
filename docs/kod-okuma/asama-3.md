# Kod Okuma Rehberi — Aşama 3 (Kronecker motorları)

*Kim için: Öğrenci A (Halil), sonra B. Önce [Aşama 2 rehberi](asama-2.md) bitmiş olmalı.
Yanında [04 — Teori](../04-teori.md) açık olsun: kodun her parçası oradaki bir lemmaya karşılık geliyor.*

Cevapları [Aşama 3 kaydı](../kayit/2026-10-27-asama-3.md) sonundaki "Kod okuma notu" bölümüne yaz.

## Okuma sırası

| # | Dosya | Teori | Ne |
|---|---|---|---|
| 1 | `src/pqc/teori.py` | Teorem 1, Sonuç 1 | gereken ℓ'yi hesaplayan 3 fonksiyon |
| 2 | `src/pqc/kronecker.py` — `paketle_dongu`, `ac_dongu_isaretli` | Lemma 1 | X = 2^ℓ koyma ve geri okuma |
| 3 | `src/pqc/kronecker.py` — `paketle_bayt`, `ac_bayt`, `_birler` | Lemma 2 | bayt ile hızlı paketleme/açma |
| 4 | `src/pqc/kronecker.py` — `Varyant` | Önerme 2, Sonuç 1 | 5 seçim, `_coz`, `ic_carpim`, `VARYANTLAR` |
| 5 | `src/pqc/kpke_kronecker.py` | ADR 0003 | K-PKE'nin Kronecker'li hali; `kpke.py` ile yan yana oku |
| 6 | `src/pqc/mlkem.py` — `pke` parametresi | — | motorun nasıl seçildiği |
| 7 | `tests/test_kronecker.py` | Önerme 1–2 | en kötü durum girdileri, sınırın keskinliği |
| 8 | `tests/test_acvp.py` — `MOTORLAR` | H1 | aynı NIST vektörleri 9 motorla |
| 9 | `experiments/01-dogruluk/` | E1.2 | 10.000 örnekli deney ve sonucu |

## Kendini kontrol soruları

**Paketleme ve açma**
1. `paketle_dongu([1, -1, 2], 8)` kaç eder? Elle hesapla, sonra Python'da dene.
2. `ac_dongu_isaretli` neden `C = (C - d) >> l` yapıyor, sadece `C >> l` yetmez mi? (İpucu: d negatifse.)
3. `ac_bayt`'ta her dilime 2^(ℓ−1) eklemek neden "borç" sorununu ortadan kaldırıyor? Lemma 2'yi kendi
   cümlelerinle yaz.
4. `paketle_bayt` neden `sapma·_birler(...)` çıkarıyor? Paketlemenin doğrusal olması ne demek?

**Varyantlar**
5. Neden `bayt=True` için ℓ 8'in katı olmak zorunda? 22 bit neden bayta uymuyor, 24 neden uyuyor?
6. `negasiklik_mod` neden işaretsiz katsayılarla kullanılamıyor? (`__post_init__`'teki yorum)
7. `_coz`'daki `c.append(0)` satırı neden var? (2n−1 dilim, i + N indeksi)
8. Modül toplamı neden ℓ'yi 22'den 23'e çıkarıyor ama 24'te üç parametre setinin hepsine yetiyor?
   04-teori.md'deki Sonuç 1 tablosunu kendin hesapla.

**ML-KEM ile bağlantı**
9. `kpke_kronecker.py`'de kaç tane `ntt_ters` çağrısı var, ML-KEM-768 için toplam kaç dönüşüm eder?
   Bu neden Kronecker için bir **bedel** (ADR 0003)?
10. `KroneckerPKE._kontrol` neden var, `Varyant.ic_carpim` neden aynı kontrolü yapmıyor?
11. decrypt'te `u` nereden geliyor ve neden "büyük" çarpan sayılıyor?

**Hata kontrolü**
12. `test_sinir_keskin` neyi kanıtlıyor? Neden 22'de doğru, 21'de yanlış olması önemli?
13. 225 NIST vakası × 8 varyant geçti ve 10.000 rastgele örnekte 0 hata çıktı. Buna rağmen neden
    ayrıca en kötü durum testleri yazdık? (İpucu: rastgele girdide katsayılar ~18 bit kalıyor — ön ölçüm.)

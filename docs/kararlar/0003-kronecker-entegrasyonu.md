# ADR 0003 — Kronecker'in ML-KEM'e takılması

*Tarih: 2026-10-27. Durum: kabul edildi.*

## Bağlam
FIPS 203, Â matrisini doğrudan NTT alanında üretir (SampleNTT) ve t̂'yi (açık anahtar) ile ŝ'yi (gizli anahtar)
NTT alanında saklar. Kronecker ikamesi ise katsayı alanında çalışır. Çıktımız standartla **bayt bayt aynı**
kalmalı (H1: NIST vektörleri değişmeden geçmeli).

## Karar
1. `kpke_kronecker.KroneckerPKE`, `kpke.py` ile aynı akışı izler; NTT alanındaki nesneler kullanılmadan önce
   NTT⁻¹ ile katsayı alanına çevrilir (Â → A: k², t̂ → t: k, ŝ → s: k dönüşüm), çarpım sonucu gerekiyorsa
   NTT ile geri çevrilir (keygen'de t ve s). Matematiksel olarak aynı sonuç: NTT bir halka izomorfizmidir.
2. Çarpım yöntemi `Varyant` nesnesiyle seçilir (`kronecker.py`); `mlkem.*` fonksiyonları `pke` parametresi alır.
3. `KroneckerPKE`, varyantın ℓ'si Teorem 1 / Sonuç 1'e göre yetersizse çalışmayı **reddeder**. `Varyant.ic_carpim`
   bu kontrolü yapmaz, çünkü H2/H4 deneyleri bilerek dar ℓ kullanır.
4. `ic_carpim`, küçük çarpanın katsayılarının [−η, η] dışında olmasını hata sayar (Teorem 1'in varsayımı).

## Sonuçlar
- (+) Tüm varyantlar NIST vektörleriyle doğrulanabiliyor; standart dışı hiçbir kısayol yok.
- (−) Dönüşümler ek maliyet: Kronecker yolu, NTT dönüşümlerinden kurtulmak yerine onlara **ek olarak**
  çarpım yapıyor. Aşama 4 (H3) bu maliyeti ayrıca ölçecek; "Kronecker ML-KEM'i hızlandırır" iddiası ancak
  bu bedel dahil ölçülerek yapılabilir.
- Değerlendirilip reddedilen: Â'yı katsayı alanında üretmek (standart dışı, NIST vektörleri geçmez).

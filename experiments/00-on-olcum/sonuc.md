# 00 — Ön Ölçüm (fikir değerlendirmesi)

*Tarih: 2026-10-26. Makine: Raspberry Pi 5, Python 3.13.5. Seed: 1. Betik: `ks_bench.py` (arşiv, değiştirilmez).*

Amaç: fikrin uygulanabilir olup olmadığını hızlıca görmek. **Raporda kullanılmaz**; Aşama 4 deneyleri
bunun yerine geçer.

## Sonuçlar [ölçüldü]

Tek polinom çarpımı (n = 256, q = 3329, s ∈ [−3, 3]), medyan:

| Yöntem | Süre |
|---|---|
| Schoolbook | 9773 µs |
| NTT (saf Python) | 903 µs |
| Kronecker, işaretsiz 32 bit | 607 µs |
| Kronecker, işaretli 22 bit (basit açma) | 790 µs |
| Kronecker, mod 2^(256·22)+1 negasiklik | 420 µs |
| Yalnızca bigint çarpımı: 8192 bit / 5632 bit | 47,8 µs / 24,7 µs (1,93×) |

Taşma:
- Rastgele girdi, 2000 denemede en büyük |c_k| = 154 034 (~18 bit); teorik en kötü durum 1 277 952.
- Rastgele girdide 300 denemede hatalı çarpım sayısı: ℓ = 21, 20, 19, 18 → 0; ℓ = 17 → 291.
- Saldırgan tipi girdi (a_i = 1664·sgn(s_{n−1−i})): ℓ = 21 doğru, ℓ ≤ 20 bozuk.

## Çıkarımlar
1. Operand küçültme bigint çarpımını ~2 kat hızlandırıyor (Karatsuba öngörüsü ~1,81×).
2. Uçtan uca süreyi paketleme/açma döngüsü belirliyor; basit işaretli açma işaretsizden yavaş.
3. Python'da Kronecker, saf Python NTT'den hızlı (bigint çarpımı C'de çalıştığı için).
4. En kötü durum ile tipik durum arasında ~3 bit fark var → H2 ve H4'ün çıkış noktası.

## Bilinen kusurlar
- **s düzgün dağılımlı [−3, 3] seçildi; ML-KEM'de s ~ CBD(η).** Düzgün dağılımda E‖s‖₁ ≈ 439,
  CBD(3)'te 240. Bu yüzden "saldırgan girdisi ℓ = 20'de bozar" sonucu dağılıma bağlıdır: hata koşulu
  1664·‖s‖₁ ≥ 2^19, yani ‖s‖₁ ≥ 316. CBD ile çoğu s için ℓ = 20'de hata **çıkmayabilir**
  (bkz. [04 — Önerme 1](../../docs/04-teori.md)). Aşama 4'te CBD ile tekrarlanacak.
- Tek makine, tek çalıştırma; CPU frekansı sabitlenmedi, `gc` açık.
- Rastgele taşma testinde yalnızca 300 deneme; düşük olasılıklı hatalar görünmez.
- NTT basit saf Python; Montgomery/Barrett gibi optimizasyonlar yok.
- Karatsuba ve modül toplamı (k > 1) ölçülmedi.

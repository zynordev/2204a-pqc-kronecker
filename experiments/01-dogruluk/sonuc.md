# E1.2 — 10.000 Rastgele Örnekle Doğruluk

*Tarih: 2026-10-27. Makine: Raspberry Pi 5 (aarch64), Python 3.13.5. Tohum: 20261027. Süre: 405 sn.
Komut: `python experiments/01-dogruluk/calistir.py` (1 GB bellek sınırı ve `nice` ile çalıştırıldı).*

## Beklenen (deneyden önce, [03](../../docs/03-hipotez-ve-deneyler.md))
Teorem 1 / Sonuç 1'e göre güvenli ℓ seçilmiş her varyant için **0 hata**.

## Ölçülen [ölçüldü]
Her örnek: ML-KEM'de gerçekten oluşan (k, η) ∈ {(1,3), (2,3), (3,2), (4,2)} çiftlerinden biri (2.500'er);
büyük polinomlar [0, q)'da düzgün, küçükler CBD(η). Referans: okul yöntemiyle Σ büyük_j·küçük_j.

| Varyant | Hatalı / toplam |
|---|---|
| isaretsiz32-dongu | 0 / 10 000 |
| isaretsiz32-bayt | 0 / 10 000 |
| isaretli22-dongu | 0 / 10 000 |
| isaretli24-bayt | 0 / 10 000 |
| isaretli22-negmod | 0 / 10 000 |
| isaretli24-bayt-negmod | 0 / 10 000 |
| isaretli24-bayt-modul | 0 / 10 000 |
| isaretli24-bayt-negmod-modul | 0 / 10 000 |

Ham veri: `veri.csv` (her satır bir örnek; 1 = doğru).

## Yorum
Beklenti tuttu. %95 güvenle, her varyantın rastgele girdide hata oranı < 3/10 000 (sıfır hatada
"üçler kuralı"). Ancak:

## Bilinen kusurlar
- **Bu deney tek başına doğruluğu kanıtlamaz.** Rastgele girdide katsayılar yaklaşık 18 bitte kalıyor
  (ön ölçüm), yani 22–24 bitlik sınırın yakınına hiç gelinmiyor. ℓ'yi 19'a düşürsek bile büyük ihtimalle
  0 hata çıkardı. Sınırın yeterliliğini gösteren şey **ispat (Teorem 1) + en kötü durum testleridir**
  (`tests/test_kronecker.py`); bu deney "ortalama durumda da sorun yok" der. Sınır ile tipik durum
  arasındaki fark H2'nin (Aşama 4) konusu.
- CBD burada `random.getrandbits` ile çekildi (dağılım FIPS 203 Alg. 8 ile aynı, ama SHAKE ile değil).
  ML-KEM'in kendi örneklemesi ayrıca NIST vektörleriyle test edildi (E1.1).
- Tek makine, tek çalıştırma (doğruluk deneyi için yeterli; süre burada ölçülen bir değer değil).

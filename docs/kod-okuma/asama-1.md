# Kod Okuma Rehberi — Aşama 1 (çıkış gözlemi + teori)

*Kim için: A ve B. Kısa: 1 dosya + 1 test + 04-teori.md §0, Lemma 1, Teorem 1, Önerme 1.*

| # | Dosya | Ne |
|---|---|---|
| 1 | [04-teori.md §0](../04-teori.md) | 23²'den Kronecker'e köprü, karşılaştırma tablosu |
| 2 | `src/pqc/taban.py` | gözlemin kodu: rakamlar, polinom değeri, elde ile normalize, eldesiz taban sınırı |
| 3 | `tests/test_taban.py` | 23², 34² adım adım; 10–99 hepsi; taban 100/163; 19² ödünç; Kronecker bağlantısı |
| 4 | 04-teori.md Lemma 1, Teorem 1, Önerme 1 | kesin ifade + ispat; her birinin altındaki kutuyu B işaretleyecek |

## Sorular
1. 47²'yi kendi yönteminle elle hesapla; sonra `elde_ile_normalize(kare_katsayilari(47))` ile karşılaştır.
   Her adımdaki elde nedir?
2. Neden 3 basamaklı sayıların karesinde eldesiz taban sınırı 3·81 = 243? Hangi sayıda tam 243'e ulaşılır,
   hangi katsayıda?
3. `elde_ile_normalize`'de `divmod` negatif sayıda ne yapıyor? `divmod(-4, 10)` = ? Bu neden "ödünç"?
4. Tablo: bizim yöntemde elde **gerekli**, Kronecker'de **olmamalı**. Kronecker'de elde olsaydı ne bozulurdu?
5. Lemma 1 ispatı (a)'da "en küçük farklı indeks j" fikri nerede kullanılıyor? |d_j − d'_j| < B neden önemli?
6. Teorem 1 (i): n = 4 için T_0 … T_6'yı tek tek say ve min(k+1, 2n−1−k) ile karşılaştır.
7. Önerme 1 (a) neden "ℓ = 21 bazen bozulur" değil "**kesinlikle** bozulur" diyor? (İpucu: algoritma hangi
   kümeden rakam üretir?)
8. 99² ↔ (a ≡ 1664, s ≡ 3) eşleşmesini kendi cümlelerinle açıkla: hangisi n, hangisi A, hangisi η?

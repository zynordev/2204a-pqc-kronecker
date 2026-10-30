# E4 — Sınırın Altında Anahtara Bağlı Davranış (H4 Sonuçları)

*Tarih: 2026-10-30. Makine: Intel Core i3-14100 (x86_64), Python 3.11.2. Tohum: 20261030.*
*Komut: `python experiments/03-guvenlik/calistir.py` + `python experiments/03-guvenlik/grafik.py`*
*Düzeltme: 2026-10-30 — bulgular ham veriye (`veri_e41.csv`, `veri_e42.csv`) göre yeniden yazıldı; "CCA ile anahtar
ele geçirme" ve "decapsulation hatası" ifadeleri çıkarıldı (gerekçe §4). Ayrıntı: `docs/analiz-fable.md` §2.*

---

## 1. Hipotez (H4, docs/03)
ℓ, en kötü durum sınırı ℓ_min'in altında seçilirse, saldırganın seçtiği girdi karşısında çarpımın bozulup bozulmaması
gizli anahtara (‖s‖₁) bağlıdır. **Beklenen (deneyden önce):** hata ⇔ 1664·‖s‖₁ ≥ 2^(ℓ−1).

## 2. Eşik modeli (docs/04, Önerme 1)
a_i = A·sgn(s_{n−1−i}), A = 1664 seçilirse c_{n−1} = A·‖s‖₁ (Hölder eşitliği). Lemma 1'e göre taşma koşulu
1664·‖s‖₁ ≥ 2^(ℓ−1) ⇔ ‖s‖₁ ≥ ⌈2^(ℓ−1)/1664⌉:

| ℓ | 18 | 19 | 20 | 21 | 22 |
|---|---|---|---|---|---|
| Eşik ‖s‖₁ | 79 | 158 | 316 | 631 | 1261 (> n·η = 768: imkânsız) |

CBD(3) için E‖s‖₁ = 256 · 60/64 = 240; standart sapma ≈ √(256·Var|s|) ≈ 14. Yani 316 eşiği ortalamanın ≈ 5σ
üstündedir; 158 ve 79 ise ortalamanın çok altındadır.

## 3. Ölçülen sonuçlar [ölçüldü]

### E4.1 — Çarpım düzeyinde (1500 vektör × ℓ ∈ {18, …, 22})
Örneklem: 400 CBD(3) + 300 CBD(2) **gerçek dağılımdan**; 800 vektör eşik çevresini taramak için normu 156–673
aralığına **yapay olarak** ayarlanmış ({−3..3} katsayılı).
- Teorik eşik ile ölçülen bozulma arasında uyumsuzluk: **0 / 7500** (1500 × 5 ℓ).
- Gerçek dağılımdaki 700 vektörün en büyük normu **282**. Bu vektörlerde ℓ = 18 ve 19: **hepsi bozuk**; ℓ = 20, 21, 22:
  **hiçbiri bozuk değil** (316 eşiği aşılmadı).
- Eşik davranışı (norm < eşik → doğru, ≥ eşik → bozuk) yapay normlu vektörlerde ℓ = 18–21 için gözlendi (`grafik_e41.png`).

### E4.2 — ML-KEM-512 iç çarpımı (150 anahtar, ℓ = 20)
Şifreli metin, FIPS 203'ün 10 bitlik sıkıştırmasına uygun uç değerlerle kuruldu: y = 511 → +1661, y = 512 → −1664
(±1664'ün ikisi de 512'ye sıkıştığı için +1661 kullanıldı; eşik buna göre ⌈2¹⁹/1664⌉ = 316 kalır çünkü belirleyici
olan negatif taraftaki 1664'tür ve pozitif tarafta 1661 ile sınır en fazla 1 birim kayar — ham veride uyumsuzluk 0).
- 75 anahtar gerçek `keygen` çıktısı: en büyük ‖s₀‖₁ = 270, bozulan **0**.
- 75 anahtarın s₀'ı 280–360 normuna yapay olarak büyütüldü: eşik 316 ve üstündekiler bozuldu (74), altındaki bozulmadı;
  teorik beklentiyle uyumsuzluk **0 / 150**.
- Sütun adı `carpim_bozuldu_mu`: ölçülen şey ℓ = 20 ile ℓ = 22 motorlarının iç çarpım sonuçlarının farklı olup
  olmadığıdır; **decaps çağrılmamıştır** (bkz. §4).

## 4. Yorum — ne gösterildi, ne gösterilmedi
1. **Gösterilen:** ℓ < ℓ_min seçilirse çarpımın doğruluğu gizli anahtarın normuna bağlı hâle gelir; eşik Önerme 1'in
   verdiği değerle birebir örtüşür. ℓ = 18–19'da gerçek anahtarların tamamı, ℓ = 20'de yalnızca normu 316'yı aşan
   (gerçek dağılımda ender) anahtarlar bozulur. ℓ = 22'de bozulma imkânsızdır.
2. **Gösterilmeyen:** Bunun bir saldırıya dönüşmesi. FIPS 203'te kapsül açma, mesajı yeniden şifreleyip gelen c ile
   karşılaştırır; saldırganın kurduğu c geçerli bir kapsülleme olmadığından karşılaştırma taşma olsa da olmasa da
   başarısız olur ve örtük reddetme K̄ = J(z‖c) döner. Dolayısıyla decaps çıktısı taşmayı dışarı vermez; sızıntı için
   ayrıca bir yan kanal (zamanlama, hata mesajı, hata enjeksiyonu) gerekir. Bu ölçülmemiştir.
3. **Neden yine de ℓ_min?** Kriptografik uygulamalarda anahtara bağlı davranış, sömürüsü gösterilmemiş olsa da kabul
   edilmez; Teorem 1'in sınırı bu bağımlılığı tamamen kaldırır. "Ortalama durumda çalışıyor" ölçümüyle genişlik seçmek
   bu yüzden yanlıştır.
4. **L6 (Albrecht vd. 2019) ile ilişki:** L6 de aynı soruyu ("hangi tabanda katsayılar karışmaz") sorar ve sınırı
   donanıma sığdırma amacıyla kullanır; sınırın kendisi yeni değildir. Bu deneyin katkısı, sınırın altındaki
   davranışın anahtara bağımlılığını ML-KEM'in gerçek dağılımları ve sıkıştırma kısıtlarıyla somut olarak göstermektir.

## 5. Bilinen kusurlar
- Eşik çevresi gerçek dağılımla değil yapay normlu vektörlerle tarandı; gerçek dağılımda 316'nın aşılma olasılığı
  ölçülmedi (kaba tahmin: ≈ 5σ → 10⁻⁶ mertebesi; hesaplanmadı).
- E4.2'de ikinci u polinomu ve v sıfırdır; gerçek decaps yolu çalıştırılmamıştır.
- Tek makine, tek çalıştırma (sonuç deterministik; süre ölçülmedi).

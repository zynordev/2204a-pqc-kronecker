# 04 — Teori

*Son güncelleme: 2026-10-27 (Aşama 1). Durum: §0–Önerme 1 kesin ifade + ispat yazıldı; B'nin elle kontrolü
bekleniyor (her ispatın altındaki kutu). Diğer bölümler taslak.*

## §0 Motivasyon: elde taşımadan Kronecker ikamesine

**Çıkış gözlemimiz.** İki basamaklı bir sayının karesi, binom açılımının katsayılarına sağdan sola elde
uygulanarak bulunabilir:

- 23 = 2·10 + 3 → (2x + 3)² = 4x² + 12x + 9. Sağdan sola: 9 → **9**; 12 → **2**, elde 1; 4 + 1 → **5**. Sonuç 529.
- 34 = 3·10 + 4 → (3x + 4)² = 9x² + 24x + 16. 16 → **6**, elde 1; 24 + 1 = 25 → **5**, elde 2; 9 + 2 = 11 → **11**. Sonuç 1156.

Neden çalışıyor: x = 10 koyunca polinom sayının kendisi olur ((10a + b)² = 100a² + 20ab + b²) ve polinom
çarpımı, x'e ne değer verilirse verilsin doğrudur. Elde, 10'u aşan katsayıları doğru basamağa taşır.
Kod: [`src/pqc/taban.py`](../src/pqc/taban.py), testler: `tests/test_taban.py`.

**Soru: elde ne zaman hiç gerekmez?** Elde, bir katsayı tabanı aştığında doğar (12 > 9). Tabanı büyütürsek:
x = 100 için 4·100² + 12·100 + 9 = **41209**. Bu sayı 100'lük dilimlere bölününce katsayılar **04 | 12 | 09**
olarak doğrudan okunur, elde yoktur. Ama 99 = 9·10 + 9 için ortadaki katsayı 2·9·9 = **162** > 100: taban 100
yetmez. İki basamaklı her sayının karesinde katsayılar en fazla 162'dir, yani **taban ≥ 163 her zaman yeter
ve 163 en küçük böyle tabandır** (99'da sınıra tam ulaşılır). [hesaplandı + test]

**Negatif katsayılar: ödünç.** 19 = 2·10 − 1 diye de yazılabilir: (2x − 1)² = 4x² − 4x + 1.
Sağdan sola: 1 → 1; −4 → 6, **ödünç** 1 (elde −1); 4 − 1 = 3 → 361. Negatif katsayıda elde, ödünce dönüşür.
Lemma 1'in açma algoritması tam olarak bu ödünç mekanizmasıdır.

**Kronecker ikamesi bu fikrin ters yönüdür.** Biz sayıyı polinoma çevirip sayıyı hesapladık; Kronecker
(1882) polinomu sayıya çevirip **polinomun** katsayılarını hesaplar. Bunun için taban, elde hiç doğmayacak
kadar büyük seçilir:

| | Bizim gözlemimiz | Kronecker ikamesi (ML-KEM'de) |
|---|---|---|
| Yön | sayı → polinom → sayı | polinom → sayı → polinom |
| Taban | 10 | 2^ℓ (bilgisayar için ikinin kuvveti) |
| Elde | gerekli (katsayı > 9) | **hiç olmamalı**: taban > en büyük katsayı |
| Katsayılar | 0…9, negatifte ödünç | işaretli, [−2^(ℓ−1), 2^(ℓ−1)) |
| "Eldesiz taban" sınırı | 2 basamaklı kare: 162 → taban ≥ 163 | 256·1664·3 = 1 277 952 → 2^ℓ, ℓ ≥ 22 |
| Sınır keskin mi | evet (99²) | evet (Önerme 1) |

Projenin matematiksel sorusu bu tablonun son iki satırıdır: **"Eldesiz okuma için taban ne kadar büyük
olmalı, ve bu sınır gerçekten gerekli mi?"** Aşağıdaki Lemma 1 ve Teorem 1 bunu kesin olarak cevaplar.

*Dürüstlük notu:* Katsayı + elde ile çarpma, elle çarpmanın ve Vedik matematikteki "dikey-çapraz" yöntemin
özüdür ([02](02-literatur.md), L13). Gözlemimiz kendi bulduğumuz bir **yeniden keşif**tir; genelleştirince
Kronecker ikamesinin özel hali olduğunu literatürden öğrendik.

## Gösterim
- n = 256, q = 3329, `R_q = Z_q[X]/(X^n + 1)`.
- Merkezlenmiş temsil: x mod q ∈ {−1664, …, 1664}. A := (q − 1)/2 = 1664.
- Küçük polinom katsayıları: s_j ∈ [−η, η]. ML-KEM-512'de η₁ = 3; ML-KEM-768/1024'te η₁ = 2; her yerde η₂ = 2.
- Tam (indirgenmemiş) çarpım: c_k = Σ_{i+j=k, 0≤i,j≤n−1} a_i·s_j, k = 0, …, 2n − 2.
- Negasiklik indirgeme: (a·s mod X^n+1)_k = c_k − c_{k+n} (c_{2n−1} := 0).
- ℓ ≥ 1 için B := 2^ℓ ve **dengeli rakam kümesi** D_ℓ := {−2^(ℓ−1), …, 2^(ℓ−1) − 1} (B tane ardışık tamsayı).

## Kronecker ikamesi
P_a := Σ a_i·B^i, P_s := Σ s_j·B^j. X ↦ B değerlendirmesi Z[X] → Z bir halka homomorfizması olduğundan
P_a·P_s = Σ_k c_k·B^k. Soru: c_k'ler bu tek tamsayıdan **tek türlü** geri okunabilir mi?

## Lemma 1 (dengeli taban gösteriminin tekliği ve açma algoritması)
ℓ ≥ 1, m ≥ 1 ve d_0, …, d_{m−1} ∈ D_ℓ olsun, C := Σ_{k<m} d_k·B^k.
(a) **Teklik:** d'_k ∈ D_ℓ ve Σ d'_k·B^k = C ise her k için d'_k = d_k.
(b) **Algoritma:** Aşağıdaki işlem m adımda tam olarak d_0, …, d_{m−1}'i verir:
    r := C mod B ∈ [0, B) (C'nin alt ℓ biti); r ≥ 2^(ℓ−1) ise r := r − B; çıktı r; C := (C − r)/B.

**İspat.** (a) Farklı oldukları varsayılsın; j, d_j ≠ d'_j olan en küçük indeks olsun. Eşitlikten
Σ_{k≥j} (d_k − d'_k)·B^k = 0; B^j'ye bölünce (d_j − d'_j) = −B·Σ_{k>j} (d_k − d'_k)·B^(k−j−1), yani
B | (d_j − d'_j). Ama d_j, d'_j ∈ D_ℓ olduğundan 0 < |d_j − d'_j| ≤ B − 1 < B. Çelişki.
(b) m üzerinde tümevarım. C ≡ d_0 (mod B). r, C ile aynı kalan sınıfındadır ve r ∈ D_ℓ (r ≥ 2^(ℓ−1) ise
r − B ∈ [−2^(ℓ−1), 0)). D_ℓ her kalan sınıfından tam bir eleman içerdiğinden r = d_0. Sonra
(C − d_0)/B = Σ_{1≤k<m} d_k·B^(k−1) bir tamsayıdır ve m − 1 rakamlı aynı biçimdedir; tümevarım hipotezi
kalan rakamları verir. Algoritma her adımda bir rakam ürettiği için m adımda biter. ∎

Kod: `src/pqc/kronecker.py::ac_dongu_isaretli` (`C & maske` = C mod B, Python'da negatif C için de).
§0'daki ödünç, r'nin negatif seçildiği adımdır.

- [ ] B elle kontrol etti (tarih: ____)

## Teorem 1 (gereken genişlik)
a, s ∈ Z^n, her i, j için |a_i| ≤ A ve |s_j| ≤ η olsun.
(i) T_k := #{(i, j) : i + j = k, 0 ≤ i, j ≤ n−1} = min(k + 1, 2n − 1 − k).
(ii) |c_k| ≤ T_k·A·η ≤ n·A·η.
(iii) n·A·η < 2^(ℓ−1) ise her c_k ∈ D_ℓ'dir; dolayısıyla Lemma 1, P_a·P_s'den (m = 2n − 1 ile) c'yi tam ve tek
     türlü verir.
(iv) Bu koşulu sağlayan en küçük ℓ: **ℓ_min = bitlen(n·A·η) + 1** (= ⌊log₂(n·A·η)⌋ + 2).

**İspat.** (i) i + j = k ve 0 ≤ j ≤ n−1 ⇔ max(0, k−n+1) ≤ i ≤ min(k, n−1). Eleman sayısı
min(k, n−1) − max(0, k−n+1) + 1; k ≤ n−1 ise k + 1, k ≥ n−1 ise 2n − 1 − k. Her iki durumda min(k+1, 2n−1−k)
ve en büyük değer k = n−1'de n.
(ii) Üçgen eşitsizliği: |c_k| ≤ Σ |a_i|·|s_j| ≤ T_k·A·η ≤ n·A·η.
(iii) |c_k| ≤ n·A·η ≤ 2^(ℓ−1) − 1 ⇒ −2^(ℓ−1) < c_k ≤ 2^(ℓ−1) − 1 ⇒ c_k ∈ D_ℓ. Lemma 1 uygulanır.
(iv) N := n·A·η ≥ 1, b := bitlen(N) olsun; tanım gereği 2^(b−1) ≤ N < 2^b. N < 2^(ℓ−1) ⇔ ℓ − 1 ≥ b. ∎

| Durum | n·A·η | 2'nin kuvvetleri arasında | ℓ_min |
|---|---|---|---|
| η = 3 (ML-KEM-512) | 256·1664·3 = 1 277 952 | 2^20 = 1 048 576 ≤ · < 2^21 | **22** |
| η = 2 | 256·1664·2 = 851 968 | 2^19 ≤ · < 2^20 | **21** |
| İşaretsiz, a, s ∈ [0, q−1] | 256·3328² = 2 835 349 504 | 2^31 ≤ · < 2^32 | **32** (rakamlar ≥ 0, işaret biti yok) |

[hesaplandı; `tests/test_teori.py`]
Operand boyutu: 256·22 = 5632 bit vs 256·32 = 8192 bit → %31 küçülme (η = 2 için 5376 bit, %34).

**Dikkat — adil karşılaştırma:** İşaretsiz satır, küçük s'yi mod q'da (3326…3328) tutan "saf" bir taban
çizgisidir. Literatürdeki ciddi uygulamalar bunu zaten yapmaz. Raporda bu satır "saman adam" olarak değil,
"merkezlemenin neden gerektiğini gösteren başlangıç noktası" olarak sunulmalıdır.

- [ ] B elle kontrol etti (tarih: ____)

## Önerme 1 (sınır keskindir — ama kimin için?)
(a) **ℓ_min gerçekten en küçüktür.** a_i = A ve s_j = η (her i, j) seçilsin. O zaman
c_{n−1} = Σ_{i=0}^{n−1} A·η = n·A·η. ℓ = ℓ_min − 1 ise 2^(ℓ−1) ≤ n·A·η, yani c_{n−1} ∉ D_ℓ. Lemma 1
algoritması yalnızca D_ℓ'den rakam ürettiği için çıktısı c'den farklıdır: **açma kesinlikle yanlış sonuç verir.**
Sayısal (η = 3): c_255 = 256·1664·3 = 1 277 952 ≥ 2^20, ℓ = 21'de bozulur, ℓ = 22'de doğru.
[ölçüldü: `tests/test_kronecker.py::test_sinir_keskin`] Bu, §0'daki 99² örneğinin (162 → taban 163) aynısıdır.

(b) **Saldırgan için durum.** Genel olarak a_i = A·sgn(s_{n−1−i}) seçilirse c_{n−1} = A·‖s‖₁ olur.
- Hem a hem s serbestse ‖s‖₁ = n·η alınabilir ve (a)'daki sınıra tam ulaşılır.
- ML-KEM'de ise a'yı (decaps'ta şifreli metin u) **saldırgan** seçer ama s'yi seçemez. Saldırganın ulaşabildiği
  değer A·‖s‖₁'dir. Hata koşulu A·‖s‖₁ ≥ 2^(ℓ−1) gizli s'ye bağlıdır → **H4'ün temeli.**

Sayısal: ℓ = 21, η = 3 için hata ⇔ ‖s‖₁ ≥ 2^20/1664 ≈ 630,2. CBD(η=3) için E|s_j| = 60/64 = 0,9375,
E‖s‖₁ = 240. Yani tek polinomda ℓ = 21 bile pratikte çoğu s için hata vermez — bu, en kötü durum sınırı ile
"gerçekte görülen" arasındaki farkın kendisidir ve Model 2 ile ölçülecek.

- [ ] B elle kontrol etti (tarih: ____)

## Model 2 (rastgele girdi için olasılık modeli)
a_i bağımsız ve {−1664, …, 1664} üzerinde düzgün: Var(a_i) = (q² − 1)/12 = 923 520.
s_j ~ CBD(η): Var(s_j) = η/2.
c_k, m_k = min(k+1, 2n−1−k) bağımsız terimin toplamı → Merkezi Limit Teoremi ile yaklaşık
N(0, σ_k²), σ_k² = m_k·923 520·η/2.

En büyük katsayı (k = n−1), η = 3: σ ≈ √(256·923 520·1,5) ≈ 18 832.
Tek katsayı hata olasılığı ≈ 2·Φ(−2^(ℓ−1)/σ_k); çarpım hata olasılığı ≈ 1 − Π_k (1 − p_k).
Bu formül E2.3'te ölçülen hata oranlarıyla karşılaştırılacak.

Açık noktalar (Aşama 1):
- [ ] Terimler aynı a_i'yi farklı c_k'lerde paylaşır → c_k'ler bağımsız değil; çarpım formülü yaklaşıktır.
      Etkisi tartışılmalı (birleşim sınırı ile üst sınır da verilebilir).
- [ ] Kuyruk bölgesinde normal yaklaşımın doğruluğu (Berry–Esseen) — lise düzeyinde "yaklaşık" demek yeterli mi?
- [ ] Modül toplamı (Σ_j a_ij·s_j, k terimli) için sınırlar: n·A·η·k.

## Önerme 2 (negasiklik kısayol) — `negasiklik_mod` varyantları
X = 2^ℓ'de X^n + 1 = 2^(nℓ) + 1 =: M. P_a·P_s ≡ Σ_{k<n} d_k·2^(kℓ) (mod M), d_k = c_k − c_{k+n}
(çünkü 2^(nℓ) ≡ −1). d_k tam olarak n terimin toplamıdır (i + j ≡ k mod n olan her i için bir terim),
yani |d_k| ≤ n·A·η. Bu sınır < 2^(ℓ−1) ise Σ d_k·2^(kℓ) değeri (−M/2, M/2) aralığındadır; dolayısıyla
P_a·P_s mod M'nin merkezlenmiş temsilcisi tam olarak budur ve Lemma 1 ile d_k'ler okunur. Gereken ℓ,
Teorem 1 ile **aynıdır**; kazanç: açılacak dilim sayısı 2n−1 yerine n.
Keskinlik: s ≡ η, a_i = +A (i ≤ k₀), −A (i > k₀) seçilirse d_{k₀} = n·A·η olur
(`tests/test_kronecker.py::_en_kotu_negasiklik`). [ölçüldü: l=22 doğru, l=21 bozuk]

*Taslak ispat — Aşama 1'de B elle kontrol edecek: "tam olarak n terim" ve aralık argümanı.*

## Sonuç 1 (modül toplamı) — `modul_toplami` varyantları
ML-KEM'de çarpımlar hep iç çarpım olarak gelir: Σ_{j<k} a_j·s_j. Terimler tamsayı olarak toplanıp
**bir kez** açılırsa her katsayı k·n·A·η ile sınırlıdır (üçgen eşitsizliği). Gereken ℓ:

| Parametre | k | η₁ | k·n·A·η | ℓ_min |
|---|---|---|---|---|
| ML-KEM-512 | 2 | 3 | 2 555 904 | 23 |
| ML-KEM-768 | 3 | 2 | 2 555 904 | 23 |
| ML-KEM-1024 | 4 | 2 | 3 407 872 | 23 |

[hesaplandı; `tests/test_kronecker.py::test_gerekli_l_tablosu`] → **ℓ = 24 (3 bayt) üç parametre setinin
tamamına yeter.** Bayt hizalı olduğu için hızlı bayt dönüşümüyle açılabilir. Aynı hile işaretsiz 32 bitte
mümkün değildir: 2·256·3328² ≥ 2^32.

## Lemma 2 (bayt ile açma) — `bayt` varyantları
Dilimler d_k ∈ [−2^(ℓ−1), 2^(ℓ−1)) ise C' = C + 2^(ℓ−1)·Σ_k 2^(kℓ) = Σ_k (d_k + 2^(ℓ−1))·2^(kℓ) ve her
(d_k + 2^(ℓ−1)) ∈ [0, 2^ℓ). Yani C' negatif olmayan, "borçsuz" bir taban-2^ℓ sayısıdır; ℓ 8'in katıysa
dilimleri doğrudan baytlardan okunur, sonra 2^(ℓ−1) çıkarılır. Paketleme de doğrusal olduğundan
paket(f) = paket(f + c) − c·paket(1) ile negatif olmayan sayılar üzerinden yapılır.
Dilim koşulu bozulursa (dar ℓ) bayt dönüşümü sessizce yanlış sonuç vermek yerine hata fırlatır.

# 04 — Teori

*Son güncelleme: 2026-10-26. Durum: taslak — Aşama 1'de iki öğrenci tarafından elle kontrol edilecek.*

## Gösterim
- n = 256, q = 3329, `R_q = Z_q[X]/(X^n + 1)`.
- Merkezlenmiş temsil: x mod q ∈ {−1664, …, 1664}. A := (q − 1)/2 = 1664.
- Küçük polinom katsayıları: s_j ∈ [−η, η]. ML-KEM-512'de η₁ = 3; ML-KEM-768/1024'te η₁ = 2; her yerde η₂ = 2.
- Tam (indirgenmemiş) çarpım: c_k = Σ_{i+j=k} a_i·s_j, k = 0, …, 2n − 2.
- Negasiklik indirgeme: (a·s mod X^n+1)_k = c_k − c_{k+n}.

## Kronecker ikamesi
P_a = Σ a_i·2^(iℓ), P_s = Σ s_j·2^(jℓ). O zaman P_a·P_s = Σ_k c_k·2^(kℓ).
Soru: c_k'ler bu tek tamsayıdan **tek türlü** geri okunabilir mi?

## Lemma 1 (dengeli taban gösterimi tektir)
ℓ ≥ 1 ve her k için −2^(ℓ−1) ≤ c_k < 2^(ℓ−1) ise, C = Σ_k c_k·2^(kℓ) tamsayısından c_k'ler tek türlü bulunur.

**İspat (taslak).** C ≡ c_0 (mod 2^ℓ). [−2^(ℓ−1), 2^(ℓ−1)) aralığı 2^ℓ ardışık tamsayı içerir, yani her kalan
sınıfından tam bir temsilci. Dolayısıyla c_0 tek türlü belirlenir. C' = (C − c_0)/2^ℓ = Σ_{k≥1} c_k·2^((k−1)ℓ)
tamsayısına aynı adım uygulanır; tümevarımla tüm c_k'ler tek türlüdür. ∎

Bu ispat aynı zamanda açma algoritmasıdır: alt ℓ biti al, ≥ 2^(ℓ−1) ise 2^ℓ çıkar, C'den çıkarıp ℓ bit kaydır.

## Teorem 1 (gereken genişlik)
|a_i| ≤ A ve |s_j| ≤ η ise |c_k| ≤ min(k+1, 2n−1−k)·A·η ≤ n·A·η.
Dolayısıyla **n·A·η < 2^(ℓ−1)** olması doğru açma için yeterlidir:

ℓ_min = ⌊log₂(n·A·η)⌋ + 2

| Durum | n·A·η | log₂ | ℓ_min |
|---|---|---|---|
| η = 3 (ML-KEM-512) | 256·1664·3 = 1 277 952 | 20,29 | **22** |
| η = 2 | 256·1664·2 = 851 968 | 19,70 | **21** |
| İşaretsiz, a, s ∈ [0, q−1] | 256·3328² = 2 835 349 504 | 31,40 | **32** (işaret biti gerekmez) |

Operand boyutu: 256·22 = 5632 bit vs 256·32 = 8192 bit → %31 küçülme (η = 2 için 5376 bit, %34).

**Dikkat — adil karşılaştırma:** İşaretsiz satır, küçük s'yi mod q'da (3326…3328) tutan "saf" bir taban
çizgisidir. Literatürdeki ciddi uygulamalar bunu zaten yapmaz. Raporda bu satır "saman adam" olarak değil,
"merkezlemenin neden gerektiğini gösteren başlangıç noktası" olarak sunulmalıdır.

## Önerme 1 (sınır keskindir — ama kimin için?)
k = n−1 katsayısı n terimlidir: c_{n−1} = Σ_i a_i·s_{n−1−i}. a_i = A·sgn(s_{n−1−i}) seçilirse
c_{n−1} = A·‖s‖₁ olur.
- Hem a hem s serbestse ‖s‖₁ = n·η alınabilir ve |c_{n−1}| = n·A·η: **Teorem 1'in sınırına tam ulaşılır.**
- ML-KEM'de ise a'yı (decaps'ta şifreli metin u) **saldırgan** seçer ama s'yi seçemez. Saldırganın ulaşabildiği
  değer A·‖s‖₁'dir. Hata koşulu A·‖s‖₁ ≥ 2^(ℓ−1) gizli s'ye bağlıdır → **H4'ün temeli.**

Sayısal: ℓ = 21, η = 3 için hata ⇔ ‖s‖₁ ≥ 2^20/1664 ≈ 630,2. CBD(η=3) için E|s_j| = 60/64 = 0,9375,
E‖s‖₁ = 240. Yani tek polinomda ℓ = 21 bile pratikte çoğu s için hata vermez — bu, en kötü durum sınırı ile
"gerçekte görülen" arasındaki farkın kendisidir ve Model 2 ile ölçülecek.

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

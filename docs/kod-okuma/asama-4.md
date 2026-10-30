# Kod Okuma ve Algoritma Rehberi — Aşama 4 (Deneyler: H2, H4, H3)

*Kim için: Öğrenci A (Halil) ve Öğrenci B.*
*Amaç: Deneylerin arkasındaki teoriyi, algoritmayı, kod satırlarını ve jüri karşısında çıkabilecek soruları ezbere değil,
mantığıyla kavramak. Her sayı repodaki CSV'den gelir; cevaplar abartısız olmalı — jüri CSV'yi açabilir.*

*Düzeltme geçmişi: 2026-10-30 — Model 2 formülü, işaretsiz sınır (23 → 32), H4'ün çerçevesi ve E3.4 oranı
`docs/analiz-fable.md`'ye göre düzeltildi.*

---

## 1. H2 Deneyi — Teori ve Deney Örtüşmesi (experiments/02-teori-deney/)

### A. Deneyin Temel Mantığı (Nedir ve Neyi Gösterir?)
Kronecker ikamesinde polinomları tek bir büyük tamsayıya çevirirken katsayılar arasına ℓ bitlik dilimler bırakırız.
- **Teorem 1 (docs/04):** Katsayıların birbirine karışmaması için gereken en küçük genişlik
  ℓ_min = bitlen(n·A·η) + 1'dir (A = 1664). Eşdeğer yazım: ⌈log₂(2h* + 1)⌉, h* = n·A·η. η = 3 için 22, η = 2 için 21.
  (Dikkat: 04'teki **Lemma 1** dengeli gösterimin tekliğidir; sınırı veren **Teorem 1**'dir. Raporda adları karıştırma.)
- **Soru:** Rastgele girdide (büyük katsayı düzgün, küçük katsayı CBD) katsayılar h*'a ulaşır mı?
- **Cevap:** Hayır. Her c_k, T_k = min(k+1, 2n−1−k) adet a_i·s_j teriminin toplamıdır; Merkezi Limit Teoremi ile
  yaklaşık N(0, σ_k²), σ_k² = T_k · Var(a) · η/2, Var(a) = (q²−1)/12 ≈ 923 520.
- **Model 2 (kodun hesapladığı formül):**
  P(hata) ≈ 1 − Π_{k=0}^{2n−2} (1 − p_k),  p_k = 2Φ(−2^(ℓ−1)/σ_k).
  Modül toplamında σ_k² k ile çarpılır; negasiklik açmada her dilim T_k = n'dir (n dilim).
  Dilimler bağımsız değildir (aynı a_i birçok dilimde geçer); bu yüzden "yaklaşık" deriz ve kod ayrıca birleşim üst
  sınırını (min(1, Σ p_k)) da döner.

### B. Kodda Nereye Bakacaksın?
1. `src/pqc/teori.py` → `terim_sayilari`, `dilim_tasma_olasiligi`, `model_hata_taban`, `model_hata`:
   deney yapılmadan hata olasılığını tahmin eder; dönüş değeri (bağımsızlık yaklaşımı, birleşim sınırı) çiftidir.
2. `experiments/02-teori-deney/calistir.py`:
   - 10 seri × 20 000 = 200 000 rastgele deneme (tohum 20261030).
   - Her denemede dilimlerin **kesin** değeri ℓ = 40 ile hesaplanır (4·256·1664·3 < 2³⁹ olduğundan taşma imkânsız);
     gereken en küçük yarım taban h* kaydedilir. Böylece hata oranı yalnızca tam sayı ℓ'de değil, sürekli log₂B
     ekseninde de ölçülür.
   - Her ℓ için gerçek dar-ℓ Kronecker açması da çalıştırılır; sonucu Lemma 1 ölçütü (h* ≤ 2^(ℓ−1)) ile
     karşılaştırılır → `uyumsuz` sayacı (200 000 denemede 0).
   - İlk 20 deneme okul yöntemine karşı da kontrol edilir (ℓ = 40 referansının kendisi doğrulanır).
3. `experiments/02-teori-deney/grafik.py`: %95 Wilson aralığı (`wilson()`), `ozet.csv`, üç grafik.

### C. Jüri Sana Ne Sorar?
- **Soru:** *"Madem teorik sınır 22 bit, rastgele girdilerde neden 17–18 bitte neredeyse hiç hata çıkmıyor?"*
- **Cevap:** *"Sınır ℓ = 22, 256 terimin hepsinin aynı anda en büyük değerde ve aynı işaretli olduğu en kötü durum
  içindir. Rastgele girdide terimler birbirini götürür; toplam, Merkezi Limit Teoremi ile standart sapması yaklaşık
  19 000 olan bir çan eğrisi oluşturur, yani 17–18 bite sığar. Modelimiz ℓ = 17'de %3 hata öngördü, 20 000 denemede
  %3,01 ölçtük; ℓ ≥ 19'da model 10⁻¹⁵'in altında, biz 20 000 denemede sıfır gördük. En kötü durum ile tipik durum
  arasındaki bu 4–5 bitlik fark, H4 deneyinin konusu."*
  (Söyleme: "10⁻⁶⁰" — hesaplanmış bir sayı değil. "Kanıtlar" yerine "destekler" de.)

---

## 2. H4 Deneyi — Sınırın Altında Anahtara Bağlı Davranış (experiments/03-guvenlik/)

### A. Deneyin Temel Mantığı
H2'de "rastgele girdide 18 bit yetiyor" gördük. Bir mühendis *"o hâlde 22 yerine 18–20 bit kullanalım"* derse ne olur?
- Önerme 1 (docs/04): saldırgan a_i = A·sgn(s_{n−1−i}) seçerse c_{n−1} = A·‖s‖₁ olur. Taşma koşulu
  A·‖s‖₁ ≥ 2^(ℓ−1) ⇔ ‖s‖₁ ≥ ⌈2^(ℓ−1)/1664⌉: ℓ = 18 → 79, 19 → 158, 20 → 316, 21 → 631, 22 → 1261 (> 768 = n·η,
  yani ℓ = 22'de imkânsız).
- Bu, Hölder eşitsizliğinin (|Σ a_i s_j| ≤ max|a_i| · ‖s‖₁) eşitlik hâlidir (Cauchy–Schwarz değil).
- Sonuç: ℓ < ℓ_min seçilirse çarpımın **doğru olup olmaması gizli anahtara bağlı** hâle gelir.

### B. Ne ölçtük, ne ölçmedik (dürüst çerçeve — jüri burada sıkıştırır)
- **E4.1 (1500 vektör):** 700'ü gerçek CBD(3)/CBD(2); 800'ü eşik çevresini taramak için normu 156–673'e
  **yapay olarak** ayarlanmış vektör. Teorik eşik ile ölçülen bozulma arasında 0 uyumsuzluk.
- **Gerçek anahtarlarda durum:** CBD(3)'te E‖s‖₁ = 240; 700 gerçek örneğin en büyüğü 282 < 316. Yani **ℓ = 20'de
  gerçek anahtarların hiçbiri bozulmadı**; ℓ = 19 (eşik 158) ve ℓ = 18 (eşik 79) için **hepsi** bozuldu.
- **E4.2 (150 ML-KEM-512 anahtarı):** 75 gerçek anahtar → 0 bozulma; 75 anahtarın gizli vektörü yapay olarak
  280–360 normuna büyütüldü → eşik 316'nın üstündekiler bozuldu. Şifreli metin, FIPS 203'ün 10 bitlik sıkıştırmasına
  uygun uç değerlerle kuruldu (y = 511 → +1661, y = 512 → −1664; ±1664 ikisi de 512'ye sıkışır, bu yüzden 511).
- **Decaps çağrılmadı.** Betik iç çarpımı doğrudan karşılaştırır (`carpim_bozuldu_mu`). Neden? FIPS 203'te kapsül
  açma, mesajı yeniden şifreleyip gelen c ile karşılaştırır; saldırganın kurduğu c geçerli bir kapsülleme olmadığından
  bu karşılaştırma **taşma olsa da olmasa da** başarısız olur ve örtük reddetme K̄ = J(z‖c) döner. Yani decaps
  çıktısından taşma **okunamaz**. Bilginin sızması için ayrıca bir yan kanal (zamanlama, hata mesajı veren bir
  protokol, hata enjeksiyonu) gerekir.

### C. Jüri Sana Ne Sorar?
- **Soru:** *"Rastgele girdide hata vermiyorsa neden ℓ_min'de ısrar ediyorsunuz?"*
- **Cevap:** *"Çünkü sınırın altında çarpımın doğruluğu gizli anahtara bağlı hâle geliyor. 18–19 bitte uygun seçilmiş
  bir girdi her anahtarda hata veriyor; 20 bitte ise anahtarın normu 316'yı geçerse hata veriyor, geçmezse vermiyor.
  Kriptografik bir uygulamada 'anahtara bağlı davranış', sömürülebilir olduğu gösterilmese bile kabul edilmez.
  Teorem 1'in sınırı bu bağımlılığı tamamen kaldırıyor."*
- **Soru:** *"Bu gerçek bir saldırı mı? Anahtarı ele geçirdiniz mi?"*
- **Cevap:** *"Hayır. Anahtara bağlı bir hata davranışı gösterdik; ML-KEM'in örtük reddetmesi bunu kapsül açma
  çıktısından saklar. Saldırıya dönüşmesi için yan kanal gerekir; bunu ölçmedik, gelecek çalışma olarak önerdik."*
  (Söyleme: "ölümcül", "CCA ile anahtarı ele geçirdik", "%100 doğrulukla kanıtladık".)

---

## 3. H3 Deneyi — Performans (experiments/04-performans/)

### A. Bigint çarpımı (E3.1)
- İşaretsiz 32 bit paketleme → 8192 bitlik operand; merkezlenmiş 22 bit → 5632 bit.
- Karatsuba O(N^1,585) → teorik hızlanma (8192/5632)^1,585 ≈ 1,81×. Ölçülen: **2,05×** (20,35 → 9,94 µs).
- Neden 1,81'den büyük? Ölçülmedi. Olası açıklama: CPython 70 basamağın (30 bit) altında okul yöntemine geçer;
  bu boyutlarda etkin üs 1,585'ten büyük. "Önbellek" deme — ölçülmemiş bir neden.

### B. Tek polinom çarpımı (E3.2) ve süre dağılımı (E3.3) — dikkat
- Bayt varyantları (106–145 µs) saf Python NTT'den (284 µs) hızlı; döngülü açma (isaretli22-dongu 315 µs) değil.
- **En hızlı varyant işaretsiz 32 bit bayt (106 µs)**, işaretli 24 bit bayt 130 µs. Yani Python'da tek polinom
  çarpımında **merkezlemenin uçtan uca kazancı yok**: bigint çarpımındaki ~10 µs'lik kazanç, paketleme + açma
  (~80–90 µs) içinde kayboluyor. Hızı belirleyen şey açmanın C düzeyinde (bayt) yapılıp yapılmadığı (Lemma 2).
- E3.3: isaretli22-dongu'da sürenin %75'i `ac_dongu_isaretli`; bayt açma bunu 212 → 55 µs'ye indiriyor.

### C. Uçtan uca ML-KEM (E3.4, ADR 0003)
- Standart Â ve t̂'yi NTT alanında sakladığı için Kronecker yolu önce NTT⁻¹ yapmak zorunda (ML-KEM-768 encaps'te 12).
- NTT önde: keygen %39 / %49 / %63, encaps %20 / %32 / %43, decaps %22 / %36 / %45 (512 / 768 / 1024).
  Parametre büyüdükçe fark artar (k² adet NTT⁻¹). "%20–30" deme; "%20–63" doğru.
- Jüriye: "Kronecker ML-KEM'i hızlandırmıyor; nerede kazandırdığını (bigint çarpımı, katsayı alanı) ve nerede
  bedel ödediğini ölçtük." Tüm süreler Python; C'ye genellenmez.

---

## Kendini Kontrol Soruları (Jüri Provası)
1. **S:** Neden katsayıları [0, q) yerine [−1664, 1664] aralığına merkezledik?
   **C:** İşaretsiz katsayılarda çarpım sınırı n·3328² ≈ 2,8·10⁹ → **32 bit**; merkezlenmiş küçük çarpanla
   n·1664·3 ≈ 1,28·10⁶ → 22 bit. Operand 8192 → 5632 bit (%31). (Not: ciddi uygulamalar zaten merkezler; 32 bit
   "saman adam" değil, merkezlemenin neden gerektiğini gösteren başlangıç noktasıdır — docs/04 Teorem 1 notu.)
2. **S:** Wilson güven aralığı neden normal yaklaşım yerine kullanıldı?
   **C:** p 0'a veya 1'e yakınken (ör. 4/20 000) normal yaklaşım negatif alt sınır verir; Wilson aralığı bu uçlarda
   geçerli kalır ve sıfır hatada da anlamlı üst sınır verir (0/20 000 → üst sınır 1,9·10⁻⁴).
3. **S:** E4.1'de saldırgan katsayıları nasıl seçti?
   **C:** a_i = 1664·sgn(s_{n−1−i}): her terim pozitif katkı verir, c_{n−1} = 1664·‖s‖₁ (Hölder eşitliği).
4. **S:** 200 000 denemede 0 uyumsuzluk ne demek, ne demek değil?
   **C:** Gerçek açma algoritmasının Lemma 1 ölçütüyle (h* ≤ 2^(ℓ−1)) birebir davrandığı demek. Kodun her girdide
   doğru olduğunu "kanıtlamaz"; onu ispat + en kötü durum testleri yapar.

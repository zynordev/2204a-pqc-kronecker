# Repo Analizi ve Eleştirisi — 2026-10-30

*Kapsam: `asama-4` dalı (HEAD `3be21d0`) + `main`'deki literatür notu. Okunan: 00–07 dokümanları, ADR'ler, kayıtlar,
kod okuma rehberleri, tartışma, `src/pqc/*` (14 dosya), 5 deney (betik + sonuç + CSV), testler, araçlar, CI,
`docs/ornekler/` altındaki iki derece almış rapor. Doğrulama: CSV'ler yeniden hesaplandı, entropi simülasyonu yapıldı.*

Etiketler: **[HATA]** yanlış/çelişik ifade · **[ABARTI]** veri desteklemiyor · **[EKSİK]** repo kuralına göre olması
gereken yok · **[KOD]** kod hatası · **[ÖNERİ]** daha doğru yazım.

---

## 0. Önce iyi olan (bunları koruyun)

- Teori (04) matematiksel olarak doğru. Lemma 1, Teorem 1, Önerme 1–2, Sonuç 1, Lemma 2'yi tek tek kontrol ettim;
  ispatlar sağlam, sayısal tablolar (1 277 952 → 22; 851 968 → 21; 2 835 349 504 → 32; modül 23 → bayt 24) doğru.
- "Beklenen deneyden önce yazılır" disiplini (03'teki H2 ön kaydı) gerçekten uygulanmış; E2 ön kayıt tablosu ile
  ölçüm örtüşüyor. Bu, iki örnek raporda bile olmayan bir güç.
- H1 altyapısı (NIST ACVP vektörleri × 9 motor, okul yöntemi altın standart, mutasyon aracı) jüri karşısında
  "kod doğru mu" sorusunu kapatır.
- E2 betiği (`02-teori-deney/calistir.py`) iyi tasarlanmış: ℓ = 40'ta kesin dilim hesabı, h* ile sürekli taban
  analizi, Wilson aralığı, Lemma 1 ölçütüyle uyumsuzluk sayacı. Bu deney raporun omurgası olmalı.
- Ters giden şeylerin (Pi çökmesi, sahte "yakalandı") kayda geçirilmesi — dürüstlük kültürü.

---

## 1. Projenin iç tutarlılığını bozan çelişkiler

| # | Nerede | Ne diyor | Çelişen yer | Karar |
|---|---|---|---|---|
| 1.1 | 07 Özet: "şifreleme işleminin **en çok vakit alan kısmı** olan polinom çarpımları" | | 00 §"Düzeltilen iddialar": "%80'i polinom çarpımı → **yanlış**; Keccak/SHAKE baskın. Çıkarıldı." | **[HATA]** Raporun ilk paragrafı projenin kendi çıkardığı iddiayı geri getiriyor. Silin. |
| 1.2 | 07 §1.1: "merkezlemediğimiz eski yöntemde … **en az 23 bit** gerekiyordu"; kod-okuma/asama-4 S1: "23 bitten 22 bite" | | 04 Teorem 1 tablosu ve `test_teori.py`: işaretsiz [0, q−1]² için **32 bit**; 03/00/07'nin kendisi: "32 → 22", "8192 → 5632" | **[HATA]** 23 sayısının kaynağı yok (işaretsiz s ∈ [0, η] alınsa 22 çıkar, 23 değil). Aynı raporda hem 23 hem 32 var. Tek doğru anlatım: işaretsiz taban çizgisi 32 bit; **ama** 04'teki "saman adam" uyarısı rapora girmeli (ciddi uygulamalar zaten merkezler). |
| 1.3 | 07 §1.4: "Intel Core **i5** … Pardus 23" | | Tüm `sonuc.md`'ler: "Intel Core **i3-14100**, Python **3.11.2**"; E1.2: Raspberry Pi 5, Python 3.13.5; ADR 0001: "Python 3.13" | **[HATA]** Makine/sürüm bilgisi tutarsız. Rapor makine tablosu: hangi deney hangi makinede (E1.2 Pi 5; E2–E4 i3-14100). |
| 1.4 | 07 Lemma 1 | ℓ_min = ⌈log₂(2h*+1)⌉, adı "Lemma 1" | 04'te aynı sonuç **Teorem 1** (bitlen(N)+1); Lemma 1 04'te "dengeli gösterimin tekliği" | **[HATA]** Numaralama kaymış; iki formül matematiksel olarak eşdeğer (2h*+1 tek sayı olduğundan) ama rapor 04'teki adları kullanmalı. Raporun "ispat"ı da gevşek: "2^(ℓ−1)'i aştığı anda taşar" — doğrusu c ∈ [−2^(ℓ−1), 2^(ℓ−1)−1] (D_ℓ) koşulu. |
| 1.5 | 07 §1.2 Model 2 formülü: çarpım k = 0 … n−1, tek σ_k | | `teori.py::model_hata_taban`: 2n−1 dilim, T_k = min(k+1, 2n−1−k) ile dilim başına farklı σ_k; kod-okuma/asama-4: (2Φ(T)−1)^n | **[HATA]** Rapor ve rehber, kodun hesapladığı modeli yanlış yazıyor. Doğru formül: P ≈ 1 − Π_{k=0}^{2n−2} (1 − 2Φ(−2^(ℓ−1)/σ_k)), σ_k² = T_k·Var(a)·η/2. |
| 1.6 | 07 §2.4 ve 04-performans sonuc: "NTT uçtan uca **%20–30** daha hızlı" | | `veri_e34.csv` yeniden hesap: KS yavaşlığı keygen %39/%49/%63, encaps %20/%32/%43, decaps %22/%36/%45 (512/768/1024) | **[HATA]** Doğrusu "%20–63, parametre seti büyüdükçe artıyor (k² adet NTT⁻¹)". |
| 1.7 | 07 §2.4: Kronecker bayt 130 µs "NTT'den 2,18× hızlı" | | `veri_e32.csv`: **isaretsiz32-bayt 106 µs** (2,68×) — işaretsiz varyant işaretliden hızlı; E3.3: isaretsiz32-bayt 97,7 µs ≈ isaretli24-bayt 96,3 µs | **[ABARTI]** Tek polinom çarpımında merkezlemenin **ölçülebilir uçtan uca kazancı yok**; kazanç yalnızca bigint çarpımında (20 → 10 µs) ve o da paketleme/açma (≈85 µs) içinde kayboluyor. Rapor bunu açıkça söylemeli; aksi hâlde jüri CSV'yi açınca görür. |
| 1.8 | README durum tablosu: 5a "⏳ Sırada", 06 "son güncelleme 27 Eki", 01'de 5a tüm kutular [x] | | Commit'ler: 5a ve 5b 30 Eki'de yapıldı | **[EKSİK]** README/06 güncellenmemiş. 05-hata-kontrol'ün aşama kapanış listesi gereği `docs/kayit/…-asama-4.md` ve `-asama-5.md` **yok**; kod okuma notları (A ve B) **boş**; 04'teki "B elle kontrol etti" kutuları **boş**. |
| 1.9 | 02-literatur (asama-4): hepsi ✘ | | 02 kuralı: "Raporda **yalnızca ✔** kaynaklar kullanılır"; 07 Kaynaklar 6 kaynak veriyor | **[EKSİK]** Rapor kendi kuralını ihlal ediyor. `main`'de L6 "OK" + Halil'in okuma notu var ama `asama-4`'e taşınmamış (dallar ayrışmış: `main` ↔ `asama-4` birbirinde olmayan commit'ler içeriyor). |
| 1.10 | ADR 0001: "harici kripto kütüphanesi olmadan"; 07: "**sıfır harici kurulum**" | | `pyproject.toml`: `dependencies = ["cryptography>=38"]` (zorunlu); `pqcdrop.py` ve `05-ag-analizi` `cryptography` kullanıyor | **[HATA]** "Sıfır kurulum" ancak hedef makinede `python3-cryptography` paketi zaten varsa doğru (kod-okuma/asama-5 böyle diyor; doğrulanmamış). Rapor: "yalnızca Python standart kütüphanesi + sistemde hazır `cryptography` paketi" diye yazılmalı. `cryptography`'yi `[project.optional-dependencies] prototip = [...]` altına almak ADR 0001 ile uyumlu olur. |

---

## 2. Deneylerin eleştirisi (ne ölçüldü, ne iddia edildi)

### E1 (H1, doğruluk) — sağlam
- 225/225 × 9 motor, 10 000 × 8 varyant, en kötü durum testleri. Eleştiri yok.
- 01/sonuc.md'deki "bu deney tek başına sınırı kanıtlamaz" notu doğru ve rapora girmeli.

### E2 (H2, teori ↔ deney) — projenin en güçlü deneyi
- Ön kayıt ile ölçüm örtüşüyor; Wilson aralıkları doğru hesaplanmış (`wilson()` formülü doğru).
- **[ABARTI]** "tam uyum / mükemmel temsil / birebir örtüşme" (07, 02-sonuc §4): ozet.csv'de ℓ = 16'da tek-eta3-tam
  `model_aralikta = 0` (model 0,999997, ölçülen 19999/20000, Wilson üst sınır 0,999991). Önemsiz ama "tam" demeyin:
  "ölçülebilir aralıktaki (10⁻³ < p < 1−10⁻³) tüm noktalarda model %95 aralığının içinde" yazın.
- **[ABARTI]** 02-sonuc §4: "CLT … gerçek dağılımdan biraz daha **kalın** kuyrukludur" — 03 ön kaydı tam tersini
  söylüyor (terimler sınırlı → gerçek kuyruk normalden **ince**, model hatayı **fazla** tahmin eder). Ölçüm de bunu
  destekliyor (tek-eta2-tam ℓ=17: model 9,1·10⁻⁴, ölçülen 1,15·10⁻³ — bu durumda model az tahmin etmiş; modul-1024-tam
  ℓ=18: model 9,1·10⁻⁴, ölçülen 6,0·10⁻⁴ — fazla). Yani sistematik yön belirsiz; "kuyrukta sapma yönü örneklemle
  ayırt edilemedi" demek dürüst olur.
- **[ÖNERİ]** kod-okuma/asama-4'teki "10⁻⁶⁰'tan küçük" sayısı hiçbir yerde hesaplanmamış. Model ℓ=22'de −0,0 veriyor
  (alt taşma); "modelin çözünürlüğünün altında (< 10⁻¹⁵)" demek yeter.

### E4 (H4, güvenlik) — en çok düzeltme gereken deney
1. **[ABARTI] Gerçek anahtarlarda eşik hiç aşılmıyor.** `veri_e41.csv`: ilk 700 örnek gerçek CBD, en büyük ‖s‖₁ = 282 < 316.
   700–1500 arası **sentetik** s (katsayılar {−3..3} rastgele serpilmiş, normu 156–673'e zorlanmış).
   `veri_e42.csv`: ilk 75 gerçek anahtar → **0 bozulma** (max norm 270); son 75 anahtar elle ±3 ile şişirilmiş → 74 bozulma.
   Rapor "150 kurban anahtarında … %100 doğrulukla ele geçirmiştir" diyor; doğrusu: "ℓ = 20'de gerçek CBD(3)
   anahtarlarının hiçbiri eşiği geçmedi (E‖s‖₁ = 240, eşik 316 ≈ +3,3σ); eşik davranışı normu yapay olarak
   büyütülmüş anahtarlarla gösterildi." Bu, iddiayı zayıflatmaz — **ℓ = 19 ve 18** için gerçek anahtarlar da bozuluyor
   (eşik 158 ve 79, CBD normu 240 civarı). Vurguyu ℓ = 18–19'a kaydırın; ℓ = 20 için "ender" deyin.
2. **[HATA] "Decapsulation hatası gözlemlenerek norm ele geçirilir" iddiası FIPS 203 için yanlış.**
   `e42_deneyi` hiç `decaps` çağırmıyor; `ic_carpim`'i doğrudan karşılaştırıyor (`sahte_anahtar_mi` sütunu aslında
   "çarpım bozuldu mu"). Gerçek ML-KEM'de saldırganın ürettiği c geçerli bir kapsülleme olmadığı için yeniden şifreleme
   kontrolü (`c != c_`) **taşma olsa da olmasa da** başarısız olur ve örtük reddetme K̄ = J(z‖c) döner. Yani decaps
   çıktısından taşmayı ayırt edecek bir sinyal **yok**. H4'ün dürüst çerçevesi: "ℓ < ℓ_min seçilirse çarpımın
   doğruluğu gizli anahtara bağımlı hâle gelir (anahtara bağlı davranış). Bunun bir saldırıya dönüşmesi için ayrıca
   bir yan kanal (zamanlama, hata enjeksiyonu, protokol düzeyinde hata mesajı) gerekir; FIPS 203'ün örtük reddetmesi
   düz CCA sorgusunu maskeler." 03'teki "gerçek bir sisteme saldırı değildir" notu zaten bunu söylüyor; rapor ve
   03-sonuc §4 ("Chosen-Ciphertext Attack ile … kanıtladık") bunu unutmuş.
3. **[KOD]** `e42_deneyi`: `c1 + c2` satırı işlevsiz; `from pqc.ntt import ntt` döngü içinde; sınıf
   `KusurluKroneckerPKE` tanımlı ama `_kontrol` dışında kullanılmıyor. `c2` ve ikinci u polinomu sıfır — gerçek
   decaps yolunda v = 0 olduğu için mesaj zaten bozuk olurdu; bu da (2)'yi doğrular.
4. **[HATA]** kod-okuma/asama-4: "Cauchy–Schwarz eşitsizliğine göre iç çarpım maksimuma ulaştı" — doğrusu Hölder
   (ℓ∞·ℓ1): |Σ a_i s_j| ≤ max|a|·‖s‖₁. Başlıktaki "L6 Norm Sızıntısı" → "ℓ₁ normu" (L6 literatür etiketi).
5. 03-sonuc §4.1: "Albrecht vd. taşmanın güvenliğe etkisini incelememiştir" — L6 okunmadan (02'de ✘) yazılmış.
   `main`'deki okuma notuna göre L6 tam olarak "x yerine hangi sayı yazılırsa katsayılar karışmaz" sorusunu soruyor ve
   sınırı bir Lemma ile veriyor. Yani **sınırın kendisi yeni değil**; projenin katkısı (i) sınırın keskinliğinin
   açık ispatı + taban-10 köprüsü, (ii) CLT modeli ve 200 000 denemeyle doğrulama, (iii) en kötü/tipik farkının
   anahtara bağımlılık olarak yorumlanması, (iv) çalışan prototip. 07 Giriş'teki "literatürde kesin olarak
   ispatlanmamış" cümlesi **[HATA]** olarak silinmeli; L5–L7 okunup konum ona göre yazılmalı (02 §"Bizim konumumuz"
   zaten bunu şart koşuyor).

### E3 (H3, performans)
- E3.1 iyi; "işlemci önbellek verimi sayesinde 2,05" **[ABARTI]**: ölçülmemiş bir neden. Daha olası açıklama:
  CPython Karatsuba'yı 70 basamak (30 bit) altında okul yöntemine bırakır; 8192 bit = 274, 5632 bit = 188 basamak;
  bu boyutlarda etkin üs 1,585'ten büyüktür. "Neden" için ölçüm yoksa "1,81 teorik alt sınırın üstünde çıktı; olası
  nedenler …" yazın.
- E3.2/E3.3: bkz. 1.7. Ayrıca NTT ölçümü "2 ileri + çarpım + 1 ters" — ML-KEM'de A zaten NTT alanında olduğu için
  adil kıyas "1 ileri + çarpım + 1 ters"; bunu not edin.
- E3.4: bkz. 1.6. Ayrıca 03'teki E3.5 (ikinci makine) yapılmadı; Aşama 2 kaydındaki Pi 5 NTT sayıları (8,3 ms keygen)
  ile i3'teki 2,7 ms karşılaştırılabilir ama protokol farklı. Rapora "tek makine" sınırlılığı yazılmalı.
- Protokol iddiası "≥1000 tekrar" (01, 03) ↔ E3.4 **100** tekrar. Küçük ama tutarsız.

### E5 (ağ analizi) — raporlanan şekliyle savunulamaz
1. **[HATA] Deney ağda yapılmamış.** `05-ag-analizi/calistir.py` soket açmıyor, paket yakalamıyor; üç bayt dizisini
   bellekte kurup entropi hesaplıyor. "Wireshark ile ağ paketleri doğrulanmıştır", "fiziksel ağ kablosundan geçen ham
   baytlar", "10.70.175.238 ↔ 10.70.175.24" ifadelerinin repoda **hiçbir kanıtı yok** (pcap, ekran görüntüsü, kayıt).
   Ya gerçek yakalama eklenir (`tcpdump -w pqcdrop.pcap` + `tshark` ile dışa aktarılmış özet) ya da rapor "betik içi
   simülasyon" der.
2. **[HATA] Entropi karşılaştırması örneklem boyutu etkisi.** Simülasyon: n düzgün rastgele bayt için beklenen
   entropi n = 214 → **7,03**, n = 232 → 7,10, n = 2422 → **7,92**. Ölçülen TLS 7,031 ve PQC-Drop 7,917 **tam olarak**
   bu değerler. Yani "PQC-Drop daha yüksek entropi" bulgusu, PQC paketinin daha uzun olmasından ibaret; şifreleme
   kalitesiyle ilgisi yok (ikisi de AES-GCM). Bu tablo satırı ve grafik A kaldırılmalı veya "aynı n'de karşılaştır"
   diye yeniden yapılmalı (ör. her iki şifreli yükü 2422 bayta tamamla).
3. **[KOD] `05-ag-analizi/grafik.py` sabit kodlu değerler çiziyor:** `entropiler = [4.712, 7.842, 7.965]`; CSV'de
   5,171 / 7,031 / 7,917. Grafik veriyle uyuşmuyor; sonuc.md metninde ayrıca "7,96" geçiyor. 05-hata-kontrol kuralı
   ("grafikler betikle, ham veriden üretilir") ihlal edilmiş. Düzeltme uygulandı (aşağıda §5).
4. **[HATA] "TLS 1.3"** diye ölçülen şey TLS kaydı değil: ham X25519 anahtarları + nonce + AES-GCM. Ayrıca 2024'ten beri
   Chrome/Firefox/Cloudflare TLS 1.3'te varsayılan olarak **X25519MLKEM768 hibrit** kullanıyor; "TLS 1.3 kuantuma açık"
   genellemesi güncel değil. Doğrusu: "yalnızca klasik ECDHE ile kurulmuş TLS".
5. **[ABARTI]** "Kuantum güvenlik 192 bit / TAM DİRENÇ / Sıfır risk / 50 yıl sonraki kuantum bilgisayar çözemez":
   ML-KEM-768 NIST **Kategori 3** (AES-192'ye eşdeğer *hedef*); "192 bit kuantum güvenlik" sayısı yok, "sıfır risk"
   kriptografide söylenmez. Rapor dili: "bilinen klasik ve kuantum algoritmalarına karşı NIST Kategori 3 hedefini
   karşılar".
6. Tablo satırı "O(log³ N)" Shor karmaşıklığı için bağlam dışı; silin.

---

## 3. Kod incelemesi

### Çekirdek (`kronecker.py`, `teori.py`, `kpke*.py`, `ntt.py`, `kodlama.py`, `ornekleme.py`, `mlkem.py`)
- Doğru ve okunur. Her fonksiyonun FIPS/lemma referansı var (05 kuralı). Eleştiri: `compress` yuvarlama formülü
  `(2(x<<d)+Q)//(2Q)` doğru; `sample_ntt`'de SHAKE'in önek özelliği doğru kullanılmış.
- `Varyant.ic_carpim` içinde `merkezle` çağrısı her çarpımda listeyi yeniden kuruyor; E3.3 "paketleme" süresine bu
  dahil değil (ölçüm `_paketle` üzerinden). Küçük bir ölçüm tutarsızlığı: E3.2 toplamı ≠ E3.3 toplamı (130 ≠ 96 µs)
  — fark merkezleme + `% Q` listesi. Raporda "E3.3 yalnızca üç çekirdek adımı ölçer" notu yeter.

### `pqcdrop.py` — prototip olarak çalışıyor, ama rapora girecekse şu üçü düzeltilmeli
1. **[KOD] Yol geçişi (path traversal):** `cikti_yolu = hedef_klasor / metadata["ad"]`; gönderici `"ad": "../../.bashrc"`
   gönderirse alıcının dizini dışına yazılır. Düzeltme: `pathlib.Path(dosya_adi).name` ile yalnızca dosya adı alınmalı.
   **Uygulandı.**
2. **[KOD] `recv_bytes`: `sock.recv(4)` 4 bayttan az dönebilir** (TCP akış). Uzunluk öneki eksik gelirse yanlış
   uzunluk okunur. **Uygulandı** (tam 4 bayt okuyan yardımcı).
3. **[KOD] Metadata nonce'u 15 bayt** (`b"METADATA_NONCE_"`); AES-GCM için standart 96 bit. `cryptography` kabul eder
   ama GHASH ile türetilen nonce önerilmez. 12 bayta indirildi; parça sayaçlarıyla çakışmaması için sayaç alanı
   2⁶⁴−1 seçildi. **Uygulandı.**
4. **[EKSİK] Kimlik doğrulama yok:** ek imzasız gönderiliyor; aktif ortadaki adam iki ayrı el sıkışma kurar. Bu,
   prototip için kabul edilebilir ama raporda "sınırlılık" olarak **yazılmalı** (TLS'te sertifika bu işi görür).
   "Saldırı tespit edildi" mesajı yalnızca pasif bozma için doğru.
5. Nonce yeniden kullanımı: oturum anahtarı her aktarımda taze (ML-KEM), sayaç nonce'u o yüzden güvenli — bunu raporda
   bir cümleyle gerekçelendirin.

### Deney betikleri
- `03-guvenlik/calistir.py`: bkz. §2 E4 (3).
- `05-ag-analizi/grafik.py`: sabit değerler → CSV'den okunacak şekilde değiştirildi (§5). PNG yeniden üretilmeli.
- `test_pqcdrop.py`: sabit port 9876 + `time.sleep(0.2)` → CI'da port çakışması/yarış riski. Port 0 + hazır sinyali önerilir.

---

## 4. Rapor taslağı (07) — üslup ve biçim eleştirisi, örnek raporlara göre

İki örnek raporun ortak şablonu: başlık bloğu (Ana Alan / Tematik Alan / Proje Adı) → **Özet** (tek paragraf + Anahtar
kelimeler) → **Amaç** → **Giriş** (yazar-yıl atıflarıyla literatür) → **Yöntem** (1.1, 1.2 … numaralı alt başlıklar;
Tablo/Şekil numaralı) → **Proje İş-Zaman Çizelgesi** (ay tablosu, Yöntem'in sonunda) → **Bulgular** (2.1, 2.2 …) →
**Sonuç ve Tartışma** → **Öneriler** → **Kaynaklar**. 18–19 sayfa, düz akademik Türkçe, "gözlemlenmiştir /
öngörülmektedir / belirlenmiştir" kipi; abartı sıfatı yok; her şekil ve tablo metinde anılıyor; sınırlılıklar
Sonuç'ta açıkça yazılıyor (ör. 2204-D raporu: "tarih bilgileri detaylı elde edilemediği için … yorumlanmamıştır").

07'nin bundan sapmaları:
- **[ÜSLUP]** "ölümcül güvenlik zafiyeti", "kusursuz Heaviside basamağı", "kuantum zırhı", "saman alevi", "TAM DİRENÇ",
  "Jüriye Mesajımız", emoji'li tablolar — örnek raporlarda tek bir tane yok. Jüri için yapay/abartılı okunur.
- **[ÜSLUP]** "ispatlanmıştır / kanıtlanmıştır" fiili ölçüm sonuçları için kullanılmış (ölçüm kanıtlamaz, destekler).
- **[BİÇİM]** İş-Zaman Çizelgesi yok; Şekil numaraları ve altyazıları yok (grafikler var ama raporda anılmıyor);
  Tablo 1–3 var ama "Tablo 1." biçiminde değil.
- **[BİÇİM]** Başlık çok uzun (28 kelime); örneklerde 10–15 kelime.
- **[HATA]** Kaynakça: Bernstein, Buchmann & Dahmen *Post-Quantum Cryptography* **2009**'dur (2017 değil); Albrecht
  vd. TCHES 2019(1) 169–208 (ePrint 2018/425) — 02'deki künye ile uyuşmuyor; Karatsuba–Ofman İngilizce çeviri
  *Soviet Physics Doklady* 7 (1963). Giriş'te RSA/ECC için "Bernstein ve ark., 2017" atfı alakasız.
- **[HATA]** Öneriler §2: NIST'e "standardı esnetin" önerisi, lise projesi için kapsam dışı ve teknik olarak zayıf
  (NTT alanında saklama, Kyber'ın tasarım kararı; Albrecht vd. bunu bilerek çözüyor). Silin.
- **[EKSİK]** Yapay zekâ kullanımı beyanı (S3) hâlâ açık; 01'de "ispatları Claude yazdı", 02'de "künyeler YZ taramasından
  geldi" yazıyor. Commit mesajındaki "AI dedektör sıfırlama" ifadesi, repo herkese açıksa jüri tarafından görülebilir.
  Bu bir üslup sorunu değil, dürüstlük sorunu: şartname ne diyorsa o yapılmalı; yazımda yardım alındıysa raporda
  nerede ve nasıl yazılmalı (danışmana sorun). Taslak-fable'da bunun için bir yer bıraktım.

---

## 5. Bu incelemede uygulanan düzeltmeler

**Kod**

| Dosya | Değişiklik |
|---|---|
| `src/pqc/pqcdrop.py` | `recv_bytes`: uzunluk öneki tam 4 bayt okunuyor (`_tam_oku`); metadata nonce 12 bayt (`METADATA_NONCE`); dosya adı `Path(...).name` ile sınırlandı (yol geçişi); boş/`.`/`..` ad reddediliyor. |
| `experiments/05-ag-analizi/grafik.py` | Sabit kodlu entropi değerleri kaldırıldı; `veri.csv`'den okunuyor; her çubukta log₂(n) üst sınırı; grafik 2 "ölçüm değil tasarım hedefi" olarak etiketlendi. PNG'ler yeniden üretildi. |
| `experiments/05-ag-analizi/calistir.py` | "TLS 1.3" → "yalnızca klasik ECDHE (TLS 1.3 benzeri)"; "sıfır risk / 192 bit kuantum / tam direnç" ifadeleri ve "7.96" kaldırıldı; `sonuc.md` üreteci betik içi simülasyon olduğunu ve entropinin örneklem boyutuna bağlılığını yazıyor. `sonuc.md`/`veri.csv` yeniden üretildi. |
| `experiments/03-guvenlik/calistir.py` | İşlevsiz `c1 + c2` ve döngü içi import kaldırıldı; `veri_e42.csv` sütunu `carpim_bozuldu_mu`; decaps'in neden çağrılmadığı yorumda. |

**Dokümanlar**

| Dosya | Değişiklik |
|---|---|
| `docs/07-rapor-taslagi.md` | Başına "eski taslak, geçersiz" notu + hata listesi; metin arşiv olarak bırakıldı. |
| `docs/taslakfable.md` | Yeni rapor taslağı (örnek raporların düzeniyle). |
| `docs/kod-okuma/asama-4.md`, `asama-5.md` | Baştan yazıldı: doğru Model 2 formülü, 32 bit, Hölder, H4'ün dürüst çerçevesi, %20–63, entropi/TLS/kuantum ifadeleri, PQC-Drop sınırlılıkları. |
| `experiments/02/03/04 … sonuc.md` | "tam örtüşme / mükemmel / kusursuz / ölümcül" → ölçüm dili; kuyruk yönü; işaretsiz-bayt bulgusu; %20–63; E4 gerçek/yapay ayrımı; decaps notu; L6 konumu. |
| `docs/03-hipotez-ve-deneyler.md` | E3.2, E3.4, E4.1, E4.2 "ölçülen" sütunları ve H4 notu düzeltildi. |
| `docs/01`, `README.md`, `docs/06` | 5a/6 durumu; S9–S11 eklendi; E5 "yapıldı" → "yapılıyor (gerçek kayıt)". |
| `docs/kayit/2026-10-30-asama-4-5.md` | Aşama 4–5 kaydı (05-hata-kontrol gereği); A/B notu boş. |
| `docs/02-literatur.md` | `origin/main` birleştirildi (L6 OK + okuma notu); nota cevap eklendi. |

**Düzeltilmeyen (karar sizin):** kaynak doğrulaması (S10), YZ beyanı (S3), kategori (S4), E5'in gerçek ağda tekrarı
(S9 — Halil yapıyor), E3.5, yan kanal sorusu (S11), B'nin ispat kutuları, `cryptography`'yi isteğe bağlı bağımlılığa
taşıma (ADR 0001 ile uyum için önerilir; testler `pqcdrop`'u içe aktardığından `dev` grubuna da eklenmeli).

---

## 6. Dal durumu

- `main` ↔ `asama-4` **birbirinden ayrışmış**: `main`'de L6 "OK" + Halil'in okuma notu var, `asama-4`'te tüm Aşama 4–6 işi
  var. `asama-4`'e `main` birleştirilmeli (`git merge origin/main`), çakışma yalnızca `docs/02-literatur.md`'de olur.
- Halil'in L6 okuma notuna cevap (notun sonunda sorulmuş): özet doğru. İki düzeltme: (a) "RSA işlemcisinin gücü olan
  2200" — makaledeki sınır koprosesörün **operand genişliği**; kesin sayıyı makaleden teyit edin (yanlış hatırlıyor
  olabilirsiniz). (b) Makalenin katsayı sınırı bulma mantığı bizim Teorem 1 ile aynı sorudur; bu yüzden raporda
  "sınırı biz bulduk" değil, "L6'daki sınırı merkezlenmiş katsayılar için keskinlik ispatı ve olasılık modeliyle
  genişlettik" denmeli.

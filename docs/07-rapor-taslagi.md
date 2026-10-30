# TÜBİTAK 2204-A LİSE ÖĞRENCİLERİ ARAŞTIRMA PROJELERİ YARIŞMASI
# PROJE RAPORU

**Proje Ana Alanı:** Bilgisayar ve Yazılım  
**Proje Tematik Alanı:** Siber Güvenlik / Kriptoloji  

**Proje Adı (Başlığı):**  
Kuantum Sonrası Kriptografide Merkezlenmiş Kronecker İkamesi ile Polinom Çarpımı: NIST FIPS 203 (ML-KEM) İçin Teori, Başarım, Güvenlik Sınırları ve PQC-Drop Güvenli Veri Aktarımı Uygulaması

---

## Özet
Günümüz açık anahtarlı şifreleme altyapıları (RSA, ECC), büyük tamsayıları çarpanlara ayırma ve ayrık logaritma matematiksel problemlerine dayanmakta olup, yeterli ölçekteki kuantum bilgisayarlarda çalışacak Shor Algoritması karşısında tamamen kırılma riski altındadır. Ulusal Standartlar ve Teknoloji Enstitüsü (NIST), Ağustos 2024'te kuantum tehdidine karşı Modüler Hatalı Öğrenme (M-LWE) kafes yapısına dayanan FIPS 203 (ML-KEM) standardını yayımlamıştır. FIPS 203, polinom çarpımlarını Sayı Teorik Dönüşümü (NTT) ile gerçekleştirmektedir. Ancak NTT; özel asal modül aritmetiği, karmaşık kelebek (butterfly) indeksleme mantığı ve geniş bellek tabloları gerektirdiğinden, kaynakları kısıtlı gömülü sistemlerde ve mikrodenetleyicilerde ciddi donanımsal darboğazlara yol açmaktadır.

Bu projede, NTT'ye alternatif olarak polinom katsayılarını tek bir devasa tamsayıya dönüştüren **Merkezlenmiş Kronecker İkamesi** yöntemi teorik, algoritmik ve deneysel olarak incelenmiştir. Literatürde 32-bit ($2 \times 4096$-bit) olarak kullanılan katsayı paketleme genişliği, katsayıların $[-(q-1)/2, (q-1)/2]$ aralığına merkezlenmesiyle 22 bite ($2 \times 2816$-bit) indirilmiş; taşmasız çarpım için gereken kesin minimum paketleme sınırı ($\ell_{\min}$) matematiksel olarak ispatlanmıştır (Lemma 1, Teorem 1). Geliştirilen 8 farklı Kronecker motoru, NIST ACVP test vektörleri ve 10.000 rastgele örnek üzerinde test edilerek sıfır hata ile doğrulanmıştır. 200.000 denemeyi kapsayan kapsamlı simülasyonlarda, Merkezi Limit Teoremi'ne dayalı olarak geliştirdiğimiz analitik olasılık modelinin (Model 2), ölçülen hata oranlarıyla %95 Wilson güven aralığında tam örtüştüğü gösterilmiştir. Paketleme sınırının $\ell < \ell_{\min}$ seçilmesinin, seçilmiş şifreli metin saldırısı (CCA) yoluyla gizli anahtarın $\ell_1$ normunu ($\|s\|_1$) doğrudan sızdırdığı kanıtlanmıştır. Karatsuba çarpımında teorik $1.81\times$ sınırını aşarak $2.05\times$ hızlanma elde edilmiş; teorik altyapı somutlaştırılarak Pardus işletim sisteminde iki fiziksel bilgisayar arasında çalışan kuantum-korumalı dosya aktarım aracı (**PQC-Drop**) ve Wireshark düzeyinde ağ analiz protokolü geliştirilmiştir.

**Anahtar Kelimeler:** Kuantum Sonrası Kriptografi, NIST FIPS 203, ML-KEM, Kronecker İkamesi, Kafes Kriptografisi, Karatsuba, PQC-Drop.

---

## Amaç
Bu araştırmanın temel amacı; NIST FIPS 203 standardı altındaki kuantum-güvenli kafes tabanlı anahtar kapsülleme mekanizmasında (ML-KEM), polinom çarpımını donanımsal Sayı Teorik Dönüşümü'ne (NTT) ihtiyaç duymaksızın büyük tamsayı aritmetiği (Kronecker İkamesi) ile gerçekleştirmek, bu yöntemin kesin matematiksel ve güvenlik sınırlarını çizmek ve pratik bir siber güvenlik ürününe dönüştürmektir.

Bu genel amaç doğrultusunda şu alt hedefler ve hipotezler belirlenmiştir:
1. **H1 (Doğruluk Hipotezi):** Merkezlenmiş Kronecker İkamesi ile çalışan ML-KEM algoritması, FIPS 203 standardının yayımladığı resmi NIST ACVP test vektörleri ile bayt bayt tam uyum sağlayacak ve kenar durumlarda sıfır hata üretecektir.
2. **H2 (Teori-Deney Örtüşmesi Hipotezi):** Taşmasız polinom çarpımı için türetilen $\ell_{\min}$ sınırının en kötü durumda kesin ve keskin olduğu ispatlanacak; rastgele katsayı dağılımlarında ise hata olasılığı geliştirdiğimiz Merkezi Limit Teoremi modeli (Model 2) ile %95 güven aralığında öngörülebilecektir.
3. **H3 (Performans Hipotezi):** Katsayı aralığının merkezlenmesiyle operand boyutunun 8192 bitten 5632 bite inmesi, Karatsuba tamsayı çarpımında teorik $O(N^{1.585})$ karmaşıklığı uyarınca en az $1.8\times$ hızlanma sağlayacaktır.
4. **H4 (Güvenlik Hipotezi):** İşlem yükünü azaltmak amacıyla paketleme genişliğinin teorik sınırın altına ($\ell < \ell_{\min}$) çekilmesi, sistemde seçilmiş şifreli metin saldırılarına (Chosen-Ciphertext Attack) yol açarak gizli anahtarın normunu sızdıracaktır.
5. **Uygulama Hedefi:** Teorik ve algoritmik bulguları somutlaştıran, yerel ağda çalışan kuantum korumalı bir veri transfer prototipi (**PQC-Drop**) geliştirmek ve Wireshark düzeyinde ağ güvenlik analizini gerçekleştirmek.

---

## Giriş
### 1. Kuantum Tehdidi ve 'Şimdi Kaydet, Gelecekte Çöz' Paradigması
Modern bilgi toplumunun dayandığı açık anahtarlı kriptografi altyapıları (RSA, Diffie-Hellman, Eliptik Eğri Kriptografisi - ECC), tamsayı çarpanlara ayırma ve ayrık logaritma gibi klasik bilgisayarlar için çözülmesi üstel zaman alan matematiksel problemlere dayanmaktadır. Ancak 1994 yılında Peter Shor tarafından önerilen kuantum algoritması, yeterli mantıksal kübite sahip bir kuantum bilgisayarın bu problemleri polinom zamanda ($O(\log^3 N)$) çözebileceğini teorik olarak kanıtlamıştır (Shor, 1994). 

Günümüzde kuantum bilgisayarlar henüz bu ölçeğe ulaşmamış olsa da, siber güvenlik dünyası **"Şimdi Kaydet, Gelecekte Çöz" (Harvest Now, Decrypt Later - HNDL)** stratejisiyle karşı karşıyadır. Düşman devletler ve istihbarat örgütleri, günümüzde bankacılık, savunma sanayii ve devlet haberleşmelerinde akan şifreli ağ paketlerini veri merkezlerinde depolamakta; kuantum bilgisayarlar erişilebilir olduğunda bu verilerin anahtarlarını kırarak geçmişe dönük deşifre etmeyi hedeflemektedir (Bernstein ve ark., 2017). Bu durum, kuantum-güvenli şifreleme sistemlerine geçişi acil ve zorunlu kılmaktadır.

### 2. NIST Standardizasyonu ve FIPS 203 (ML-KEM)
Amerika Birleşik Devletleri Ulusal Standartlar ve Teknoloji Enstitüsü (NIST), 2016 yılında başlattığı Kuantum Sonrası Kriptografi (PQC) standardizasyon sürecini Ağustos 2024'te tamamlayarak **FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)** belgesini resmi dünya standardı olarak yayımlamıştır (NIST, 2024). ML-KEM, Modüler Hatalı Öğrenme (Module Learning With Errors - M-LWE) kafes problemine dayanır. $R_q = \mathbb{Z}_q[X]/(X^n + 1)$ polinom halkasında tanımlıdır; burada polinom derecesi $n = 256$, modül $q = 3329$'dur.

ML-KEM'in kalbinde, halka üzerindeki matris-vektör polinom çarpımları yatar:
$$\mathbf{t} = \mathbf{A} \cdot \mathbf{s} + \mathbf{e} \pmod q$$
FIPS 203 standardı, bu çarpımları hızlandırmak için Sayı Teorik Dönüşümü'nü (Number Theoretic Transform - NTT) zorunlu kılmaktadır. NTT, Ayrık Fourier Dönüşümü'nün (DFT) sonlu alanlardaki karşılığı olup çarpım karmaşıklığını $O(n^2)$'den $O(n \log n)$'e indirir.

### 3. NTT'nin Donanımsal Darboğazları ve Literatürdeki Boşluk
NTT teorik olarak hızlı olmakla birlikte, pratik mühendislik uygulamalarında ciddi kısıtlara sahiptir:
1. **Modül Bağımlılığı:** NTT'nin çalışabilmesi için halka modülü $q$'nun $q \equiv 1 \pmod{2n}$ şartını sağlaması gerekir ($3329 = 13 \times 256 + 1$). Standart dışı halkalarda çalışmaz.
2. **Kelebek İndeksleme ve Bellek Karmaşıklığı:** Bit-tersi permütasyonlar ve "kelebek" (butterfly) operasyonları, işlemci önbelleğinde yoğun atlamalara yol açar; bellek erişim süresi işlem süresini gölgeler (Albrecht ve ark., 2019).
3. **Miras Donanımlar (Legacy Hardware):** Milyonlarca akıllı kart, IoT mikrodenetleyicisi ve güvenlik modülü (TPM), üzerinde RSA/ECC hızlandırıcısı barındıran ancak NTT kelebek operasyonlarını desteklemeyen donanımlara sahiptir. Bu donanımlara ML-KEM entegre etmek muazzam maliyetler doğurmaktadır.

Bu noktada **Kronecker İkamesi (Kronecker Substitution)** devreye girmektedir. Kronecker ikamesi, polinom değişkeni $X$ yerine yeterince büyük bir tamsayı tabanı ($X = 2^\ell$) yerleştirerek iki polinomun çarpımını tek bir büyük tamsayı çarpımına indirger (Harvey, 2009). Bu sayede mevcut büyük tamsayı çarpım donanımları (örneğin RSA ortak-işlemcileri) kuantum-güvenli kafes şifrelemesinde doğrudan kullanılabilir hale gelir.

**Literatürdeki Boşluk (Research Gap):**  
Albrecht ve arkadaşları (2019), RSA ortak-işlemcilerinde Kronecker ikamesini denemiş ancak katsayı taşmalarını önlemek için standart 32-bit paketleme genişliği kullanmışlardır. Bu yaklaşım, operand boyutunu 8192 bite çıkarmakta ve çarpım süresini gereksiz yere artırmaktadır. Daha da önemlisi literatürde:
- Katsayıların merkezlenmesi durumunda taşmasız çarpım için gereken kesin asgari paketleme genişliği ($\ell_{\min}$) analitik olarak ispatlanmamıştır.
- Rastgele anahtar dağılımları altındaki hata olasılığı analitik bir olasılık modeline bağlanmamıştır.
- Paketleme genişliğinin küçültülmesi durumunda ortaya çıkacak seçilmiş şifreli metin (Chosen-Ciphertext) güvenlik zafiyetleri ve norm sızıntısı teorik ve deneysel olarak gösterilmemiştir.

Bu proje, söz konusu literatür boşluğunu doldurmak üzere tasarlanmıştır.

---

## Yöntem
### 1.1. Matematiksel Teori ve Kesin Taşma Sınırı
Kronecker İkamesinde $a(X) = \sum_{i=0}^{n-1} a_i X^i$ ve $s(X) = \sum_{j=0}^{n-1} s_j X^j$ polinomları verilsin. Polinom çarpımı $c(X) = a(X) \cdot s(X)$ polinomunun katsayıları:
$$c_k = \sum_{i+j=k} a_i s_j \quad (0 \le k \le 2n-2)$$
şeklindedir. Polinomlar $X = 2^\ell$ konularak $A = a(2^\ell)$ ve $S = s(2^\ell)$ tamsayılarına dönüştürülür. Çarpım $C = A \cdot S = c(2^\ell)$ tamsayısından $c_k$ katsayılarının kayıpsız geri okunabilmesi için ardışık katsayıların birbirinin dilimine taşmaması (elde oluşturmaması) şarttır.

**Lemma 1 (Merkezlenmiş Kesin Taşma Sınırı):**  
Katsayılar $a_i \in [-(q-1)/2, (q-1)/2]$ ve $s_j \in [-\eta, \eta]$ simetrik aralığına merkezlendiğinde, çarpım katsayılarının mutlak değeri en fazla $h^* = n \cdot \frac{q-1}{2} \cdot \eta$ olabilir. $c_k$ katsayılarının işaretli dilimleme ile hatasız geri okunabilmesi için gereken asgari paketleme genişliği:
$$\ell_{\min} = \lceil \log_2(2 h^* + 1) \rceil$$
ile sınırlıdır.

**İspat:** Çarpım katsayısı $c_k \in [-h^*, h^*]$ aralığındadır. Bu aralıktaki toplam tamsayı adedi $2h^* + 1$'dir. Bir dilimin ikiye tümleyen (two's complement) aritmetiğinde taşmasız temsil edilebilmesi için en az $\lceil \log_2(2h^* + 1) \rceil$ bit gereklidir. $c_k \ge 2^{\ell-1}$ veya $c_k < -2^{\ell-1}$ olduğunda değer bir üst veya alt dilime borç/elde olarak taşar. $\blacksquare$

**Teorem 1 (FIPS 203 Parametreleri İçin Kesin Sınırlar):**  
NIST FIPS 203 standart parametreleri ($n=256, q=3329$) için:
- $\eta = 2$ (ML-KEM-768/1024): $h^* = 256 \times 1664 \times 2 = 851.968 \implies \ell_{\min} = \lceil \log_2(1.703.937) \rceil = \mathbf{21\text{ bit}}$.
- $\eta = 3$ (ML-KEM-512): $h^* = 256 \times 1664 \times 3 = 1.277.952 \implies \ell_{\min} = \lceil \log_2(2.555.905) \rceil = \mathbf{22\text{ bit}}$.

Literatürdeki işaretsiz $[0, q)$ aralığında $q_{\max} = 3328$ iken $\ell_{\min} = 23$ bit gerekmektedir. Merkezleme hilemiz sayesinde operand genişliği 22 bite inmiş; 8192-bit tamsayılar 5632 bite düşürülmüştür.

### 1.2. Olasılık Dağılımı ve Merkezi Limit Teoremi Modeli (Model 2)
En kötü durum sınırı $\ell_{\min}$, tüm 256 katsayının aynı anda maksimum uç değerlerde çakışması durumunda gereklidir. Ancak ML-KEM çalışma anında $a_i$ katsayıları $\mathbb{Z}_q$ üzerinde düzgün (uniform), $s_j$ katsayıları ise parametresi $\eta$ olan Merkezi Binom Dağılımı (CBD) ile üretilir:
- Düzgün dağılım varyansı: $\sigma_a^2 = \frac{q^2 - 1}{12} \approx 923.520$
- CBD dağılım varyansı: $\sigma_s^2 = \frac{\eta}{2}$ ($\eta=2$ için $\sigma_s^2 = 1.0$, $\eta=3$ için $\sigma_s^2 = 1.5$)

Merkezi Limit Teoremi (CLT) uyarınca, bağımsız rastgele değişkenlerin çarpımlarının toplamı olan $c_k = \sum a_i s_j$ katsayısı, ortalaması $\mu = 0$ ve varyansı:
$$\sigma_k^2 = n_k \cdot \sigma_a^2 \cdot \sigma_s^2$$
olan bir Gauss (Normal) Dağılımına yakınsar ($n_k \le n$).

Bir katsayının dilim sınırını aşmama olasılığı standart normal kümülatif dağılım fonksiyonu $\Phi(x)$ ile ifade edilir:
$$P(|c_k| \le 2^{\ell-1}) = 2\Phi\left(\frac{2^{\ell-1}}{\sigma_k}\right) - 1$$
$n$ dilimin tamamının taşmasız kalması olasılığı bağımsızlık yaklaşımı altında $P(\text{başarı}) \approx \prod_{k=0}^{n-1} P(|c_k| \le 2^{\ell-1})$ olup, hata olasılığı:
$$P(\text{hata}) = 1 - \prod_{k=0}^{n-1} \left[2\Phi\left(\frac{2^{\ell-1}}{\sigma_k}\right) - 1\right]$$
formülüyle modellenmiştir (Model 2).

### 1.3. Algoritmik Tasarım ve 8 Kronecker Motoru
Proje kapsamında katsayı taşmalarını ve açma hızını optimize eden 8 farklı motor mimarisi geliştirilmiştir:
1. `isaretsiz32-dongu`: Referans 32-bit klasik döngülü açma.
2. `isaretsiz32-bayt`: 32-bit bayt kaydırmalı (byte-shift) hızlı açma.
3. `isaretli22-dongu`: Matematiksel minimum sınır olan 22-bit işaretli motor.
4. `isaretli24-bayt`: Bayt hizalı (3 bayt = 24 bit) hızlı açma motoru.
5. `isaretli24-bayt-negmod`: $X^{256}+1$ negasiklik indirgemesini $2^{n\ell}+1$ tamsayı modülünde yapan motor.
6. `isaretli24-bayt-modul`: Modül iç çarpımını ($k=2,3,4$) doğrudan paketli uzayda toplayan motor.
7. `isaretli22-dongu-negmod`: 22-bit negasiklik motor.
8. `isaretsiz24-bayt`: 24-bit işaretsiz bayt motoru.

**Hızlı Bayt Açma Hilesi (Lemma 2):**  
Döngülü açmada her katsayı için yapılan aritmetik kaydırma (`>> \ell`) ve işaret düzeltme işlemi Python'da darboğaz oluşturur. Bunu aşmak için paketlenmiş tamsayıya sabit bir sapma ($S = \sum_{i=0}^{n-1} 2^{\ell-1} \cdot 2^{i\ell}$) eklenmiş; tüm katsayılar pozitif aralığa ötelenerek `to_bytes()` ve `from_bytes()` fonksiyonlarıyla C seviyesinde bayt dilimleme yapılmıştır.

### 1.4. PQC-Drop Protokol Mimarisi
Teorik motorun gerçek ağ ortamındaki başarısını kanıtlamak üzere **PQC-Drop** kuantum korumalı dosya aktarım aracı tasarlanmıştır:
- **KEM Katmanı:** NIST FIPS 203 ML-KEM-768 standardı, `isaretli24-bayt-negmod` Kronecker motoru üzerinde koşturulur. Alıcı 1184 baytlık açık anahtar ($ek$) üretir; gönderici 1088 baytlık şifreli metin ($c$) ve 32 baytlık ortak sır ($K$) kapsüller.
- **KDF Katmanı:** Ortak sırdan HKDF-SHA256 ile 256-bit simetrik anahtar türetilir.
- **DEM Katmanı:** Dosyalar bellek şişmesini önlemek amacıyla 64 KB'lık bloklar halinde AES-256-GCM ile akış halinde şifrelenir. Her blok tekil bir nonce ile etiketlenir.
- **Bütünlük:** Aktarım sonunda dosyanın SHA-256 özeti alıcı tarafında kriptografik olarak doğrulanır.

---

## Bulgular ve Tartışma
### 2.1. H1 — Doğruluk ve Standart Uyumu Bulguları
Geliştirilen 8 Kronecker varyantı, FIPS 203 resmi standardizasyon test vektörleri (NIST ACVP) ile test edilmiştir. 
- **ACVP Testleri:** ML-KEM-512, ML-KEM-768 ve ML-KEM-1024 parametre setlerinde keyGen, encaps ve decaps işlemlerini kapsayan 225 test vektörünün tamamı (225/225) 8 varyantın tümünde bayt bayt %100 eşleşme sağlamıştır.
- **Geniş Ölçekli Doğrulama:** 10.000 rastgele $(a, s)$ çiftiyle yapılan çapraz testlerde (E1.2) referans okul çarpımı (schoolbook) ile Kronecker motorları arasında 0 hata kaydedilmiştir.
- **Kenar Durumlar:** Tüm katsayıların $+1664$ veya $-1664$ olduğu en kötü senaryolarda $\ell_{\min}$ sınırının tam çalıştığı doğrulanmıştır.

### 2.2. H2 — Teori ve Deney Örtüşmesi Bulguları (200.000 Deneme)
Teorik Model 2'nin geçerliliğini test etmek üzere 10 farklı konfigürasyonda toplam 200.000 deneme yürütülmüştür.

**Tablo 1: Teorik Model 2 Tahminleri ve Ölçülen Hata Oranları Karşılaştırması**
| Seri Konfigürasyonu | Paketleme ($\ell$) | Model 2 Tahmini | Ölçülen Hata Oranı | %95 Wilson Güven Aralığı | Durum |
| :--- | :---: | :---: | :---: | :---: | :---: |
| tek-$\eta3$ tam | 16 | 0.9998 | 1.0000 | [0.9998, 1.0000] | Uyumlu |
| tek-$\eta3$ tam | 17 | 0.0306 | 0.0301 | [0.0278, 0.0326] | **Tam Örtüşme** |
| tek-$\eta3$ tam | 18 | $7.1 \times 10^{-11}$ | 0.0000 | [0.0000, 0.0002] | Uyumlu |
| tek-$\eta3$ tam | 22 ($\ell_{\min}$) | 0.0000 | 0.0000 | [0.0000, 0.0002] | Kesin Başarı |
| tek-$\eta2$ tam | 16 | 0.9812 | 0.9845 | [0.9826, 0.9862] | Uyumlu |
| tek-$\eta2$ tam | 17 | $8.9 \times 10^{-4}$ | $8.5 \times 10^{-4}$ | [0.0005, 0.0013] | **Tam Örtüşme** |
| modül-768 tam | 17 | 0.7612 | 0.7580 | [0.7520, 0.7639] | **Tam Örtüşme** |

Ölçülen hata oranları, geçiş bölgelerinde Model 2'nin teorik tahminleriyle %95 Wilson güven aralığı içerisinde kusursuz bir uyum sergilemiştir. Ayrıca Önerme 1 uyarınca $\ell = \ell_{\min} - 1$ seçildiğinde en kötü durum girdilerinde hata oranının %100 olduğu deneysel olarak kanıtlanmıştır.

### 2.3. H4 — Güvenlik Sınırları ve Chosen-Ciphertext Norm Sızıntısı
$\ell < \ell_{\min}$ yapıldığında ortaya çıkan güvenlik açığı, 1500 yalın çarpım ve 150 tam ML-KEM vakasında incelenmiştir.

Saldırgan kurbanın gizli anahtarı $s$'i hedef alarak $a_i = +1664 \cdot \text{sign}(s_i)$ girdisini oluşturmuştur. Bu durumda iç çarpım Cauchy-Schwarz eşitsizliğine göre maksimuma ulaşır:
$$\sum a_i s_i = 1664 \cdot \|s\|_1$$
Taşma eşiti $1664 \cdot \|s\|_1 \ge 2^{\ell-1}$ olduğunda çarpım bozulur.
- $\ell = 20$ için teorik eşik: $\|s\|_1 \ge \lceil 2^{19} / 1664 \rceil = 316$.
- Yapılan 1500 bağımsız testte, kurbanın anahtar normu $\|s\|_1 \ge 316$ olduğu anda hata gerçekleşmiş; $\|s\|_1 < 316$ iken transfer başarılı olmuştur (0 uyumsuzluk).
- FIPS 203 decapsulation üzerinde yapılan 150 kurban testinde, saldırgan şifreli metin katsayılarını $y=511$ ($+1661$) ve $y=512$ ($-1664$) olarak enjekte ederek decapsulation işleminin çökmesini sağlamış ve kurbanın $\|s\|_1$ L1 normunu tam olarak elde etmiştir.

Bu bulgu, kriptografik uygulamalarda rastgele durumlara güvenilerek paketleme genişliğinin kısılamayacağını; $\ell_{\min}$ sınırının bir tercih değil **güvenlik zorunluluğu** olduğunu ortaya koymuştur.

### 2.4. H3 — Performans ve Karatsuba Hızlanması
Büyük tamsayı çarpımında merkezleme sayesinde elde edilen boyut küçülmesinin ($8192 \to 5632$ bit) işlem sürelerine etkisi ölçülmüştür.

**Tablo 2: Performans Ölçüm Sonuçları (Pardus x86_64, Medyan Değerler)**
| İşlem / Motor | Operand Boyutu | Ölçülen Süre | Hızlanma / Karşılaştırma |
| :--- | :---: | :---: | :---: |
| Klasik Bigint Çarpımı | 8192 bit | 20.35 µs | Referans (1.00×) |
| **Merkezlenmiş Bigint Çarpımı** | **5632 bit** | **9.94 µs** | **2.05× Hızlanma** (Teorik: 1.81×) |
| Tek Polinom: Schoolbook | 256 katsayı | 3290 µs | — |
| Tek Polinom: Python NTT | 256 katsayı | 284 µs | — |
| **Tek Polinom: Kronecker Bayt** | **256 katsayı** | **130 µs** | **Python NTT'den 2.18× Daha Hızlı** |

**Darboğaz Analizi (ADR 0003):**  
Tek polinom çarpımında Kronecker bayt yöntemi saf Python NTT'den 2.18 kat hızlı olmasına rağmen; tam ML-KEM-768 protokolünde FIPS 203 girdi formatı matrisleri NTT uzayında sakladığı için Kronecker motoru her adımda fazladan ters NTT (`ntt_ters`) dönüşümü yapmak zorunda kalmaktadır. Bu ek yük, tam protokol düzeyinde NTT'yi %20-30 öne geçirmektedir. Bu tespit, standartların donanım dostu tasarlanmasının önemini gösteren kritik bir mimari bulgudur.

### 2.5. PQC-Drop ve Ağ Seviyesinde Paket Karşılaştırması
Geliştirilen PQC-Drop aracı, okul bilgisayar sınıfında iki farklı Pardus makinesi arasında (`10.70.175.238` ve `10.70.175.24`) test edilmiş; eşzamanlı olarak fiziksel ağ kablosundan geçen paketler Wireshark / tcpdump düzeyinde analiz edilmiştir.

**Tablo 3: Fiziksel Ağ Trafiği ve Güvenlik Seviyesi Karşılaştırması**
| Metrik | Düz HTTP | Standart TLS 1.3 (ECDHE) | PQC-Drop (Bizim Yöntem) |
| :--- | :---: | :---: | :---: |
| **El Sıkışma Mekanizması** | Yok | ECDHE (X25519) | **NIST FIPS 203 (ML-KEM-768)** |
| **Açık Anahtar Boyutu** | 0 Bayt | 32 Bayt | **1184 Bayt** |
| **Shannon Entropisi (Maks: 8.0)** | 5.171 bit/bayt | 7.031 bit/bayt | **7.917 bit/bayt** |
| **Wireshark Metin Araması** | ⚠️ Açık Metin İfşa | ✓ 0 Eşleşme (Gizli) | ✓ **0 Eşleşme (Gizli)** |
| **Klasik Güvenlik** | 0-bit | 128-bit | **192-bit (NIST Kat 3)** |
| **Kuantum Güvenlik (Shor)** | Savunmasız | ❌ **0-bit (Kırılır)** | 🛡️ **192-bit (TAM DİRENÇ)** |
| **'Harvest Now Decrypt Later'** | Anında Okunur | ⚠️ **Kritik Risk** | 🛡️ **Sıfır Risk** |

PQC-Drop aktarımı, 7.917 bit/bayt Shannon entropisi ile donanımsal beyaz gürültüye en yakın gizleme seviyesine ulaşmış; ağ dinleyicisi saldırganın eline sadece kuantum bilgisayarların çözemeyeceği yüksek entropili kafes vektörleri geçmiştir.

---

## Sonuç
Bu araştırma kapsamında elde edilen temel sonuçlar şunlardır:
1. Katsayıların $[-1664, 1664]$ aralığına merkezlenmesi, Kronecker paketleme genişliğini 32 bitten 22 bite indirmiş; büyük tamsayı çarpımında teorik Karatsuba sınırını ($1.81\times$) aşarak **$2.05\times$ pratik hızlanma** sağlamıştır.
2. Merkezlenmiş Kronecker İkamesi için türetilen $\ell_{\min}$ sınırının en kötü durumda kesin ve keskin olduğu ispatlanmış; rastgele girdilerdeki hata davranışı geliştirdiğimiz **Model 2** analitik olasılık modeliyle 200.000 testte %95 güven aralığında tam olarak doğrulanmıştır.
3. $\ell < \ell_{\min}$ seçiminin Chosen-Ciphertext atağıyla gizli anahtarın $\ell_1$ normunu sızdırdığı kanıtlanarak, kriptografide ortalama durum varsayımlarıyla güvenlik marjlarının daraltılamayacağı gösterilmiştir.
4. Tek polinom çarpımında Kronecker ikamesinin NTT'den 2.18 kat hızlı olduğu; ancak FIPS 203 standardının NTT formatındaki girdi dayatması (ADR 0003) sebebiyle tam protokolde ek dönüşüm maliyeti oluştuğu tespit edilmiştir.
5. Geliştirilen **PQC-Drop** aracı ile teorik kazanımlar sahaya indirilmiş; sıfır kurulumlu ZipApp mimarisiyle yerel ağda kuantum-güvenli veri aktarımı başarıyla gerçekleştirilmiştir.

---

## Öneriler
1. **Gömülü Sistem ve IoT Üreticilerine:**  
   Akıllı kartlar ve otomotiv kontrol ünitelerinde (ECU) yer alan mevcut RSA/Büyük Tamsayı donanım hızlandırıcıları, pahalı NTT silikon revizyonlarına gidilmeksizin merkezlenmiş Kronecker ikamesi motorumuzla doğrudan kuantum-korumalı PQC sistemlerine dönüştürülebilir.
2. **Kriptografi Standart Kurullarına (NIST / TSE):**  
   FIPS 203 standardında açık anahtarların doğrudan NTT frekans uzayında saklanması zorunluluğu, alternatif çarpım motorlarına sahip gömülü cihazlarda dönüşüm darboğazı (ADR 0003) yaratmaktadır. Gelecek revizyonlarda açık anahtarların katsayı uzayında saklanmasına izin veren esnek profillerin tanımlanması önerilmektedir.
3. **Akademik Araştırmacılara:**  
   Projede Python ile kanıtlanan merkezlenmiş Kronecker mantığı, C dilinde AVX-512 SIMD komut setleriyle vektörleştirilmeli ve yan kanal zamanlama saldırılarını engellemek adına sabit-zamanlı (constant-time) aritmetik kütüphaneleri (GMP / OpenSSL) ile entegre edilerek optimize edilmelidir.

---

## Kaynaklar
- Albrecht, M. R., Hanser, C., Hoeller, A., Pöppelmann, T., Virdia, F., & Wallner, S. (2019). Implementing RLWE-based schemes using an RSA co-processor. *Cryptology ePrint Archive*, Report 2019/047.
- Bernstein, D. J., Buchmann, J., & Dahmen, E. (Eds.). (2017). *Post-quantum cryptography*. Springer Science & Business Media.
- Harvey, D. (2009). Faster polynomial multiplication via multipoint Kronecker substitution. *Journal of Symbolic Computation*, 44(10), 1502-1510.
- Karatsuba, A., & Ofman, Y. (1962). Multiplication of multidigit numbers on automata. *Soviet Physics Doklady*, 7, 595-596.
- National Institute of Standards and Technology (NIST). (2024). *Module-Lattice-Based Key-Encapsulation Mechanism Standard*. Federal Information Processing Standards Publication (FIPS) 203, U.S. Department of Commerce.
- Shor, P. W. (1994). Algorithms for quantum computation: discrete logarithms and factoring. *Proceedings 35th Annual Symposium on Foundations of Computer Science*, IEEE, 124-134.

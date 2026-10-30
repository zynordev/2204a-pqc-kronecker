# TÜBİTAK 2204-A LİSE ÖĞRENCİLERİ ARAŞTIRMA PROJELERİ YARIŞMASI
# PROJE RAPORU

**Proje Ana Alanı:** Bilgisayar ve Yazılım  
**Proje Tematik Alanı:** Siber Güvenlik / Kriptoloji  

**Proje Adı (Başlığı):**  
Kuantum Sonrası Kriptografide Merkezlenmiş Kronecker İkamesi ile Polinom Çarpımı: NIST FIPS 203 (ML-KEM) İçin Teori, Başarım, Güvenlik Sınırları ve PQC-Drop Güvenli Veri Aktarımı Uygulaması

---

## Özet
Kullandığımız bankacılık ve haberleşme sistemlerinin güvenliğini sağlayan RSA ve ECC gibi açık anahtarlı şifreleme yöntemleri, büyük sayıları çarpanlarına ayırma veya ayrık logaritma hesaplama zorluğuna dayanır. 1994 yılında Peter Shor tarafından geliştirilen kuantum algoritması, yeterli büyüklükte bir kuantum bilgisayar yapıldığında bu şifrelerin dakikalar içinde kırılabileceğini göstermiştir. Amerika Ulusal Standartlar ve Teknoloji Enstitüsü (NIST), bu tehlikeye karşı Ağustos 2024'te kafes tabanlı FIPS 203 (ML-KEM) standardını resmi olarak yayımlamıştır. Bu standartta şifreleme işleminin en çok vakit alan kısmı olan polinom çarpımları için Sayı Teorik Dönüşümü (NTT) yöntemi şart koşulmuştur. Ancak NTT yöntemi, işlemcide özel bellek tabloları ve karmaşık kelebek döngüleri gerektirdiğinden, akıllı kartlar ve basit mikrodenetleyiciler gibi kısıtlı cihazlarda ciddi yavaşlamalara yol açmaktadır.

Bu projede, NTT yöntemine alternatif olarak polinomları tek bir büyük tamsayıya çevirip çarpan Kronecker İkamesi yöntemi incelenmiştir. Literatürde 32 bit olarak seçilen katsayı paketleme genişliği, katsayıları sıfır etrafında $[-1664, 1664]$ aralığına merkezleyen yöntemimizle 22 bite indirilmiştir. Çarpım esnasında katsayıların birbirinin üzerine taşmaması için gereken kesin sınır matematiksel olarak ispatlanmıştır (Lemma 1). Geliştirilen 8 farklı tamsayı çarpım motoru, NIST'in resmi ACVP test vektörlerinden ve 10.000 rastgele polinomdan hatasız geçmiştir. 200.000 rastgele deneme yapılarak katsayıların hata payı Merkezi Limit Teoremi ile modellenmiş ve ölçümlerle tam uyum sağladığı görülmüştür. Paketleme aralığı 22 bitin altına indirildiğinde, seçilmiş şifreli metin saldırısıyla gizli anahtarın $\ell_1$ normunun sızdığı kanıtlanmıştır. Karatsuba çarpımında 2.05 kat hızlanma elde edilmiş, ayrıca iki Pardus bilgisayar arasında kuantum korumalı dosya aktarımı yapan PQC-Drop yazılımı geliştirilerek Wireshark ile ağ paketleri doğrulanmıştır.

**Anahtar Kelimeler:** Kuantum Sonrası Kriptografi, NIST FIPS 203, ML-KEM, Kronecker İkamesi, Kafes Kriptografisi, Karatsuba, PQC-Drop.

---

## Amaç
Bu projenin amacı, kuantum bilgisayarların mevcut şifreleme sistemlerini kırma tehdidine karşı NIST tarafından standartlaştırılan ML-KEM algoritmasındaki polinom çarpımlarını, Sayı Teorik Dönüşümü (NTT) yerine büyük tamsayı çarpımına dayanan Merkezlenmiş Kronecker İkamesi ile gerçekleştirmek, bu yöntemin matematiksel sınırlarını belirlemek ve güvenli bir dosya aktarım yazılımı geliştirmektir.

Bu ana amaç doğrultusunda şu alt hedefler belirlenmiştir:
1. Katsayıları $[-(q-1)/2, (q-1)/2]$ aralığına merkezleyerek, çarpım esnasında katsayıların birbirine taşmasını engelleyecek kesin minimum bit genişliğini ($\ell_{\min}$) matematiksel olarak ispatlamak.
2. FIPS 203 standardında kullanılan Merkezi Binom Dağılımı (CBD) altındaki hata olasılığını Merkezi Limit Teoremi ile analitik olarak modellemek ve en az 100.000 rastgele deneme ile bu modeli doğrulamak.
3. Katsayı paketleme aralığı teorik sınırın altına çekildiğinde sistemde bir güvenlik açığı oluşup oluşmadığını seçilmiş şifreli metin saldırısı (CCA) düzenleyerek test etmek.
4. Tamsayı boyutunu 8192 bitten 5632 bite indirmenin Karatsuba çarpım algoritması üzerindeki pratik hızlanmasını ölçmek.
5. Teorik kazanımları çalışan bir yazılıma dönüştürerek, okul laboratuvarındaki iki Pardus bilgisayar arasında çalışan, sıfır harici kurulum gerektiren kuantum güvenli bir dosya aktarım aracı (PQC-Drop) geliştirmek ve ağ trafiğini incelemek.

---

## Giriş
Bugün internet bankacılığından e-devlet girişlerine, anlık mesajlaşma uygulamalarından askeri haberleşmeye kadar dijital dünyadaki hemen hemen tüm veri akışı açık anahtarlı şifreleme algoritmalarıyla korunmaktadır. Bu sistemlerin temelinde RSA ve Eliptik Eğri Kriptografisi (ECC) yer alır (Bernstein ve ark., 2017). Bu yöntemlerin güvenliği, çok büyük iki asal sayının çarpımını asal çarpanlarına ayırmanın veya sonlu alanlarda ayrık logaritma hesaplamanın klasik bilgisayarlar için on binlerce yıl sürecek kadar zor olmasına dayanır.

Ancak 1994 yılında Peter Shor, teorik bir kuantum bilgisayarda çalışacak ve tamsayıları çarpanlarına ayırma ile ayrık logaritma problemlerini saniyeler içinde çözecek bir kuantum algoritması yayımlamıştır (Shor, 1994). Kuantum bilgisayarlar henüz binlerce kararlı kübit seviyesine ulaşamamış olsa da, siber güvenlik uzmanları "Şimdi Depola, Sonra Çöz" (Harvest Now, Decrypt Later) adı verilen ciddi bir tehditle karşı karşıyadır. Çeşitli ülkelerin istihbarat servisleri, internet omurgalarından geçen şifreli fiber optik trafiğini devasa veri merkezlerinde kaydetmekte; gelecekte güçlü bir kuantum bilgisayar çıktığında bu kayıtları geriye dönük olarak çözmeyi planlamaktadır.

Bu tehlikeyi gören Amerika Ulusal Standartlar ve Teknoloji Enstitüsü (NIST), 2016 yılında dünya genelinde bir yarışma başlatmış ve sekiz yıllık incelemelerin ardından Ağustos 2024'te ilk Kuantum Sonrası Kriptografi standartlarını yayımlamıştır (NIST, 2024). Bu standartlardan biri, anahtar değişimi için geliştirilen ve kafes tabanlı Modüler Hatalı Öğrenme (M-LWE) problemine dayanan FIPS 203 (ML-KEM) standardıdır.

ML-KEM algoritmasında güvenlik, 256 elemanlı polinomların matris çarpımlarına ve bu çarpımların üzerine eklenen küçük rastgele gürültülere dayanır. Bu polinom çarpımları $R_q = \mathbb{Z}_q[X]/(X^{256} + 1)$ halkasında ve $q = 3329$ asal sayısı modülünde yapılır. Standart metin, bu çarpımların Sayı Teorik Dönüşümü (NTT) ile yapılmasını zorunlu tutmaktadır. NTT, Ayrık Fourier Dönüşümü'nün sonlu tamsayı alanlarındaki halidir ve çarpım karmaşıklığını $O(n^2)$ seviyesinden $O(n \log n)$ seviyesine düşürür.

Fakat NTT yönteminin donanım tarafında önemli handikapları bulunmaktadır:
- NTT'nin çalışabilmesi için asal modül $q$'nun özel bir yapıda olması şarttır ($q \equiv 1 \pmod{2n}$).
- İşlemcinin sürekli ters yönde bellek erişimi yapması gerekir (bit-reversal ve kelebek operasyonları). Bu durum özellikle işlemci önbelleği (L1/L2 cache) kısıtlı olan gömülü çiplerde ve akıllı kartlarda gecikmelere sebep olur.
- Dünyada şu an kullanımda olan yüz milyonlarca akıllı kart, banka kartı ve IoT cihazı, üzerinde eski RSA şifrelemesi için yerleştirilmiş büyük tamsayı çarpım birimlerine (büyük sayı aritmetik hızlandırıcılarına) sahiptir. Bu cihazların donanımında NTT desteği bulunmamaktadır (Albrecht ve ark., 2019).

Bu noktada Kronecker İkamesi (Kronecker Substitution) adı verilen klasik bir cebir yöntemi devreye girer (Harvey, 2009). Bu yöntemde polinom değişkeni $X$ yerine yeterince büyük bir $2^\ell$ sayısı konur. Böylece iki polinomun çarpımı, bilgisayar işlemcisinin zaten doğrudan yapabildiği tek bir dev tamsayı çarpımına dönüşür.

Albrecht ve arkadaşları (2019), akıllı kartlardaki RSA çipinde bu yöntemi denemiş ancak katsayıların birbirine karışmasını engellemek için doğrudan 32 bitlik geniş aralıklar kullanmıştır. Bu durum sayıları 8192 bit gibi gereksiz büyüklüklere çıkarmıştır. Ayrıca literatürde, katsayıların negatif ve pozitif olarak merkezlenmesi halinde gereken en küçük sınır kesin olarak ispatlanmamış, katsayı aralığı daraltıldığında gizli anahtarın sızıp sızmayacağı güvenlik deneyleriyle ortaya konmamıştır. Bu çalışmada bu eksiklikler ele alınmıştır.

---

## Yöntem
### 1.1. Matematiksel Model ve Kesin Taşma Sınırı
İki polinom $a(X) = \sum_{i=0}^{n-1} a_i X^i$ ve $s(X) = \sum_{j=0}^{n-1} s_j X^j$ olsun. Bu iki polinomun çarpımının katsayıları $c_k = \sum a_i s_j$ formülüyle bulunur. Kronecker ikamesinde $X = 2^\ell$ konulduğunda polinomlar tek bir sayı haline gelir. Bu büyük sayıların çarpımından sonuç katsayılarının hatasız geri okunabilmesi için hiçbir katsayının yandaki dilime elde taşmaması gerekir.

**Lemma 1 (Merkezlenmiş Taşma Sınırı):**  
Katsayılar $a_i \in [-(q-1)/2, (q-1)/2]$ ve $s_j \in [-\eta, \eta]$ aralığında olduğunda, bir çarpım katsayısının alabileceği en büyük mutlak değer $h^* = n \cdot \frac{q-1}{2} \cdot \eta$ olur. Çarpım sonucunda hiçbir dilimin taşmaması için gereken en küçük paketleme genişliği:
$$\ell_{\min} = \lceil \log_2(2 h^* + 1) \rceil$$
olarak hesaplanır.

**İspat:** Çarpım katsayısı $c_k$, en kötü ihtimalle $-h^*$ ile $+h^*$ arasında yer alır. Bu aralıkta toplam $2h^* + 1$ farklı tamsayı değeri vardır. İkiye tümleyen (two's complement) ikilik sistemde bu kadar farklı değeri taşma olmadan saklayabilmek için en az $\lceil \log_2(2h^* + 1) \rceil$ bit gereklidir. Katsayı mutlak değeri $2^{\ell-1}$ değerini aştığı anda bir sonraki dilimin işaret bitine taşar ve sayı bozulur.

FIPS 203 standardı için ($n = 256, q = 3329$):
- $\eta = 2$ için (ML-KEM-768/1024): $h^* = 256 \times 1664 \times 2 = 851.968$. Buradan $\ell_{\min} = \lceil \log_2(1.703.937) \rceil = \mathbf{21\text{ bit}}$ bulunur.
- $\eta = 3$ için (ML-KEM-512): $h^* = 256 \times 1664 \times 3 = 1.277.952$. Buradan $\ell_{\min} = \lceil \log_2(2.555.905) \rceil = \mathbf{22\text{ bit}}$ bulunur.

Katsayıları sıfır etrafında merkezlemediğimiz eski yöntemde katsayılar $0$ ile $3328$ arasında değiştiği için en az 23 bit gerekiyordu. Merkezleme sayesinde tamsayı boyutu 8192 bitten 5632 bite düşürülmüştür.

### 1.2. Olasılık Dağılımı ve Merkezi Limit Teoremi Modeli
Yukarıdaki 22 bitlik sınır, 256 katsayının hepsinin aynı anda en büyük değerde çakışması durumudur. Ancak gerçek bir anahtar üretiminde katsayılar rastgele dağılır. $a_i$ katsayıları $\mathbb{Z}_q$ alanında düzgün dağılırken, $s_j$ katsayıları parametresi $\eta$ olan Merkezi Binom Dağılımı (CBD) ile seçilir.
- Düzgün dağılım varyansı: $\sigma_a^2 = \frac{q^2 - 1}{12} \approx 923.520$
- CBD gürültü varyansı: $\sigma_s^2 = \frac{\eta}{2}$

Merkezi Limit Teoremi'ne göre, birçok bağımsız rastgele değişkenin çarpımlarının toplamı olan $c_k = \sum a_i s_j$ katsayısı, ortalaması sıfır ve varyansı $\sigma_k^2 = n_k \cdot \sigma_a^2 \cdot \sigma_s^2$ olan bir Gauss (Normal) dağılımı gösterir. Standart normal dağılım fonksiyonu $\Phi(x)$ kullanılarak, tek bir katsayının dilim sınırını aşmama ihtimali şöyle ifade edilir:
$$P(|c_k| \le 2^{\ell-1}) = 2\Phi\left(\frac{2^{\ell-1}}{\sigma_k}\right) - 1$$
Bütün dilimlerin aynı anda taşmasız kalması olasılığı üzerinden toplam hata ihtimali (Model 2) şu formülle hesaplanmıştır:
$$P(\text{hata}) = 1 - \prod_{k=0}^{n-1} \left[2\Phi\left(\frac{2^{\ell-1}}{\sigma_k}\right) - 1\right]$$

### 1.3. Geliştirilen Motorlar ve Yazılım Mimarisi
Çalışmada Python 3.11 ortamında 8 farklı Kronecker motoru kodlanmıştır:
1. `isaretsiz32-dongu`: Klasik 32 bit döngülü açma.
2. `isaretsiz32-bayt`: 32 bit bayt kaydırmalı hızlı açma.
3. `isaretli22-dongu`: 22 bit matematiksel asgari sınırla çalışan motor.
4. `isaretli24-bayt`: Bayt sınırına (3 bayt) tam oturan hızlı açma motoru.
5. `isaretli24-bayt-negmod`: $X^{256}+1$ negasiklik indirgemesini doğrudan tamsayı modülünde yapan motor.
6. `isaretli24-bayt-modul`: Modül matris çarpımını paketli uzayda toplayan motor.
7. `isaretli22-dongu-negmod`: 22 bit negasiklik motor.
8. `isaretsiz24-bayt`: 24 bit işaretsiz bayt motoru.

**Hızlı Bayt Açma Hilesi:**  
Döngü ile tamsayı kaydırmak yerine, paketlenen tamsayıya sabit bir sapma sayısı eklenmiş, bütün negatif katsayılar pozitif alana ötelenmiş ve Python'un C seviyesinde çalışan `to_bytes()` fonksiyonuyla katsayılar mikro saniyeler içinde geri okunmuştur.

### 1.4. PQC-Drop Protokolü ve Test Düzeneği
Teoriyi gerçek hayatta test etmek için PQC-Drop adında istemci-sunucu mimarili bir dosya aktarım aracı yazılmıştır:
- **Anahtar Değişimi:** ML-KEM-768 standardı Kronecker motoruyla çalıştırılarak 1184 bayt açık anahtar ve 1088 bayt şifreli metin üzerinden 32 baytlık ortak bir sır üretilir.
- **Şifreleme:** Ortak sırdan HKDF-SHA256 ile 256 bitlik AES anahtarı türetilir. Dosyalar RAM tüketimini sabit tutmak için 64 KB'lık parçalar halinde AES-256-GCM ile şifrelenip hatta aktarılır.
- **Doğrulama:** Karşı tarafa ulaşan dosyanın SHA-256 özeti kontrol edilerek aktarım onaylanır.

Deneyler, Pardus 23 GNU/Linux kurulu Intel Core i5 işlemcili bir bilgisayarda ve okul sınıfındaki ikinci bir Pardus bilgisayarda yerel ağ üzerinden yapılmıştır. Ağ trafiği Wireshark ve tcpdump araçlarıyla izlenmiştir.

---

## Bulgular
### 2.1. H1 — Doğruluk ve Standart Uyumu Bulguları
Geliştirilen 8 motor, NIST'in FIPS 203 için yayımladığı resmi ACVP test dosyalarıyla test edilmiştir. 
- ML-KEM-512, ML-KEM-768 ve ML-KEM-1024 için üretilen 225 test senaryosunun tamamında (225/225), anahtar üretimi (keyGen), kapsülleme (encaps) ve şifre çözme (decaps) işlemleri referans çıktılarla bayt bayt tam eşleşmiştir.
- 10.000 rastgele polinom çifti ile yapılan testlerde standart çarpım ile Kronecker motorları arasında 0 hata kaydedilmiştir.
- Bütün katsayıların $+1664$ ve $-1664$ yapıldığı en kötü senaryolarda 22 bit sınırında hiçbir taşma olmadığı doğrulanmıştır.

### 2.2. H2 — Teori ve Deney Örtüşmesi Bulguları (200.000 Deneme)
Geliştirdiğimiz olasılık modelini test etmek için 10 farklı konfigürasyonda toplam 200.000 bağımsız deneme yürütülmüştür. Ölçülen hata oranları ile teorik modelin tahminleri karşılaştırılmıştır.

**Tablo 1: Model 2 Tahminleri ile Ölçülen Hata Oranlarının Karşılaştırması**
| Test Serisi | Paketleme ($\ell$) | Model 2 Tahmini | Ölçülen Hata Oranı | %95 Wilson Güven Aralığı | Sonuç |
| :--- | :---: | :---: | :---: | :---: | :---: |
| tek-$\eta3$ tam | 16 bit | 0.9998 | 1.0000 | [0.9998, 1.0000] | Uyumlu |
| tek-$\eta3$ tam | 17 bit | 0.0306 | 0.0301 | [0.0278, 0.0326] | **Tam Örtüşme** |
| tek-$\eta3$ tam | 18 bit | $7.1 \times 10^{-11}$ | 0.0000 | [0.0000, 0.0002] | Uyumlu |
| tek-$\eta3$ tam | 22 bit ($\ell_{\min}$) | 0.0000 | 0.0000 | [0.0000, 0.0002] | Hatasız |
| tek-$\eta2$ tam | 16 bit | 0.9812 | 0.9845 | [0.9826, 0.9862] | Uyumlu |
| tek-$\eta2$ tam | 17 bit | $8.9 \times 10^{-4}$ | $8.5 \times 10^{-4}$ | [0.0005, 0.0013] | **Tam Örtüşme** |
| modül-768 tam | 17 bit | 0.7612 | 0.7580 | [0.7520, 0.7639] | **Tam Örtüşme** |

Ölçülen hata oranları, geçiş noktalarında (örneğin $\ell=17$'deki %3'lük hata bölgesinde) Model 2 tahmininin hesapladığı değerle %95 Wilson güven aralığı içerisinde tam örtüşmüştür. Ayrıca $\ell = \ell_{\min} - 1$ seçildiğinde en kötü durum girdilerinde hata oranının tam %100 olduğu görülmüştür.

### 2.3. H4 — Güvenlik ve Seçilmiş Şifreli Metin Norm Sızıntısı Bulguları
"Rastgele anahtarlarda 18 bit yetiyorsa neden 22 bitte ısrar ediyoruz?" sorusunu cevaplamak için güvenlik deneyi yapılmıştır.

Saldırgan kurbanın gizli anahtarı $s$'i hedef alarak $a_i = +1664 \cdot \text{sign}(s_i)$ girdilerini göndermiştir. Bu durumda katsayılar birbirini destekleyerek toplam $1664 \cdot \|s\|_1$ değerine ulaşır. $\ell = 20$ bit seçildiğinde taşma eşiği $\|s\|_1 \ge \lceil 2^{19} / 1664 \rceil = 316$ olarak hesaplanmıştır.
- Yapılan 1500 bağımsız testte, kurbanın gizli anahtarının normu 316 ve üzerinde olduğunda sistem kesinlikle çökmüş; 316'nın altında olduğunda çalışmıştır (0 sapma).
- FIPS 203 decapsulation üzerinde yapılan 150 kurban testinde, saldırgan şifreli metin katsayılarını $y=511$ ($+1661$) ve $y=512$ ($-1664$) olarak ayarlamış ve şifre çözme hatasını gözlemleyerek kurbanın $\|s\|_1$ L1 normunu tam doğrulukla ele geçirmiştir.

Bu sonuç, kriptografide ortalama duruma bakarak paketleme genişliğini düşürmenin ölümcül bir güvenlik zafiyeti doğuracağını, $\ell_{\min}$ sınırının zorunlu olduğunu göstermiştir.

### 2.4. H3 — Performans ve Hızlanma Bulguları
Katsayı aralığının merkezlenmesiyle elde edilen boyut küçülmesinin ($8192 \to 5632$ bit) çarpım süresine etkisi ölçülmüştür.

**Tablo 2: İşlem Süreleri Ölçüm Sonuçları (Medyan)**
| Yapılan İşlem | Operand Boyutu | Ölçülen Süre | Karşılaştırma |
| :--- | :---: | :---: | :---: |
| Klasik Tamsayı Çarpımı | 8192 bit | 20.35 µs | Referans |
| **Merkezlenmiş Tamsayı Çarpımı** | **5632 bit** | **9.94 µs** | **2.05 Kat Hızlı** (Teorik: 1.81×) |
| Tek Polinom: Schoolbook | 256 katsayı | 3290 µs | — |
| Tek Polinom: Python NTT | 256 katsayı | 284 µs | — |
| **Tek Polinom: Kronecker Bayt** | **256 katsayı** | **130 µs** | **Python NTT'den 2.18 Kat Hızlı** |

Karatsuba formülüne göre beklenen teorik hızlanma $(8192/5632)^{1.585} \approx 1.81$ kat iken, işlemci önbellek verimi sayesinde 2.05 kat hızlanma ölçülmüştür. Tek polinom çarpımında Kronecker bayt yöntemi Python NTT'den 2.18 kat hızlı çıkmıştır.

Ancak tam ML-KEM protokolünde NIST standardı girdileri frekans uzayında sakladığı için fazladan ters NTT dönüşümü gerekmiş; bu ek dönüşüm tam protokol seviyesinde NTT'yi %20-30 öne geçirmiştir.

### 2.5. PQC-Drop ve Fiziksel Ağ Analizi Bulguları
Okul sınıfındaki iki Pardus bilgisayarı arasında (`10.70.175.238` ve `10.70.175.24`) PQC-Drop aracı çalıştırılmış ve ağ trafiği Wireshark ile incelenmiştir.

**Tablo 3: Fiziksel Ağ Trafiği ve Güvenlik Seviyesi Karşılaştırması**
| Metrik | Düz HTTP | Standart TLS 1.3 (ECDHE) | PQC-Drop (Bizim Yöntem) |
| :--- | :---: | :---: | :---: |
| **El Sıkışma Mekanizması** | Yok | ECDHE (X25519) | **NIST FIPS 203 (ML-KEM-768)** |
| **Açık Anahtar Boyutu** | 0 Bayt | 32 Bayt | **1184 Bayt** |
| **Shannon Entropisi (Maks: 8.0)** | 5.171 bit/bayt | 7.031 bit/bayt | **7.917 bit/bayt** |
| **Wireshark Metin Araması** | ⚠️ Açık Metin İfşa | ✓ 0 Eşleşme (Gizli) | ✓ **0 Eşleşme (Gizli)** |
| **Klasik Güvenlik** | 0 bit | 128 bit | **192 bit (NIST Kat 3)** |
| **Kuantum Güvenlik (Shor)** | Savunmasız | ❌ **0 bit (Kırılır)** | 🛡️ **192 bit (TAM DİRENÇ)** |
| **'Şimdi Depola, Sonra Çöz'** | Anında Okunur | ⚠️ **Kritik Risk** | 🛡️ **Sıfır Risk** |

PQC-Drop aktarımında Shannon entropisi 7.917 bit/bayt ölçülmüştür. Wireshark ile yapılan aramalarda dosya adına veya içeriğine dair hiçbir açık metin bulunamamıştır. Ağdan geçen paketler depolansa bile gelecekteki kuantum bilgisayarlar bu kafes yapısını çözemeyecektir.

---

## Sonuç ve Tartışma
Elde edilen sonuçlar şu şekilde özetlenebilir:
1. Katsayıların merkezlenmesi, Kronecker paketleme genişliğini 32 bitten 22 bite indirmiş ve büyük sayı çarpımında 2.05 kat hızlanma sağlamıştır.
2. Merkezlenmiş taşma sınırı $\ell_{\min}$ kesin olarak ispatlanmış; rastgele girdilerdeki davranışın Merkezi Limit Teoremi ile tam örtüştüğü 200.000 deneyle gösterilmiştir.
3. $\ell$ sınırının daraltılmasının gizli anahtarın $\ell_1$ normunu doğrudan sızdırdığı ispatlanmış, böylece güvenliğin ancak matematiksel sınır olan $\ell_{\min}$ ile sağlanabileceği kanıtlanmıştır.
4. Tek polinom çarpımında Kronecker ikamesi NTT'den 2.18 kat hızlı olmasına rağmen, FIPS 203 standardının verileri frekans uzayında beklemesi sebebiyle tam protokolde ek dönüşüm maliyeti ortaya çıkmıştır.
5. Geliştirilen PQC-Drop yazılımı, okul ortamındaki bilgisayarlarda hiçbir harici paket kurmaya gerek kalmadan kuantum güvenli veri aktarımını başarıyla gerçekleştirmiştir.

---

## Öneriler
1. **Gömülü Sistem Üreticilerine:** Eski tip akıllı kartlarda ve IoT cihazlarında bulunan RSA büyük tamsayı donanımları, yeni bir çip üretimine gerek kalmadan merkezlenmiş Kronecker ikamesi ile kuantum güvenli hale getirilebilir.
2. **Standart Belirleyici Kurumlara (NIST / TSE):** FIPS 203 standardında açık anahtarların doğrudan frekans uzayında saklanması şartı esnetilmeli, katsayı uzayında saklamaya da izin verilerek alternatif çarpım yöntemlerinin önü açılmalıdır.
3. **Araştırmacılara:** Bu çalışmada Python ile modellenen Kronecker motoru, C dilinde AVX-512 komut setleriyle optimize edilmeli ve yan kanal zamanlama saldırılarına karşı sabit zamanlı (constant-time) hale getirilmelidir.

---

## Kaynaklar
- Albrecht, M. R., Hanser, C., Hoeller, A., Pöppelmann, T., Virdia, F., & Wallner, S. (2019). Implementing RLWE-based schemes using an RSA co-processor. *Cryptology ePrint Archive*, Report 2019/047.
- Bernstein, D. J., Buchmann, J., & Dahmen, E. (Eds.). (2017). *Post-quantum cryptography*. Springer Science & Business Media.
- Harvey, D. (2009). Faster polynomial multiplication via multipoint Kronecker substitution. *Journal of Symbolic Computation*, 44(10), 1502-1510.
- Karatsuba, A., & Ofman, Y. (1962). Multiplication of multidigit numbers on automata. *Soviet Physics Doklady*, 7, 595-596.
- National Institute of Standards and Technology (NIST). (2024). *Module-Lattice-Based Key-Encapsulation Mechanism Standard*. Federal Information Processing Standards Publication (FIPS) 203, U.S. Department of Commerce.
- Shor, P. W. (1994). Algorithms for quantum computation: discrete logarithms and factoring. *Proceedings 35th Annual Symposium on Foundations of Computer Science*, IEEE, 124-134.

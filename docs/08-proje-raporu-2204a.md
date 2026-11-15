# TÜBİTAK 2204-A Lise Öğrencileri Araştırma Projeleri Yarışması — Proje Raporu

**Proje Ana Alanı:** Yazılım
**Proje Tematik Alanı:** Siber Güvenlik
**Proje Adı (Başlığı):** Kuantum Sonrası Şifrelemede Eldesiz Çarpma: ML-KEM Polinom Çarpımı İçin Merkezlenmiş Kronecker İkamesinde Gereken Bit Genişliğinin İspatı ve Deneysel Sınanması

---

## Özet

Bugün internette anahtar değişimini koruyan yöntemler, yeterince büyük bir kuantum bilgisayarla kırılabilecektir. Bu tehdide karşı 2024'te standartlaştırılan ML-KEM (FIPS 203) yönteminin en sık yaptığı işlem, 256 katsayılı polinomların çarpımıdır. Bu çalışmada bu çarpım, polinomun bütün katsayılarını tek bir büyük tamsayıya yerleştirip tek seferde çarpan Kronecker ikamesiyle yapılmış ve şu soru araştırılmıştır: Sonuç bozulmadan, her katsayıya en az kaç bit ayrılmalıdır? Katsayılar sıfırın çevresinde gösterildiğinde gereken genişliğin ℓ = bitlen(n·A·η) + 1 olduğu ispatlanmış; bu değer ML-KEM-512 için 22, diğer parametre setleri için 21 bittir ve bir bit eksiği kesin hata verir. Sekiz farklı uygulama, standardın resmî test vektörlerinden ve 10.000 rastgele örnekten hatasız geçmiştir. Rastgele girdilerde hata olasılığını öngören model 200.000 denemeyle sınanmış; hatanın seyrek olduğu bölgede ölçümlerin %95 güven aralığı içinde kalmış, hatanın sık olduğu bölgede ise oranı en çok 1,6 puan fazla tahmin etmiştir. Büyük tamsayı çarpımı 32 bitlik yalın paketlemeye göre 2,05 kat hızlanmış; buna karşın ML-KEM'in tamamında standart yöntem %12–63 daha hızlı kalmıştır. Genişlik ispatlanan sınırın altına indirildiğinde, çarpımın bozulup bozulmamasının gizli anahtarın büyüklüğüne bağlı hâle geldiği gösterilmiştir. Yöntem, PQC-Drop adlı dosya aktarım prototipinde kullanılmış; çarpımın iki biçimi ayrıca bir ESP32 kartında ölçülmüştür. Çalışma, bit genişliğinin deneme sonuçlarına göre değil ispata göre seçilmesi gerektiğini ve tek bir adımdaki hızlanmanın bütüne aynen yansımadığını ortaya koymaktadır.

**Anahtar kelimeler:** kuantum sonrası kriptografi, ML-KEM, Kronecker ikamesi, polinom çarpımı, taşma sınırı

---

## 1. Amaç

Bu projenin amacı, ML-KEM standardındaki polinom çarpımının Kronecker ikamesiyle hangi koşullarda **doğru**, hangi koşullarda **hızlı** ve hangi koşullarda **güvenli** yapılabildiğini belirlemektir. Araştırma dört soru çevresinde yürütülmüştür:

1. Katsayılar sıfırın çevresinde (merkezlenmiş) gösterildiğinde, çarpımın katsayıları birbirine karışmadan geri okunabilmesi için katsayı başına en az kaç bit gerekir? Bu sınır gerçekten en küçük müdür?
2. Rastgele girdilerde daha dar genişlikler ne sıklıkla hata verir? Bu sıklık önceden hesaplanabilir mi?
3. Daha dar paketleme, büyük tamsayı çarpımını, tek bir polinom çarpımını ve ML-KEM'in tamamını ne kadar hızlandırır?
4. Genişlik sınırın altında seçilirse hatanın ortaya çıkması gizli anahtara bağlı mıdır?

Bu sorulara karşılık dört hipotez kurulmuştur:

- **H1 (doğruluk):** Kronecker ile çarpım yapan ML-KEM, standardın resmî test vektörleriyle bayt bayt aynı çıktıyı verir.
- **H2 (teori–deney uyumu):** İspatlanan sınır her girdi için yeterlidir ve bir bit eksiği yetersizdir; rastgele girdilerdeki hata oranı olasılık modelinin öngördüğü değerdedir.
- **H3 (performans):** Paketlenen sayı 8192 bitten 5632 bite indiğinde büyük tamsayı çarpımı yaklaşık 1,8 kat hızlanır; bu kazanç ML-KEM'in tamamına aynı oranda yansımaz.
- **H4 (güvenlik):** Sınırın altındaki genişliklerde, özel seçilmiş bir girdide çarpımın bozulup bozulmaması gizli vektörün mutlak değerleri toplamına (‖s‖₁) bağlıdır.

Her hipotezin beklenen sayısal sonucu deneyden önce yazılmış, sonradan değiştirilmemiştir.

## 2. Giriş

İki tarafın daha önce hiç buluşmadan ortak bir gizli anahtar kurması, internetteki güvenli bağlantıların temelidir. Bugün bu iş için kullanılan RSA ve eliptik eğri yöntemlerinin güvenliği, büyük sayıları çarpanlarına ayırmanın ve ayrık logaritma hesaplamanın zorluğuna dayanır. Shor (1994), bu iki problemi kuantum bilgisayarda verimli biçimde çözen bir algoritma vermiştir. Yeterli büyüklükte bir kuantum bilgisayar henüz yoktur; ancak bugün kaydedilen şifreli trafik ileride çözülebileceği için geçişin şimdiden yapılması gerekmektedir. Bu amaçla ABD Ulusal Standartlar ve Teknoloji Enstitüsü (NIST), Ağustos 2024'te ML-KEM anahtar kapsülleme standardını yayımlamıştır (NIST, 2024). ML-KEM, Kyber algoritmasından türetilmiştir (Bos ve ark., 2018) ve güvenliği modül üzerinde hatalarla öğrenme problemine dayanır.

ML-KEM'in bütün hesapları, katsayıları 3329'a göre kalan olarak tutulan ve X²⁵⁶ = −1 kuralıyla indirgenen 256 katsayılı polinomlar üzerinde yapılır. Bu polinomların çarpımı, yöntemin en sık tekrarlanan işlemidir. Standart bu çarpımı Sayı Teorik Dönüşüm (NTT) ile yapar ve açık anahtarı doğrudan dönüşmüş biçimde saklar.

Bu projenin çıkış noktası ise ilkokuldan bilinen bir gözlemdir. 23 sayısı 2·10 + 3 olarak yazılırsa karesi (2x + 3)² = 4x² + 12x + 9 polinomunun x = 10'daki değeridir; katsayılara sağdan sola elde uygulanınca 529 bulunur. Buradan şu soru doğmuştur: *Taban ne kadar büyük seçilirse hiç elde gerekmez ve katsayılar sayının içinden doğrudan okunur?* İki basamaklı sayıların karesinde en büyük katsayı 2·9·9 = 162 olduğundan cevap 163'tür. Bu sorunun genel hâli, polinom çarpımını tek bir büyük tamsayı çarpımına indirgeyen ve Kronecker'e (1882) dayanan **Kronecker ikamesidir**: x yerine yeterince büyük bir sayı (bilgisayarda 2^ℓ) konur, iki tamsayı çarpılır ve sonuç ℓ bitlik dilimlere ayrılarak katsayılar geri okunur. Gözlemimizin bu yöntemin özel bir hâli olduğu, literatür taraması sırasında öğrenilmiştir.

Kronecker ikamesi hızlı polinom çarpımı alanında uzun süredir incelenmektedir (Harvey, 2009). Kuantum sonrası kriptografide Albrecht ve ark. (2019), Kyber'ı akıllı kartlardaki RSA büyük tamsayı çarpıcısı üzerinde çalıştırmak için bu yöntemi kullanmış ve katsayıların karışmaması için gereken genişliği belirlemiştir; Bos ve ark. (2022) aynı donanım hedefi için daha gelişmiş varyantlar önermiştir. Dolayısıyla işaretli (merkezlenmiş) Kronecker ikamesi ve en kötü durum sınırı literatürde bilinmektedir; bu proje yeni bir şifreleme algoritması ya da yeni bir çarpma yöntemi önermemektedir.

Projenin literatüre göre konumu şudur: (i) FIPS 203'ün kesinleşmiş parametreleri için gereken genişlik, en küçük olduğunu gösteren açık bir örnekle birlikte ispatlanmış; (ii) en kötü durum sınırı ile ML-KEM'in gerçek katsayı dağılımlarında görülen tipik durum arasındaki fark bir olasılık modeliyle hesaplanıp deneyle sınanmış; (iii) bu farkın "denemelerde yetiyor" diyerek daha dar genişlik seçmeyi neden sakıncalı kıldığı gösterilmiş; (iv) hızlanmanın hangi adımdan geldiği ve neden bütüne yansımadığı ayrıştırılmıştır. ML-KEM'de çarpanlardan biri her zaman küçük katsayılıdır (gizli vektörün katsayıları −3 ile +3 arasındadır); çalışma bu özellikten yararlanmaktadır.

## 3. Yöntem

### 3.1. Matematiksel Çerçeve

n = 256, q = 3329 alınmıştır. Katsayılar merkezlenmiş biçimde, yani {−1664, …, 1664} aralığında tutulur; A = (q − 1)/2 = 1664'tür. Küçük polinomun katsayıları s_j ∈ [−η, η] aralığındadır (ML-KEM-512'de η = 3, ML-KEM-768 ve ML-KEM-1024'te η = 2). İki polinomun indirgenmemiş çarpımının katsayıları c_k = Σ_{i+j=k} a_i·s_j, X²⁵⁶ = −1 kuralıyla indirgenmiş katsayılar ise d_k = c_k − c_{k+n} biçimindedir.

Kronecker ikamesinde B = 2^ℓ seçilir ve P_a = Σ a_i·B^i, P_s = Σ s_j·B^j tamsayıları oluşturulur. Polinomda x yerine sayı koymak çarpma ve toplamayı koruduğundan P_a·P_s = Σ c_k·B^k olur. Geriye tek soru kalır: c_k'ler bu tamsayıdan tek türlü geri okunabilir mi?

**Lemma 1 (dengeli gösterimin tekliği).** Her rakamı D_ℓ = {−2^(ℓ−1), …, 2^(ℓ−1) − 1} kümesinden olan C = Σ d_k·B^k gösterimi tektir ve rakamlar şu adımla sırayla bulunur: C'nin alt ℓ biti alınır; değer 2^(ℓ−1) veya daha büyükse 2^ℓ çıkarılır; bulunan rakam C'den çıkarılıp sonuç 2^ℓ'ye bölünür. İspat, iki farklı gösterimin ilk ayrıldığı basamakta farkın B'ye bölünmesi gerektiği, oysa farkın mutlak değerinin B'den küçük olduğu çelişkisine dayanır. Bu adım, 19² = (2x − 1)² örneğindeki "ödünç alma" işleminin kendisidir.

**Teorem 1 (gereken genişlik).** |a_i| ≤ A ve |s_j| ≤ η ise her katsayı için |c_k| ≤ n·A·η olur; çünkü bir katsayıya en çok n terim katkı verir. n·A·η < 2^(ℓ−1) ise bütün katsayılar D_ℓ içindedir ve Lemma 1 ile tam olarak geri okunur. Bu koşulu sağlayan en küçük genişlik

**ℓ_min = bitlen(n·A·η) + 1**

olur. η = 3 için n·A·η = 256·1664·3 = 1.277.952 ve ℓ_min = 22; η = 2 için 851.968 ve ℓ_min = 21'dir.

**Önerme 1 (sınır en küçüktür).** Bütün a_i = 1664 ve bütün s_j = η seçilirse c_{n−1} = n·A·η olur. Genişlik bir bit azaltıldığında bu değer D_ℓ'nin dışında kalır ve açma kesinlikle yanlış sonuç verir. Daha genel olarak a_i'lerin işareti s'nin işaretlerine uydurulursa c_{n−1} = 1664·‖s‖₁ elde edilir; yani dar genişlikte hatanın oluşması gizli vektöre bağlıdır (H4'ün dayanağı).

**Önerme 2 (indirgemenin tamsayıda yapılması).** x = 2^ℓ için X^n + 1 ifadesi M = 2^(nℓ) + 1 sayısına karşılık gelir. Çarpımın M'ye göre kalanı alınırsa doğrudan indirgenmiş d_k katsayıları elde edilir; her d_k tam n terim içerdiğinden gereken genişlik değişmez, açılacak dilim sayısı ise 511'den 256'ya iner.

**Sonuç 1 (toplamın açılmadan yapılması).** ML-KEM'de çarpımlar k terimli toplamlar hâlinde gelir (k = 2, 3, 4). Terimler tamsayı olarak toplanıp bir kez açılırsa sınır k·n·A·η olur ve üç parametre setinde de ℓ_min = 23 çıkar; bayt sınırına denk gelen 24 bit üçüne de yeter.

**Tablo 1.** Gereken en küçük genişlikler

| Durum | En büyük katsayı | ℓ_min | 256 katsayının toplam boyutu |
|---|---:|:---:|---:|
| Yalın paketleme (iki çarpan da 0…3328) | 256·3328² = 2.835.349.504 | 32 | 8192 bit |
| Merkezlenmiş, η = 3 (ML-KEM-512) | 1.277.952 | 22 | 5632 bit |
| Merkezlenmiş, η = 2 (ML-KEM-768/1024) | 851.968 | 21 | 5376 bit |
| Merkezlenmiş, toplam açılmadan (üç set) | 2.555.904 – 3.407.872 | 23 | 5888 bit |

Karşılaştırmanın adil olması için bir not gerekir: 32 bitlik satır, küçük çarpanı da 0…3328 aralığında tutan en yalın uygulamadır. Yalnızca küçük çarpan η kadar kaydırılıp negatif olmayan hâle getirilirse en büyük katsayı 256·3328·6 = 5.111.808 olur ve 23 bit yeter. Yani 32 → 22 bitlik kazancın büyük kısmı küçük çarpanın küçük tutulmasından, son bir biti ise büyük çarpanın merkezlenmesinden gelir.

### 3.2. Rastgele Girdiler İçin Olasılık Modeli

Teorem 1, bütün katsayıların aynı anda en büyük değerde ve aynı işaretli olduğu en kötü durumu ele alır. ML-KEM'de ise büyük polinomun katsayıları düzgün dağılır (varyansı (q² − 1)/12 = 923.520), küçük polinomunkiler merkezli binom dağılımından gelir (varyansı η/2). Bir çarpım katsayısı, T adet bağımsız terimin toplamı olduğundan Merkezi Limit Teoremi ile yaklaşık normal dağılır: σ² = T·923.520·η/2. Tek bir dilimin D_ℓ dışına çıkma olasılığı p_k ≈ 2Φ(−2^(ℓ−1)/σ_k), çarpımın bozulma olasılığı ise 1 − Π(1 − p_k) olarak modellenmiştir. Modelin iki yaklaşıklığı baştan bilinmektedir: dilimler aynı katsayıları paylaştığı için tam bağımsız değildir ve terimler sınırlı olduğu için gerçek dağılımın kuyruğu normalden incedir.

### 3.3. Yazılım

ML-KEM'in üç parametre seti, standarttaki algoritma numaraları izlenerek Python ile sıfırdan yazılmıştır; özet fonksiyonları için yalnızca Python'un standart kütüphanesi kullanılmıştır. Kronecker ikamesi beş seçimle tanımlanan bir yapı olarak kodlanmıştır: dilim genişliği, katsayıların işaretli olup olmadığı, paketleme ve açmanın döngüyle mi bayt dönüşümüyle mi yapıldığı, indirgemenin tamsayıda yapılıp yapılmadığı (Önerme 2) ve toplamın açılmadan yapılıp yapılmadığı (Sonuç 1). Bu seçimlerden sekiz varyant oluşturulmuştur (Tablo 3'te adlarıyla verilmiştir).

Standart, açık anahtarı ve A matrisini NTT biçiminde ürettiği için Kronecker yolu bunları önce ters dönüşümle katsayı biçimine çevirir, çarpar ve sonucu geri çevirir. Böylece çıktı standartla bayt bayt aynı kalır. Bu ek dönüşümler ayrıca ölçülmüştür.

Doğruluk üç bağımsız kaynağa karşı sınanmıştır: NIST'in resmî test vektörleri, katsayıları tek tek çarpıp toplayan okul yöntemi ve Teorem 1'in sayısal değerleri. Testlerin hata yakalama gücünü görmek için koda bilerek 12 ayrı hata yerleştiren bir araç yazılmıştır. Depoda toplam 1884 otomatik test bulunmaktadır.

### 3.4. Deney Düzeni

**Tablo 2.** Deneyler ve ölçüm ortamları

| Deney | İçerik | Ortam |
|---|---|---|
| E1 | Resmî test vektörleri (NTT + 8 varyant); 10.000 rastgele çarpım × 8 varyant; en kötü durum girdileri | Raspberry Pi 5, Python 3.13 |
| E2 | En kötü durum girdileri (60 çalıştırma); 10 seri × 20.000 rastgele deneme, ℓ = 14 … ℓ_min | Intel Core i3-14100, Python 3.11 |
| E3 | Büyük tamsayı çarpımı (15.000 tekrar), tek polinom çarpımı (1000), adım adım süre dağılımı, ML-KEM'in tamamı (100) | Intel Core i3-14100, Python 3.11 |
| E3-ek | Tek polinom çarpımı ve ML-KEM'in tamamı (500 tekrar), Python bellek tahsisi | x86-64 bilgisayar, Python 3.14 |
| E4 | ℓ = 18 … 22 için 1500 gizli vektör; 150 ML-KEM-512 anahtarı | Intel Core i3-14100, Python 3.11 |
| E5 | 16.384 baytlık içeriğin şifresiz ve PQC-Drop akışıyla aktarımı | Tek bilgisayar, yerel döngü arayüzü |
| E6 | Çarpımın iki biçiminin çevrim sayısı (100 çalıştırma) | ESP32-D0WD-V3, 80 MHz, C++ |

**E2.** Seriler ML-KEM'de gerçekten oluşan durumlardır: tek çarpım (η = 3 ve η = 2) ve k = 2, 3, 4 terimli toplamlar; her biri hem tam açma (511 dilim) hem tamsayıda indirgeme (256 dilim) ile. Her denemede dilimlerin kesin değerleri 40 bitlik genişlikle hesaplanmış ve o deneme için gereken en küçük taban kaydedilmiştir; böylece hata oranı yalnızca tam sayı ℓ değerlerinde değil, sürekli bir eksende de ölçülmüştür. Oranlar için %95 Wilson güven aralığı kullanılmıştır. Rastgele sayı tohumu sabittir.

**E3.** Süreler `perf_counter_ns` ile, ısınma turundan sonra ve çöp toplayıcı kapatılarak ölçülmüş; medyan ve çeyrekler arası aralık (ÇAA) raporlanmıştır.

**E4.** Önerme 1'deki girdi (her katsayısı ±1664 olan ve işaretleri gizli vektöre uydurulmuş polinom) kullanılarak çarpımın bozulup bozulmadığı ‖s‖₁ ile karşılaştırılmıştır. 1500 vektörün 700'ü ML-KEM'in gerçek dağılımından alınmış, 800'ünün normu eşik çevresini taramak için yapay olarak 156–673 aralığına ayarlanmıştır. 150 anahtarın 75'i gerçek anahtar üretiminden gelmiş, 75'inin gizli vektörü deney amacıyla büyütülmüştür. Girdi, standardın 10 bitlik şifreli metin sıkıştırmasından geçebilen uç değerlerle kurulmuştur. Bu deneyde kapsül açma işleminin tamamı değil, içindeki çarpım ölçülmüştür.

**E6.** ESP32 üzerinde büyük tamsayı paketlemesi uygulanmamıştır. Ölçülen, aynı çarpımın iki C++ biçimidir: sonuçları 511 elemanlı bir ara dizide biriktiren okul yöntemi ve her sonuç katsayısını tek bir 32 bitlik toplayıcıda hesaplayan, ara dizi kullanmayan biçim. Teorem 1'e göre toplayıcının değeri 1.277.952'yi aşamayacağından 32 bit taşmaz. Bir rastgele girdi çifti üretilmiş, iki biçimin çıktıları karşılaştırılmış ve her biri 100 kez çalıştırılarak işlemcinin çevrim sayacı okunmuştur.

### 3.5. PQC-Drop Prototipi

PQC-Drop, aynı ağdaki iki cihaz arasında dosya aktaran bir araçtır. Alıcı ML-KEM-768 anahtar çifti üretip açık anahtarı (1184 bayt) gönderir; gönderici kapsülü (1088 bayt) yollar; iki taraf 32 baytlık ortak sırdan HKDF-SHA256 ile bir AES anahtarı türetir. Dosya 64 KB'lık parçalar hâlinde AES-256-GCM ile şifrelenir; her parça kendi doğrulama etiketiyle, aktarımın sonunda bütün dosya SHA-256 özetiyle denetlenir. Polinom çarpımları 24 bitlik, bayt hizalı ve tamsayıda indirgeme yapan Kronecker varyantıyla yapılır. ML-KEM ve Kronecker katmanı projenin kendi kodudur; AES-GCM ve HKDF için hazır `cryptography` kütüphanesi kullanılmıştır. Aracın komut satırı, masaüstü ve terminal arayüzleri ile aynı ağdaki cihazları bulan bir keşif servisi vardır.

### 3.6. Proje İş-Zaman Çizelgesi

| İşin tanımı | Ekim | Kasım | Aralık | Ocak |
|---|:---:|:---:|:---:|:---:|
| Literatür taraması | X | X | | |
| Teori: ispatlar ve olasılık modeli | X | X | | |
| ML-KEM uygulaması ve resmî testler | X | | | |
| Kronecker varyantları ve deneyler (E1–E4) | X | X | | |
| PQC-Drop prototipi, ağ ve ESP32 ölçümleri | X | X | X | |
| Proje raporunun yazımı | | X | X | X |

## 4. Bulgular

### 4.1. Doğruluk (H1)

Standardın yolu (NTT) ve sekiz Kronecker varyantının her biri, üç parametre setindeki 180 anahtar üretimi, kapsülleme ve kapsül açma vakasının tamamında resmî beklenen çıktıyı bayt bayt üretmiştir; 60 anahtar denetimi vakası da geçmiştir. 10.000 rastgele çarpımda sekiz varyantın hiçbiri okul yönteminden sapmamıştır (Tablo 3). Bütün katsayıların uç değerde olduğu en kötü durum girdileri de sekiz varyantta doğru sonuç vermiştir. Koda bilerek yerleştirilen 12 hatanın 12'si testlerce yakalanmıştır.

**Tablo 3.** 10.000 rastgele çarpımda hata sayısı

| Varyant | Genişlik | Hatalı / toplam |
|---|:---:|:---:|
| İşaretsiz, döngü | 32 | 0 / 10.000 |
| İşaretsiz, bayt | 32 | 0 / 10.000 |
| İşaretli, döngü | 22 | 0 / 10.000 |
| İşaretli, tamsayıda indirgeme | 22 | 0 / 10.000 |
| İşaretli, bayt | 24 | 0 / 10.000 |
| İşaretli, bayt, tamsayıda indirgeme | 24 | 0 / 10.000 |
| İşaretli, bayt, toplam açılmadan | 24 | 0 / 10.000 |
| İşaretli, bayt, indirgeme + toplam | 24 | 0 / 10.000 |

Sıfır hata, %95 güvenle hata oranının 10.000'de 3'ün altında olduğunu söyler; daha fazlasını söylemez. Rastgele girdilerde katsayılar 17–18 bit civarında kaldığından bu deney sınırın yakınına hiç gelmemektedir. Sınırın yeterli olduğunu gösteren şey ispat ve en kötü durum girdileridir; bu deney yöntemin gerçek dağılımlarda da sorunsuz çalıştığını gösterir. **H1 desteklenmiştir.**

### 4.2. Teori ile Deneyin Karşılaştırılması (H2)

**Sınırın en küçük olması.** On serinin her birinde en kötü durum girdileri ℓ_min genişliğinde doğru, bir bit dar genişlikte bozuk sonuç vermiştir (60 çalıştırmanın 60'ı beklendiği gibi). 200.000 rastgele denemenin hiçbirinde, gerçek açma sonucu ile Lemma 1'in ölçütü birbirinden ayrılmamıştır.

**Model ile ölçüm.** Tablo 4, hata oranının 0 ile 1 arasında ölçülebildiği noktaları göstermektedir. Sonuç iki bölgede farklıdır. Hatanın seyrek olduğu bölgede (oran 0,15'in altında) model sekiz noktanın sekizinde güven aralığının içindedir. Hatanın sık olduğu bölgede (oran 0,7'nin üstünde) ise model altı noktanın altısında aralığın dışında kalmış ve oranı 0,3 ile 1,6 puan arasında **fazla** tahmin etmiştir.

**Tablo 4.** Olasılık modelinin tahmini ile ölçülen hata oranı (seri başına 20.000 deneme)

| Seri | ℓ | Hatalı | Ölçülen oran | %95 güven aralığı | Model | Model aralıkta mı? |
|---|:---:|---:|:---:|:---:|:---:|:---:|
| Tek çarpım, η = 3, tam açma | 17 | 602 | 0,0301 | [0,0278; 0,0326] | 0,0306 | evet |
| Tek çarpım, η = 3, indirgemeli | 17 | 2434 | 0,1217 | [0,1172; 0,1263] | 0,1205 | evet |
| Tek çarpım, η = 2, tam açma | 17 | 23 | 0,00115 | [0,00077; 0,00173] | 0,00091 | evet |
| Tek çarpım, η = 2, indirgemeli | 17 | 99 | 0,00495 | [0,00407; 0,00602] | 0,00517 | evet |
| Toplam, k = 2, indirgemeli | 18 | 4 | 0,00020 | [0,00008; 0,00051] | 0,00022 | evet |
| Toplam, k = 3, indirgemeli | 18 | 6 | 0,00030 | [0,00014; 0,00065] | 0,00022 | evet |
| Toplam, k = 4, tam açma | 18 | 12 | 0,00060 | [0,00034; 0,00105] | 0,00091 | evet |
| Toplam, k = 4, indirgemeli | 18 | 110 | 0,00550 | [0,00457; 0,00662] | 0,00517 | evet |
| Tek çarpım, η = 2, tam açma | 16 | 19.360 | 0,9680 | [0,9655; 0,9704] | 0,9822 | hayır (+1,4 puan) |
| Toplam, k = 2, tam açma | 17 | 14.770 | 0,7385 | [0,7324; 0,7445] | 0,7546 | hayır (+1,6 puan) |
| Toplam, k = 2, indirgemeli | 17 | 19.232 | 0,9616 | [0,9589; 0,9642] | 0,9719 | hayır (+1,0 puan) |
| Toplam, k = 3, tam açma | 17 | 14.921 | 0,7461 | [0,7400; 0,7520] | 0,7546 | hayır (+0,9 puan) |
| Toplam, k = 3, indirgemeli | 17 | 19.366 | 0,9683 | [0,9658; 0,9706] | 0,9719 | hayır (+0,4 puan) |
| Toplam, k = 4, tam açma | 17 | 19.578 | 0,9789 | [0,9768; 0,9808] | 0,9822 | hayır (+0,3 puan) |

Sapmanın yönü her seferinde aynıdır ve modelin baştan bilinen yaklaşıklığıyla açıklanabilir: dilimler aynı katsayıları paylaştığı için birbirinden bağımsız değildir; bir dilim taştığında komşularının da taşması daha olasıdır. Bağımsızlık varsayımı bu yüzden "en az bir dilim taşar" olasılığını olduğundan büyük hesaplar. Hata seyrekken bu etki ölçüm belirsizliğinin altında kalmakta, hata sıklaştıkça görünür hâle gelmektedir.

Genişlik 19 bit ve üzerindeyken hiçbir seride 20.000 denemede hata görülmemiştir. Bu sonuç, modelin bu bölgedeki çok küçük tahminlerini (10⁻¹⁵'in altı) **doğrulamaz**; yalnızca hata oranının 1,9·10⁻⁴'ün altında olduğunu gösterir.

Sürekli eksende ölçülen eğriler modelle üst üste gelmiştir (Şekil 1, Şekil 2): hata olasılığının yarıya düştüğü taban, model ve ölçümde en fazla 0,01 bit farkla aynıdır (Tablo 5). k = 2, η = 3 ile k = 3, η = 2 serilerinin aynı eğriyi vermesi, modelin yalnızca k·η çarpımına bağlı olduğu öngörüsünü doğrulamıştır.

**Tablo 5.** Rastgele girdide gereken genişlik ile ispatın verdiği sınır

| Seri | Model medyanı (bit) | Ölçülen medyan | 20.000 denemede en büyük | ℓ_min | Fark |
|---|:---:|:---:|:---:|:---:|:---:|
| Tek çarpım, η = 3 | 16,62 | 16,61 | 17,49 | 22 | 4,5 bit |
| Tek çarpım, η = 2 | 16,32 | 16,32 | 17,20 | 21 | 3,8 bit |
| Toplam, k = 2 | 17,12 | 17,11 | 17,92 | 23 | 5,1 bit |
| Toplam, k = 3 | 17,12 | 17,12 | 17,98 | 23 | 5,0 bit |
| Toplam, k = 4 | 17,32 | 17,33 | 18,16 | 23 | 4,8 bit |

![Şekil 1](../experiments/02-teori-deney/grafik_e24.png)
*Şekil 1. Tam açma serilerinde model eğrisi ve ölçülen hata oranları (%95 güven aralığıyla).*

![Şekil 2](../experiments/02-teori-deney/grafik_e24_neg.png)
*Şekil 2. Tamsayıda indirgeme yapılan serilerde aynı karşılaştırma.*

![Şekil 3](../experiments/02-teori-deney/grafik_fark.png)
*Şekil 3. Rastgele girdide gereken genişliğin dağılımı ve ispatlanan sınır.*

Rastgele girdiler 17–18 bitte kalırken ispatın istediği genişlik 21–23 bittir (Şekil 3). Bu 4–5 bitlik aralık, 4.4'teki deneyin konusudur. **H2'nin ispatla ilgili bölümü tümüyle, modelle ilgili bölümü kısmen desteklenmiştir:** model geçiş bölgesinin yerini 0,01 bit doğrulukla ve seyrek hata oranlarını güven aralığı içinde vermekte, sık hata oranlarını ise en çok 1,6 puan fazla tahmin etmektedir.

### 4.3. Performans (H3)

**Büyük tamsayı çarpımı.** Çarpılan sayı 8192 bitten 5632 bite indiğinde süre 20,35 µs'den 9,94 µs'ye düşmüştür (Tablo 6). Beklenen değer yaklaşık 1,8 kattı; ölçülen 2,05 kattır. Farkın nedeni ayrıca ölçülmemiştir; olası açıklama, Python'un bu boyutlarda iki farklı çarpma algoritması arasında geçiş yapmasıdır.

**Tablo 6.** Yalnızca büyük tamsayı çarpımı (15.000 tekrar)

| Paketleme | Sayının boyutu (bit) | Medyan (µs) | ÇAA (µs) | Hızlanma |
|---|:---:|:---:|:---:|:---:|
| 32 bit | 8192 | 20,35 | 0,86 | 1,00× |
| 24 bit | 6144 | 11,68 | 0,05 | 1,74× |
| 22 bit | 5632 | 9,94 | 0,18 | 2,05× |
| 21 bit | 5376 | 9,20 | 0,04 | 2,21× |

**Tek polinom çarpımı.** Paketleme ve açma da hesaba katıldığında tablo değişmektedir (Tablo 7). Bayt dönüşümü kullanan Kronecker varyantları (106–145 µs) Python ile yazılmış NTT'den (284 µs) hızlıdır; döngüyle açan varyantlar değildir. Bu deneyin beklenmedik bulgusu, **en hızlı varyantın 32 bitlik işaretsiz varyant olmasıdır** (106 µs; 24 bitlik işaretli varyant 130 µs). Adım adım ölçüm bunun nedenini göstermektedir (Tablo 8): dar paketlemenin çarpımda kazandırdığı yaklaşık 10 µs, toplam 80–90 µs tutan paketleme ve açma içinde kaybolmaktadır. Döngüyle işaretli açma sürenin %75'ini alırken bayt dönüşümüyle açma bu adımı 212 µs'den 55 µs'ye indirmiştir. Farklı bir bilgisayarda 500 tekrarla yapılan ek ölçüm aynı sıralamayı vermiştir (32 bit işaretsiz 2,46 kat, 24 bit işaretli 2,22 kat NTT'den hızlı).

Bu karşılaştırma dikkatle okunmalıdır: NTT burada satır satır Python ile çalışırken büyük tamsayı çarpımı Python'un C ile yazılmış çekirdeğinde yapılmaktadır. "Kronecker NTT'den 2,2 kat hızlıdır" cümlesi yalnızca bu ortam için geçerlidir; iki yöntemin C ile yazıldığı bir karşılaştırma yapılmamıştır.

**Tablo 7.** Tek polinom çarpımı (1000 tekrar, medyan)

| Yöntem | Medyan (µs) | ÇAA (µs) |
|---|---:|---:|
| Okul yöntemi | 3290,95 | 322,47 |
| NTT (iki ileri dönüşüm + çarpım + ters dönüşüm) | 284,28 | 11,53 |
| NTT (yalnızca dönüşmüş biçimde çarpım) | 21,49 | 1,00 |
| Kronecker, 32 bit işaretsiz, döngü | 207,79 | 1,61 |
| Kronecker, 32 bit işaretsiz, bayt | 106,10 | 2,34 |
| Kronecker, 22 bit işaretli, döngü | 314,83 | 6,49 |
| Kronecker, 22 bit işaretli, tamsayıda indirgeme | 196,45 | 1,64 |
| Kronecker, 24 bit işaretli, bayt | 130,18 | 2,32 |
| Kronecker, 24 bit, bayt, tamsayıda indirgeme | 145,17 | 1,53 |
| Kronecker, 24 bit, bayt, toplam açılmadan | 122,85 | 2,24 |

**Tablo 8.** Kronecker çarpımında sürenin adımlara dağılımı (µs)

| Varyant | Paketleme | Tamsayı çarpımı | Açma ve indirgeme | Toplam |
|---|---:|---:|---:|---:|
| 32 bit işaretsiz, döngü | 80,8 | 21,5 | 102,6 | 204,8 |
| 32 bit işaretsiz, bayt | 25,4 | 20,6 | 51,8 | 97,7 |
| 22 bit işaretli, döngü | 60,3 | 10,3 | 212,4 | 283,0 |
| 24 bit işaretli, bayt | 28,8 | 12,5 | 55,0 | 96,3 |
| 22 bit işaretli, tamsayıda indirgeme | 61,6 | 46,1 | 48,9 | 156,6 |
| 24 bit, bayt, tamsayıda indirgeme | 27,6 | 54,6 | 27,4 | 109,6 |

Tablo 8'in son iki satırı ikinci bir darboğazı göstermektedir: tamsayıda indirgeme açılacak dilim sayısını yarıya indirmekte, fakat kalan alma işlemi çarpım adımını 12 µs'den 55 µs'ye çıkarmaktadır.

**ML-KEM'in tamamı.** Standartla aynı çıktıyı üretmek için gereken ters dönüşümler (ML-KEM-768 kapsüllemesinde 12 adet) Kronecker yolunu standardın gerisinde bırakmıştır (Tablo 9). Standart yol anahtar üretiminde %39–63, kapsüllemede %20–43, kapsül açmada %22–45 daha hızlıdır ve fark parametre seti büyüdükçe artmaktadır. A matrisinin katsayı biçimi bellekte hazır tutulduğunda fark küçülmekte ama kapanmamaktadır: üç işlemin toplamında Kronecker yolu standardın 0,90 / 0,85 / 0,82 katı hızdadır (Tablo 10). Aynı ek ölçümde 24 bitlik Kronecker çarpımı, Python'un izlediği en yüksek bellek tahsisini NTT'ye göre %56,9 artırmıştır; yani paketlenen sayının %31 küçülmesi programın bellek kullanımının azalması anlamına gelmemektedir.

**Tablo 9.** ML-KEM işlemleri (100 tekrar, medyan, µs)

| Parametre seti | Çarpım yolu | Anahtar üretimi | Kapsülleme | Kapsül açma |
|---|---|---:|---:|---:|
| ML-KEM-512 | NTT (standart) | 2692 | 4289 | 4698 |
| | Kronecker, 24 bit | 3736 | 5167 | 5728 |
| ML-KEM-768 | NTT (standart) | 4138 | 6227 | 6532 |
| | Kronecker, 24 bit | 6153 | 8242 | 8903 |
| ML-KEM-1024 | NTT (standart) | 5516 | 8156 | 8688 |
| | Kronecker, 24 bit | 8987 | 11698 | 12579 |

**Tablo 10.** Üç işlemin toplamı, A matrisi hazır tutulduğunda (500 tekrar, medyan)

| Parametre seti | Standart (ms) | Kronecker (ms) | Kronecker / standart hızı |
|---|---:|---:|:---:|
| ML-KEM-512 | 14,64 | 16,34 | 0,90× |
| ML-KEM-768 | 21,25 | 24,91 | 0,85× |
| ML-KEM-1024 | 29,40 | 35,87 | 0,82× |

![Şekil 4](../experiments/04-performans/grafik_e33.png)
*Şekil 4. Kronecker varyantlarında sürenin adımlara dağılımı.*

![Şekil 5](../experiments/04-performans/grafik_e34.png)
*Şekil 5. ML-KEM işlemlerinde standart yol ile Kronecker yolunun süreleri.*

**H3 desteklenmiştir:** çarpım adımı beklenenden biraz fazla hızlanmış, kazanç bütüne yansımamıştır. "Kronecker ikamesi ML-KEM'i hızlandırır" iddiası bu verilerle desteklenmemektedir.

### 4.4. Sınırın Altında Anahtara Bağlı Davranış (H4)

4.2'de rastgele girdilerin 18 bitte bile hata vermediği görülmüştü. Bu bölüm "öyleyse 22 yerine 18–20 bit kullanılsın" seçiminin sonucunu inceler. Önerme 1'e göre özel seçilmiş girdide hata koşulu 1664·‖s‖₁ ≥ 2^(ℓ−1) olur (Tablo 11).

**Tablo 11.** Hata için gereken en küçük ‖s‖₁ ve ölçülen sonuç

| ℓ | Eşik | Gerçek dağılımdan 700 vektör (en büyük norm 282) | Yapay normlu 800 vektör |
|:---:|:---:|---|---|
| 18 | 79 | hepsi bozuldu | hepsi bozuldu |
| 19 | 158 | hepsi bozuldu | eşiğin üstündekiler bozuldu |
| 20 | 316 | hiçbiri bozulmadı | eşiğin üstündekiler bozuldu |
| 21 | 631 | hiçbiri bozulmadı | eşiğin üstündekiler bozuldu |
| 22 | 1261 (ulaşılamaz: en fazla 768) | hiçbiri bozulmadı | hiçbiri bozulmadı |

1500 vektör ve beş genişlik için yapılan 7500 karşılaştırmanın hiçbirinde ölçülen sonuç teorik eşikten ayrılmamıştır; bozulma, normun eşiğe ulaştığı noktada başlayan bir basamak biçimindedir (Şekil 6). 150 ML-KEM-512 anahtarında, sıkıştırmadan geçebilen girdiyle 20 bit için aynı eşik (316) yine sıfır uyumsuzlukla gözlenmiştir: 75 gerçek anahtarın hiçbiri bozulmamış (en büyük norm 270), yapay olarak büyütülen anahtarlardan eşiği aşanların tamamı bozulmuştur.

![Şekil 6](../experiments/03-guvenlik/grafik_e41.png)
*Şekil 6. Beş genişlik için ‖s‖₁'e karşı çarpımın bozulması ve teorik eşikler.*

Bu sonucun ölçüsü dikkatle verilmelidir. Gösterilen şudur: rastgele denemelerde sorunsuz görünen 18–19 bit, uygun seçilmiş bir girdiyle her gerçek anahtarda yanlış sonuç verir; 20 bit yalnızca normu ender görülecek kadar büyük anahtarlarda yanlış sonuç verir ve bu, anahtarın kendisine bağlıdır; 22 bitte hata imkânsızdır. Gösterilmeyen ise şudur: bu davranışın gerçek bir saldırıya dönüştüğü. Deneydeki girdi gizli vektörün işaretleri bilinerek kurulmuştur. Ayrıca standart, kapsül açma sırasında mesajı yeniden şifreleyip gelen şifreli metinle karşılaştırır; elle kurulmuş bir şifreli metin bu denetimi taşma olsa da olmasa da geçemez ve sonuç her iki durumda da sahte bir anahtardır. Bilginin dışarı sızması için zamanlama gibi ek bir yan kanal gerekir ve bu ölçülmemiştir. **H4, çarpım düzeyinde desteklenmiştir;** anahtarın ele geçirilebildiği yönünde bir bulgu yoktur.

### 4.5. PQC-Drop ve Ağ Üzerindeki Görünüm (E5)

PQC-Drop ile dosya aktarımı, otomatik testlerde aynı bilgisayardaki iki uç arasında gönderilen ve alınan dosyanın bayt bayt eşleşmesiyle doğrulanmış; masaüstü ve terminal arayüzleri bir dizüstü bilgisayar ile Raspberry Pi 5 arasında kablolu ve kablosuz ağda denenmiştir.

Ağ deneyinde 16.384 baytlık aynı metin iki biçimde gönderilmiş ve soketten geçen baytlar kaydedilmiştir (Tablo 12). Şifresiz gönderimde aranan sözcük doğrudan bulunmuş, PQC-Drop akışında bulunmamıştır. Kuantum sonrası anahtar değişiminin bedeli boyuttadır: içerik dışındaki 2300 baytın 2272'si açık anahtar ve kapsüldür.

**Tablo 12.** Aynı 16.384 baytlık içerik için soketten geçen veri

| Ölçüt | Şifresiz HTTP | PQC-Drop akışı |
|---|:---:|:---:|
| Toplam bayt | 16.493 | 18.684 |
| İçerik dışındaki bayt | 109 | 2300 |
| Açık metin araması | bulundu | bulunamadı |
| Bayt entropisi (en çok 8) | 4,130 | 7,992 |

Entropi değeri bir güvenlik kanıtı olarak sunulmamaktadır. 18.684 rastgele baytın beklenen entropisi yaklaşık 7,99'dur; ölçülen 7,992 bununla uyumludur ve verinin rastgele veriden ayırt edilemeyecek biçimde göründüğünü söyler. Sıkıştırılmış fakat şifrelenmemiş bir dosya da benzer değer verir. Deney kaydında bir de "klasik şifreli bağlantı" satırı (16.435 bayt) yer almaktadır; bu satır gerçek bir TLS oturumunun kaydı olmayıp aynı içeriğin rastgele bir anahtarla şifrelenmesiyle üretildiği için bu rapora ölçüm olarak alınmamıştır. Benzer biçimde, depodaki paket kayıt dosyalarının ağ başlıkları deney betiği tarafından üretilmiştir; bu dosyalar bağımsız bir ağ dinleme aracının yakaladığı paketler değildir.

### 4.6. ESP32 Üzerinde Çarpımın İki Biçimi (E6)

**Tablo 13.** ESP32-D0WD-V3, 80 MHz, n = 256, aynı girdiyle 100 çalıştırmanın ortalaması

| Biçim | Ortalama çevrim | Süre (ms) | Ara dizi |
|---|---:|---:|---|
| Okul yöntemi (511 elemanlı ara dizi) | 677.956 | 8,47 | 2044 bayt |
| Tek toplayıcıda biriktirme (ara dizisiz) | 841.234 | 10,51 | yok |

İki biçim 256 katsayının tamamında aynı sonucu vermiştir. Ara dizi kullanmayan biçim yaklaşık %24 daha fazla çevrim harcamıştır (0,81 kat hız); karşılığında yığında 2044 baytlık diziye gerek kalmamaktadır. Bu ölçüm, Teorem 1'deki sınırın 32 bitlik bir toplayıcıda taşma olmayacağını güvenceye aldığı küçük bir işlemcide çarpımın doğru yapılabildiğini göstermektedir. Büyük tamsayı paketlemesi ESP32'de uygulanmadığı için bu sonuç, Kronecker ikamesinin mikrodenetleyicideki hızı hakkında bir şey söylemez ve 4.3'teki ML-KEM oranlarıyla (0,82–0,90) aynı karşılaştırma değildir. Doğruluk tek bir girdi çiftiyle denetlenmiş; enerji tüketimi ve bellek kullanımı ölçülmemiştir.

## 5. Sonuç ve Tartışma

**Gereken genişlik ispatlandı ve en küçüktür.** Merkezlenmiş Kronecker ikamesinde katsayıların karışmadan geri okunması için gereken genişlik ℓ_min = bitlen(n·A·η) + 1'dir: ML-KEM-512 için 22, diğer setler için 21, toplam açılmadan yapıldığında üç set için 23 bit. Bir bit eksiğinde yanlış sonuç veren girdi açıkça verilmiş, 60 en kötü durum çalıştırması ve 200.000 rastgele deneme ispatla uyumlu çıkmıştır. Sınırın kendisi literatürde bilinen türden bir sınırdır (Albrecht ve ark., 2019); bu çalışmanın yaptığı, onu kesinleşmiş standart parametreleri için en küçük olduğunu gösteren örnekle birlikte vermek ve deneyle sınamaktır.

**Tipik durum ile en kötü durum arasında 4–5 bit vardır ve bu fark hesaplanabilir.** Olasılık modeli geçiş bölgesinin yerini doğru vermiş ve hatanın seyrek olduğu sekiz noktanın sekizinde güven aralığının içinde kalmıştır. Hatanın sık olduğu altı noktada ise oranı 0,3–1,6 puan fazla tahmin etmiştir; bu sapma, dilimlerin bağımsız sayılmasından kaynaklanan ve baştan bilinen yaklaşıklıkla aynı yöndedir. Modelin çok küçük olasılıklardaki tahminleri bu örneklemle sınanamamıştır; 20.000 denemede sıfır hata yalnızca bir üst sınır verir.

**Hız kazancı çarpım adımındadır, bütünde değildir.** Sayının küçülmesi büyük tamsayı çarpımını 2,05 kat hızlandırmıştır. Ancak Python ortamında tek polinom çarpımının süresini paketleme ve açma belirlemekte, bu yüzden 32 bitlik yalın varyant 24 bitlik merkezlenmiş varyanttan hızlı çıkmaktadır. ML-KEM'in tamamında ise standardın verileri dönüşmüş biçimde saklaması, Kronecker yoluna her işlemde ek dönüşüm yükü getirmekte ve standart yol %12–63 önde kalmaktadır. Bu, başlangıçtaki beklentimizin tersine bir sonuçtur ve yöntemin anlamlı olabileceği yeri daraltır: NTT'yi hızlandıran donanımı olmayan, buna karşılık RSA için üretilmiş büyük tamsayı çarpıcısı bulunan cihazlar (Albrecht ve ark., 2019; Bos ve ark., 2022). Bu çalışmada böyle bir cihazda ölçüm yapılmamıştır.

**Genişlik denemeyle değil ispatla seçilmelidir.** Rastgele denemeler 18 bitin yettiği izlenimini verir; oysa uygun bir girdi, 18–19 bitte her gerçek anahtarda, 20 bitte normu büyük anahtarlarda çarpımı bozar. Bir kriptografik uygulamada sonucun doğruluğunun gizli anahtara bağlı olması, sömürüldüğü gösterilmemiş olsa bile istenmeyen bir özelliktir; ispatlanan sınır bu bağımlılığı tümüyle ortadan kaldırır. Çıkış noktamızdaki "taban en az 163 olmalı" gözlemi ile bu sonuç aynı düşüncenin iki ucudur.

**Sınırlılıklar.**
1. Bütün süre ölçümleri Python'a aittir; C ile yazılmış uygulamalara genellenemez. Performans deneyleri iki ayrı bilgisayarda yapılmış, aynı deney iki makinede tekrarlanmamıştır.
2. 32 bitlik karşılaştırma tabanı en yalın uygulamadır; küçük çarpanı kaydıran işaretsiz bir uygulama 23 bitle çalışır (3.1). Merkezlemenin buna göre kazancı bir bittir.
3. Uygulama sabit zamanlı değildir; işlem süresi verilere bağlı olabilir (bkz. Bernstein ve ark., 2024). Bunun bilgi sızdırıp sızdırmadığı incelenmemiştir.
4. H4 deneyinde eşik çevresi yapay vektörlerle taranmış, girdi gizli vektör bilinerek kurulmuş ve kapsül açmanın tamamı çalıştırılmamıştır.
5. Ağ deneyi tek bilgisayarda, yerel döngü arayüzünde yapılmıştır; gerçek bir TLS oturumuyla karşılaştırma ve bağımsız paket yakalama yoktur.
6. ESP32 ölçümü tek girdiyle ve yalnızca çarpım düzeyindedir; büyük tamsayı paketlemesini içermez.
7. PQC-Drop bir araştırma prototipidir. Açık anahtarın kime ait olduğu doğrulanmadığından araya giren etkin bir saldırgana karşı koruma sağlamaz; alıcı gelen dosyayı kullanıcıya sormadan kabul eder ve gelen dosya adı ile boyut bilgisine yönelik denetimler yeterli değildir. Bağımsız bir güvenlik incelemesinden geçmemiştir.

**Yapay zekâ kullanımı.** Çalışmada kod yazımı, grafiklerin hazırlanması ve metnin dil düzenlemesinde üretken yapay zekâ araçlarından destek alınmıştır. Deneyler proje ekibi tarafından çalıştırılmış, sonuçlar ham verilerle karşılaştırılarak denetlenmiştir.

## 6. Öneriler

1. Büyük tamsayı paketlemesi, RSA çarpıcısı bulunan bir mikrodenetleyicide C ile uygulanmalı; süre, enerji ve bellek birlikte ölçülmelidir. Yöntemin asıl sınanacağı ortam budur.
2. Kronecker tabanlı uygulamalarda genişlik, rastgele testlerde yeterli görünen değere göre değil Teorem 1'deki sınıra göre seçilmelidir.
3. Olasılık modelinin küçük olasılıklardaki doğruluğu, normal yaklaşım yerine kesin bir üst sınır (örneğin Chernoff sınırı) hesaplanarak ve daha büyük örneklemle sınanmalıdır.
4. Sınırın altındaki genişliklerde kapsül açma işleminin tamamı çalıştırılarak hatanın dışarıdan gözlenip gözlenemediği (anahtar uyuşmazlığı, süre farkı) ölçülmelidir.
5. Tamsayıda indirgeme adımındaki kalan alma işlemi, 2^(nℓ) ≡ −1 özelliğinden yararlanan kaydırma ve çıkarma işlemleriyle değiştirilerek Tablo 8'deki ikinci darboğaz giderilebilir.
6. PQC-Drop'a karşı tarafın doğrulanması (iki ekranda karşılaştırılan kısa bir doğrulama kodu ya da ML-DSA imzası), alıcı onayı ve gelen dosya adı denetimi eklenmeli; ağ deneyi iki ayrı bilgisayar arasında, gerçek bir TLS oturumuyla ve bağımsız paket yakalama aracıyla yinelenmelidir.

## Kaynaklar

Albrecht, M. R., Hanser, C., Höller, A., Pöppelmann, T., Virdia, F. ve Wallner, A. (2019). Implementing RLWE-based schemes using an RSA co-processor. *IACR Transactions on Cryptographic Hardware and Embedded Systems, 2019*(1), 169–208.

Bernstein, D. J., Bhargavan, K., Bhasin, S., Chattopadhyay, A., Chia, T. K., Kannwischer, M. J., Kiefer, F., Paiva, T., Ravi, P. ve Tamvada, G. (2024). *KyberSlash: Exploiting secret-dependent division timings in Kyber implementations* (Rapor No. 2024/1049). IACR Cryptology ePrint Archive.

Bos, J., Ducas, L., Kiltz, E., Lepoint, T., Lyubashevsky, V., Schanck, J. M., Schwabe, P., Seiler, G. ve Stehlé, D. (2018). CRYSTALS-Kyber: A CCA-secure module-lattice-based KEM. *2018 IEEE European Symposium on Security and Privacy* içinde (s. 353–367). IEEE.

Bos, J. W., Renes, J. ve van Vredendaal, C. (2022). Post-quantum cryptography with contemporary co-processors: Beyond Kronecker, Schönhage-Strassen & Nussbaumer. *31st USENIX Security Symposium* içinde (s. 3683–3700). USENIX Association.

Harvey, D. (2009). Faster polynomial multiplication via multipoint Kronecker substitution. *Journal of Symbolic Computation, 44*(10), 1502–1510.

Kronecker, L. (1882). Grundzüge einer arithmetischen Theorie der algebraischen Grössen. *Journal für die reine und angewandte Mathematik, 92*, 1–122.

National Institute of Standards and Technology. (2024). *Module-lattice-based key-encapsulation mechanism standard* (FIPS 203). U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.203

National Institute of Standards and Technology. (t.y.). *ACVP-Server: ML-KEM test vectors* [Veri seti]. https://github.com/usnistgov/ACVP-Server

Shor, P. W. (1994). Algorithms for quantum computation: Discrete logarithms and factoring. *Proceedings 35th Annual Symposium on Foundations of Computer Science* içinde (s. 124–134). IEEE.

> **Editör notu (rapora girmez).** Bu taslak, `docs/analiz-fable.md`'deki eleştiriler uygulanarak ve `docs/ornekler/`
> altındaki iki derece almış raporun bölüm düzeni, üslubu ve atıf biçimi örnek alınarak yazıldı. Sayılar repodaki
> CSV'lerden alındı (2026-10-30 ölçümleri). Köşeli parantezli `[…]` yerler ekip tarafından doldurulacak.
> Kaynakça'daki her künye, `docs/02-literatur.md` kuralı gereği teslimden önce ekipten biri tarafından aslından
> doğrulanmalıdır; şu an yalnızca L6 (Albrecht vd.) okunmuştur.

**Proje Ana Alanı :** Bilgisayar [veya Matematik — S4 kararı bekleniyor]
**Proje Tematik Alanı :** Siber Güvenlik ve Kriptoloji
**Proje Adı (Başlığı) :** ML-KEM Polinom Çarpımı İçin Merkezlenmiş Kronecker İkamesi: Taşma Sınırının İspatı, Deneysel Doğrulanması ve Kuantum Sonrası Dosya Aktarım Prototipi

## Özet

Günümüzde internet trafiğini koruyan RSA ve eliptik eğri tabanlı anahtar değişimi yöntemleri, yeterince büyük bir kuantum bilgisayarda Shor algoritmasıyla kırılabilmektedir. Bu nedenle ABD Ulusal Standartlar ve Teknoloji Enstitüsü (NIST) Ağustos 2024'te kafes tabanlı FIPS 203 (ML-KEM) standardını yayımlamıştır. ML-KEM'in temel aritmetik işlemi, Z₃₃₂₉[X]/(X²⁵⁶+1) halkasında polinom çarpımıdır ve standart bu çarpımı Sayı Teorik Dönüşüm (NTT) ile yapar. Bu çalışmada, aynı çarpımı polinomları tek bir büyük tamsayıya paketleyip çarpan Kronecker ikamesiyle yapmanın koşulları incelenmiştir. Çarpanlardan birinin her zaman küçük katsayılı (|s| ≤ η ≤ 3) olmasından yararlanılarak katsayılar sıfır etrafında merkezlenmiş, paketleme genişliğinin işaretsiz 32 bitten 22 bite indirilebileceği gösterilmiştir. Bu genişliğin yeterli ve en küçük olduğu ispatlanmış (Teorem 1, Önerme 1); rastgele girdilerde taşma olasılığı Merkezi Limit Teoremi'ne dayalı bir modelle öngörülmüş ve 200.000 denemeyle sınanmıştır. Model tahminleri, ölçülebilir aralıktaki tüm noktalarda ölçümün %95 güven aralığı içinde kalmıştır. Python ile yazılan sekiz Kronecker motoru, NIST'in resmî 225 test vektörünün tamamından ve 10.000 rastgele örnekten hatasız geçmiştir. Operand boyutunun 8192 bitten 5632 bite inmesi tek başına büyük tamsayı çarpımını 2,05 kat hızlandırmış; ancak standardın verileri NTT alanında saklaması nedeniyle uçtan uca ML-KEM'de NTT %20–63 daha hızlı kalmıştır. Genişlik sınırın altına çekildiğinde çarpımın doğruluğunun gizli anahtarın ℓ₁ normuna bağlı hâle geldiği gösterilmiş ve bunun güvenlik açısından anlamı tartışılmıştır. Son olarak yöntem, iki bilgisayar arasında ML-KEM-768 ile anahtar kurup dosyayı AES-256-GCM ile aktaran PQC-Drop prototipinde kullanılmıştır.

**Anahtar kelimeler:** kuantum sonrası kriptografi, ML-KEM, FIPS 203, Kronecker ikamesi, polinom çarpımı, Merkezi Limit Teoremi

## Amaç

Bu projenin amacı, NIST FIPS 203 (ML-KEM) standardındaki polinom çarpımının, katsayıları merkezlenmiş Kronecker ikamesiyle hangi koşullarda doğru yapılabileceğini matematiksel olarak belirlemek, bu koşulları deneysel olarak sınamak ve yöntemi çalışan bir güvenli dosya aktarım uygulamasında kullanmaktır. Bu doğrultuda şu alt hedefler belirlenmiştir:

1. Çarpım katsayılarının birbirine karışmaması için gereken en küçük paketleme genişliğini (ℓ_min) ispatlamak ve bu sınırın keskin olduğunu göstermek.
2. ML-KEM'in kendi katsayı dağılımları (düzgün ve merkezli binom) altında taşma olasılığını analitik bir modelle öngörmek ve modeli en az 100.000 rastgele denemeyle sınamak.
3. Kronecker tabanlı ML-KEM uygulamasının NIST'in resmî test vektörleriyle bayt bayt aynı çıktıyı verdiğini doğrulamak.
4. Merkezlemenin büyük tamsayı çarpımına, tek polinom çarpımına ve uçtan uca ML-KEM'e etkisini ölçmek; hızın hangi adımdan geldiğini ayrıştırmak.
5. Paketleme genişliği sınırın altında seçildiğinde çarpımın doğruluğunun gizli anahtara bağlı hâle geldiğini göstermek ve bunun güvenlik sonuçlarını tartışmak.
6. Yöntemi, okul laboratuvarındaki iki bilgisayar arasında çalışan bir dosya aktarım aracında (PQC-Drop) uygulamak.

## Giriş

Açık anahtarlı şifreleme, iki tarafın daha önce buluşmadan ortak bir gizli anahtar kurmasını sağlar ve bugün internet bankacılığından mesajlaşma uygulamalarına kadar hemen her güvenli bağlantının temelidir. Yaygın yöntemler olan RSA ve eliptik eğri kriptografisinin güvenliği, büyük sayıları çarpanlarına ayırmanın ve ayrık logaritma hesaplamanın klasik bilgisayarlar için pratikte imkânsız olmasına dayanır. Shor (1994), bu iki problemi kuantum bilgisayarda polinom zamanda çözen bir algoritma vermiştir. Yeterli büyüklükte ve hata düzeltmeli bir kuantum bilgisayar henüz yoktur; ancak bugün kaydedilen şifreli trafiğin ileride çözülebilmesi ("şimdi topla, sonra çöz") riski, geçişin şimdiden başlamasını gerektirmektedir (NIST, 2024).

NIST, 2016'da başlattığı değerlendirme sürecinin sonunda Ağustos 2024'te ilk kuantum sonrası standartlarını yayımlamıştır. Bunlardan FIPS 203, Kyber algoritmasından (Bos ve ark., 2018) türetilen ML-KEM anahtar kapsülleme mekanizmasını tanımlar. ML-KEM'in güvenliği Modül Üzerinde Hatalarla Öğrenme (Module-LWE) problemine dayanır ve tüm aritmetiği R_q = Z_q[X]/(Xⁿ+1), n = 256, q = 3329 halkasında polinom çarpımları üzerinden yürür. Standart bu çarpımları, Ayrık Fourier Dönüşümü'nün sonlu cisimlerdeki karşılığı olan Sayı Teorik Dönüşüm (NTT) ile yapar; açık anahtar ve A matrisi doğrudan NTT alanında üretilip saklanır.

Polinom çarpımını büyük tamsayı çarpımına indirgeyen Kronecker ikamesi (Kronecker, 1882) ise X yerine yeterince büyük bir sayı koyarak polinomu tek bir tamsayıya çevirir; iki tamsayı çarpılır ve sonuçtan katsayılar geri okunur. Yöntem hızlı polinom çarpımı literatüründe uzun süredir kullanılmaktadır (Schönhage, 1982; Harvey, 2009). Kuantum sonrası kriptografi bağlamında Albrecht ve ark. (2019), Kyber'ı akıllı kartlardaki RSA büyük tamsayı hızlandırıcısı üzerinde çalıştırmak için Kronecker ikamesini kullanmış; katsayıların karışmaması için gereken tamsayı genişliğini belirlemiş ve bu genişlik koprosesörün operand sınırını aştığı için halkayı parçalara bölen bir yaklaşım geliştirmiştir. Bos ve ark. (2022) aynı donanım hedefi için daha ileri varyantlar önermiştir. Bu çalışmalardaki ortak soru, bizim de çıkış noktamız olan sorudur: "X yerine hangi sayı yazılırsa çarpımın katsayıları birbirine karışmaz?"

Bu projenin başlangıcı, iki basamaklı sayıların karesinin binom açılımı ve elde ile hesaplanabileceği gözlemidir: 23 = 2·10 + 3 için (2x+3)² = 4x² + 12x + 9, sağdan sola elde ile 529. Buradan "taban ne kadar büyük olursa elde hiç gerekmez?" sorusu doğmuş; bu sorunun genel hâlinin Kronecker ikamesinin kendisi olduğu literatürden öğrenilmiştir. ML-KEM'de bu soru şu biçimi alır: çarpanlardan biri her zaman küçük katsayılı (gizli vektör, |s_j| ≤ η) olduğuna göre, katsayılar sıfır etrafında merkezlenirse kaç bitlik dilim yeter?

Bu çalışmanın literatürdeki çalışmalardan farkı şudur: Albrecht ve ark. (2019) ve Bos ve ark. (2022) paketleme genişliğini donanıma sığdırma sorunu olarak ele alır ve en kötü durum sınırıyla çalışır. Bu projede (i) merkezlenmiş katsayılar için sınırın en küçük olduğu açık bir keskinlik örneğiyle ispatlanmış, (ii) en kötü durum ile ML-KEM'in gerçek dağılımlarındaki tipik durum arasındaki fark olasılık modeliyle nicelenip deneyle sınanmış, (iii) bu farkın "ortalamada yeter" diye daha dar genişlik seçmeyi neden güvensiz kıldığı gösterilmiş, (iv) hızın hangi adımdan geldiği ayrıştırılmış ve (v) yöntem çalışan bir uygulamaya taşınmıştır. Çalışma yeni bir şifreleme algoritması önermemekte; standardın içindeki bir işlemi, bilinen bir yöntemin merkezlenmiş varyantıyla incelemektedir.

## Yöntem

### 1.1. Matematiksel Çerçeve ve Gösterim

n = 256, q = 3329 ve R_q = Z_q[X]/(Xⁿ+1) olsun. Katsayılar merkezlenmiş biçimde, yani {−1664, …, 1664} aralığında tutulur; A = (q−1)/2 = 1664. Küçük polinomun katsayıları s_j ∈ [−η, η] olup ML-KEM-512'de η₁ = 3, diğer parametre setlerinde η₁ = 2'dir. İki polinomun indirgenmemiş çarpımının katsayıları c_k = Σ_{i+j=k} a_i s_j (k = 0, …, 2n−2) ve negasiklik indirgeme (a·s mod Xⁿ+1)_k = c_k − c_{k+n} biçimindedir.

Kronecker ikamesinde B = 2^ℓ seçilerek P_a = Σ a_i B^i ve P_s = Σ s_j B^j tamsayıları oluşturulur. X ↦ B değerlendirmesi bir halka homomorfizması olduğundan P_a · P_s = Σ c_k B^k olur. Soru, c_k'lerin bu tek tamsayıdan tek türlü geri okunup okunamadığıdır. Bunun için dengeli rakam kümesi D_ℓ = {−2^(ℓ−1), …, 2^(ℓ−1)−1} tanımlanmıştır.

### 1.2. Taşma Sınırı ve Keskinliği

**Lemma 1 (dengeli gösterimin tekliği).** d_k ∈ D_ℓ olmak üzere C = Σ d_k B^k ise d_k'ler tek türlü belirlidir ve şu algoritma onları sırayla verir: r = C mod B; r ≥ 2^(ℓ−1) ise r = r − B; d = r; C = (C − d)/B. İspat, farklı iki gösterimin en küçük farklı basamağında B | (d_j − d'_j) çelişkisine dayanır; algoritma adımı ise 1.1'deki "ödünç" işleminin kendisidir.

**Teorem 1 (gereken genişlik).** |a_i| ≤ A ve |s_j| ≤ η ise her tam çarpım katsayısı için |c_k| ≤ T_k·A·η ≤ n·A·η'dir; burada T_k = min(k+1, 2n−1−k), k'ıncı katsayıya katkı veren terim sayısıdır. n·A·η < 2^(ℓ−1) ise her c_k ∈ D_ℓ olur ve Lemma 1 ile c tam olarak geri okunur. Bu koşulu sağlayan en küçük genişlik ℓ_min = bitlen(n·A·η) + 1'dir. Sayısal olarak η = 3 için n·A·η = 1.277.952 ve ℓ_min = 22; η = 2 için 851.968 ve ℓ_min = 21. Katsayılar merkezlenmeyip [0, q−1] aralığında tutulursa sınır n·3328² = 2.835.349.504 olur ve 32 bit gerekir. Operand boyutu böylece 256·32 = 8192 bitten 256·22 = 5632 bite iner.

**Önerme 1 (sınır keskindir).** a_i = A ve s_j = η seçildiğinde c_{n−1} = n·A·η olur; ℓ = ℓ_min − 1 için bu değer D_ℓ dışındadır ve Lemma 1 algoritması kesinlikle yanlış sonuç verir. Daha genel olarak a_i = A·sgn(s_{n−1−i}) seçilirse c_{n−1} = A·‖s‖₁ olur; yani taşma koşulu A·‖s‖₁ ≥ 2^(ℓ−1) gizli vektöre bağlıdır. Bu gözlem 1.5'teki güvenlik deneyinin temelidir.

**Önerme 2 (negasiklik kısayol).** X = 2^ℓ için Xⁿ + 1 = 2^(nℓ) + 1 =: M'dir. Çarpım mod M alınırsa doğrudan d_k = c_k − c_{k+n} dilimleri elde edilir; her dilim tam n terim içerdiğinden gereken ℓ Teorem 1 ile aynıdır, açılacak dilim sayısı 2n−1 yerine n'dir.

**Sonuç 1 (modül toplamı).** ML-KEM'deki çarpımlar k terimli iç çarpımlar (Σ_j a_j·s_j) olarak gelir. Terimler tamsayı olarak toplanıp bir kez açılırsa sınır k·n·A·η olur; üç parametre setinde de ℓ_min = 23 çıkar ve bayt hizalı 24 bit üçüne de yeter.

**Lemma 2 (bayt ile açma).** Dilimler D_ℓ içindeyse C' = C + 2^(ℓ−1)·Σ 2^(kℓ) negatif olmayan, borçsuz bir taban-2^ℓ sayısıdır; ℓ 8'in katıysa dilimler doğrudan baytlardan okunur. Bu, döngülü açmayı C düzeyinde çalışan bayt dönüşümüne çevirir.

Tüm ispatlar `docs/04-teori.md`'de, kod karşılıkları `src/pqc/teori.py` ve `src/pqc/kronecker.py`'de yer alır; sayısal tablolar `tests/test_teori.py` ile kontrol edilmiştir.

### 1.3. Rastgele Girdi İçin Olasılık Modeli

Teorem 1 en kötü durumu ele alır: tüm katsayıların aynı anda en büyük değerde ve aynı işaretli olması. ML-KEM'de ise a_i katsayıları [0, q) üzerinde düzgün, s_j katsayıları parametresi η olan merkezli binom dağılımından (CBD) gelir. Merkezlenmiş a_i için Var(a) = (q²−1)/12 ≈ 923.520, CBD(η) için Var(s) = η/2'dir. c_k, T_k adet a_i·s_j teriminin toplamı olduğundan Merkezi Limit Teoremi ile yaklaşık N(0, σ_k²), σ_k² = T_k·Var(a)·Var(s) dağılır. Tek dilimin D_ℓ dışına çıkma olasılığı p_k ≈ 2Φ(−2^(ℓ−1)/σ_k) ve açmanın bozulma olasılığı, dilimler bağımsız sayılarak,

P(hata) ≈ 1 − Π_{k=0}^{2n−2} (1 − p_k)

olarak modellenmiştir (Model 2). Modül toplamı için σ_k² k ile, negasiklik açma için T_k = n ile değiştirilir. Modelin iki bilinen yaklaşıklığı vardır: dilimler aynı a_i'leri paylaştığı için bağımsız değildir ve terimler sınırlı olduğu için gerçek dağılımın kuyruğu normalden farklıdır. Bu nedenle model deneyden önce "ölçülebilir aralıkta (10⁻³ < p < 1 − 10⁻³) %95 güven aralığı içinde kalmalı" biçiminde bir öngörü olarak kaydedilmiş, beklenen değerler deney yapılmadan `docs/03-hipotez-ve-deneyler.md`'ye yazılmıştır.

### 1.4. Yazılım ve Doğrulama Kaynakları

Tüm kütüphane Python 3 ile, harici kriptografi kütüphanesi kullanılmadan yazılmıştır (yalnızca `hashlib` SHA-3/SHAKE). FIPS 203'ün her algoritması (SampleNTT, CBD, NTT, K-PKE, ML-KEM, girdi kontrolleri) standarttaki numarasıyla kodlanmıştır. Kronecker ikamesi beş seçimle tanımlanan bir "varyant" nesnesiyle uygulanmıştır: dilim genişliği ℓ, işaretli/işaretsiz katsayı, döngülü/bayt ile paketleme-açma, negasiklik indirgemenin tamsayıda (mod 2^(nℓ)+1) yapılıp yapılmadığı ve iç çarpım terimlerinin açmadan önce toplanıp toplanmadığı. Bu seçimlerden sekiz varyant kurulmuştur: işaretsiz 32 bit (döngü, bayt), işaretli 22 bit (döngü, negasiklik), işaretli 24 bit bayt (düz, negasiklik, modül toplamı, negasiklik + modül toplamı).

Standart, A matrisini ve açık anahtarı NTT alanında ürettiği için Kronecker yolu bu nesneleri önce ters NTT ile katsayı alanına çevirir, çarpımı yapar ve gerekirse sonucu NTT ile geri çevirir. Böylece çıktı standartla bayt bayt aynı kalır; bu dönüşümler "standart uyumluluk bedeli" olarak ayrıca ölçülmüştür (1.5, E3.4).

Doğruluk üç kaynağa karşı sınanmıştır: (i) NIST ACVP resmî test vektörleri (ML-KEM-512/768/1024; keyGen 75, encaps 75, decaps 30, anahtar kontrolleri 60 vaka), (ii) okul yöntemi negasiklik çarpım (yavaş ama apaçık doğru "altın standart"), (iii) teoriden gelen sayısal sınırlar. Testlerin hata yakalama gücü, koda bilerek 12 hata yerleştiren bir mutasyon aracıyla ölçülmüştür. Her depo gönderiminde kod stili ve 1879 test otomatik olarak çalıştırılmıştır.

### 1.5. Deney Tasarımı

Her deney için beklenen sonuç deneyden önce yazılmış; sabit tohum, ham veri (CSV) ve grafik üreten betik depoda saklanmıştır. Ölçüm makineleri Tablo 1'de verilmiştir.

**Tablo 1.** Deneyler ve ölçüm ortamları

| Deney | İçerik | Makine | Python |
|---|---|---|---|
| E1 | NIST vektörleri (9 motor); 10.000 rastgele iç çarpım × 8 varyant; en kötü durum girdileri | Raspberry Pi 5 (aarch64) | 3.13.5 |
| E2 | En kötü durum keskinliği; 10 seri × 20.000 rastgele deneme, ℓ = 14 … ℓ_min; sürekli taban analizi | Intel Core i3-14100 | 3.11.2 |
| E3 | Bigint çarpımı (15.000 tekrar); tek polinom çarpımı (1000); süre dağılımı; uçtan uca ML-KEM (100) | Intel Core i3-14100 | 3.11.2 |
| E4 | ℓ ∈ {18, …, 22} için 1500 gizli vektör; 150 ML-KEM-512 anahtarı | Intel Core i3-14100 | 3.11.2 |
| E5 | PQC-Drop aktarımı ve ağ yükü karşılaştırması | [Pardus 1 ↔ Pardus 2; doldurulacak] | [ ] |

**E2 (teori–deney).** Seriler, ML-KEM'de gerçekten oluşan (k, η) çiftleridir: tek çarpım η = 3 ve η = 2; modül toplamı k = 2, 3, 4; her biri tam (2n−1 dilim) ve negasiklik (n dilim) açma ile. Her denemede büyük polinom [0, q)'da düzgün, küçük polinom CBD(η) ile çekilmiş; dilimlerin kesin değerleri ℓ = 40 ile hesaplanıp gereken en küçük yarım taban h* kaydedilmiştir. Böylece hata oranı yalnızca tam sayı ℓ'lerde değil, sürekli log₂B ekseninde de ölçülmüştür. Ölçülen oranlar için %95 Wilson güven aralığı hesaplanmıştır.

**E3 (performans).** `time.perf_counter_ns`, ısınma turu, çöp toplayıcı kapalı, medyan ve çeyrekler arası aralık (IQR) raporlanmıştır. NTT ölçümü iki ileri dönüşüm + çarpım + bir ters dönüşümü içerir; ML-KEM'de A zaten NTT alanında olduğundan bu, NTT aleyhine hafif bir kıyastır. Tüm süreler Python'a aittir; C uygulamalarına genellenemez (bkz. Sonuç ve Tartışma).

**E4 (anahtara bağlı davranış).** Önerme 1'deki girdi (a_i = A·sgn(s_{n−1−i})) ile ℓ ∈ {18, …, 22} için çarpımın bozulup bozulmadığı, ‖s‖₁ ile karşılaştırılmıştır. 1500 vektörün 700'ü gerçek CBD(3) ve CBD(2) örnekleri, 800'ü eşik çevresini taramak için normu 156–673 aralığına yapay olarak ayarlanmış vektörlerdir. 150 ML-KEM-512 anahtarının 75'i gerçek anahtar üretiminden, 75'i eşik çevresini (280–360) görmek için gizli vektörü yapay olarak büyütülmüş anahtarlardır. Saldırgan girdisi, FIPS 203'ün 10 bitlik şifreli metin sıkıştırmasına uygun uç değerlerle (y = 511 → +1661, y = 512 → −1664) kurulmuştur. Bu deneyde decapsulation çağrılmamış; yalnızca iç çarpımın doğruluğu ölçülmüştür (nedeni 2.4'te).

### 1.6. PQC-Drop Prototipi

PQC-Drop, iki bilgisayar arasında dosya aktaran bir komut satırı aracıdır. Alıcı ML-KEM-768 ile anahtar çifti üretip açık anahtarı (1184 bayt) gönderir; gönderici kapsülleme yapıp şifreli metni (1088 bayt) yollar; iki taraf da 32 baytlık ortak sırdan HKDF-SHA256 ile 256 bitlik AES anahtarı türetir. Dosya 64 KB'lık parçalar hâlinde AES-256-GCM ile şifrelenir; her parça kendi kimlik doğrulama etiketiyle, aktarım sonunda tüm dosya SHA-256 özetiyle doğrulanır. Polinom çarpımı için `isaretli24-bayt-negmod` motoru kullanılmıştır. ML-KEM ve Kronecker katmanı projenin kendi kodudur; AES-GCM ve HKDF için sistemde hazır bulunan `cryptography` paketi kullanılmıştır. Prototipte açık anahtar imzalanmamaktadır; bu nedenle araç pasif dinlemeye karşı koruma sağlar, aktif ortadaki adam saldırısına karşı kimlik doğrulama katmanı gerektirir (bkz. Öneriler).

### Proje İş-Zaman Çizelgesi

| İşin Tanımı | Ekim | Kasım | Aralık | Ocak |
|---|:---:|:---:|:---:|:---:|
| Literatür taraması ve kaynak doğrulama | X | X | | |
| Teori (ispatlar, olasılık modeli) | X | X | | |
| ML-KEM uygulaması ve NIST testleri | X | X | | |
| Kronecker motorları ve deneyler (E1–E4) | X | X | X | |
| PQC-Drop prototipi ve ağ ölçümü | | X | X | |
| Proje raporu yazımı | | | X | X |

## Bulgular

### 2.1. Doğruluk (E1)

NTT yolu ve sekiz Kronecker varyantının her biri, üç parametre setindeki 225 NIST ACVP vakasının tamamından geçmiştir. 10.000 rastgele iç çarpımda ((k, η) ∈ {(1,3), (2,3), (3,2), (4,2)}, her biri 2.500) sekiz varyantın hiçbiri okul yönteminden sapmamıştır (Tablo 2). Tüm katsayıların ±1664 ve +3 olduğu en kötü durum girdileri de sekiz varyantta doğru sonuç vermiştir. Mutasyon aracına yerleştirilen 12 hatanın 12'si testlerce yakalanmıştır.

**Tablo 2.** 10.000 rastgele iç çarpımda hata sayısı

| Varyant | Hatalı / toplam |
|---|---|
| isaretsiz32-dongu, isaretsiz32-bayt | 0 / 10.000 |
| isaretli22-dongu, isaretli22-negmod | 0 / 10.000 |
| isaretli24-bayt, isaretli24-bayt-negmod | 0 / 10.000 |
| isaretli24-bayt-modul, isaretli24-bayt-negmod-modul | 0 / 10.000 |

Rastgele girdide katsayılar 18 bit civarında kaldığından bu deney sınırın yakınına hiç gelmez; sınırın yeterliliğini gösteren şey ispat ve en kötü durum testleridir. Bu deney, yöntemin ML-KEM'in gerçek dağılımlarında da sorunsuz çalıştığını gösterir.

### 2.2. Teori ile Deneyin Örtüşmesi (E2)

**Keskinlik.** 10 serinin her birinde en kötü durum girdileri ℓ = ℓ_min'de doğru, ℓ = ℓ_min − 1'de bozuk sonuç vermiştir (60 çalıştırma, 0 beklenmedik sonuç). 200.000 rastgele denemede gerçek açma sonucu ile Lemma 1 ölçütü (h* ≤ 2^(ℓ−1)) arasında hiç uyumsuzluk görülmemiştir; bu, açma algoritmasının ispattaki ölçütle birebir davrandığını gösterir.

**Model ile ölçüm.** Tablo 3, hata oranının 0 ile 1 arasında ölçülebildiği noktaları vermektedir. Model tahmini her satırda %95 Wilson güven aralığının içindedir. ℓ ≥ 19'da hiçbir seride 20.000 denemede hata görülmemiş, model tahmini de 10⁻¹⁵'in altında kalmıştır.

**Tablo 3.** Model 2 tahmini ile ölçülen hata oranı (seri başına 20.000 deneme)

| Seri | ℓ | Hatalı / toplam | Ölçülen | %95 güven aralığı | Model 2 |
|---|:---:|:---:|:---:|:---:|:---:|
| tek-η3-tam | 17 | 602 / 20.000 | 3,01·10⁻² | [2,78; 3,26]·10⁻² | 3,06·10⁻² |
| tek-η3-neg | 17 | 2.434 / 20.000 | 1,22·10⁻¹ | [1,17; 1,26]·10⁻¹ | 1,20·10⁻¹ |
| tek-η2-tam | 17 | 23 / 20.000 | 1,15·10⁻³ | [0,77; 1,73]·10⁻³ | 0,91·10⁻³ |
| tek-η2-neg | 17 | 99 / 20.000 | 4,95·10⁻³ | [4,07; 6,02]·10⁻³ | 5,17·10⁻³ |
| modül-512-neg | 18 | 4 / 20.000 | 2,0·10⁻⁴ | [0,78; 5,14]·10⁻⁴ | 2,2·10⁻⁴ |
| modül-768-neg | 18 | 6 / 20.000 | 3,0·10⁻⁴ | [1,37; 6,54]·10⁻⁴ | 2,2·10⁻⁴ |
| modül-1024-tam | 18 | 12 / 20.000 | 6,0·10⁻⁴ | [3,43; 10,5]·10⁻⁴ | 9,1·10⁻⁴ |
| modül-1024-neg | 18 | 110 / 20.000 | 5,5·10⁻³ | [4,57; 6,62]·10⁻³ | 5,17·10⁻³ |

Sürekli taban analizinde (Şekil 1 ve Şekil 2) model eğrisi ile ölçülen noktalar tüm seriler için üst üste gelmiş; bozulma olasılığının 0,5 olduğu log₂B değeri model ve ölçümde en fazla 0,01 farkla aynı çıkmıştır (Tablo 4). Modül toplamında ML-KEM-512 (k = 2, η = 3) ile ML-KEM-768 (k = 3, η = 2) serilerinin aynı eğriyi vermesi, modelin yalnızca k·η'ya bağlı olduğu öngörüsünü doğrulamıştır. Negasiklik açma, her dilimi n terimli yaptığı için aynı ℓ'de yaklaşık 0,17 bit daha geniş taban gerektirmiştir.

**Tablo 4.** Tipik durum ile en kötü durum arasındaki fark (log₂B)

| Seri | Model medyanı | Ölçülen medyan | 20.000 denemede en büyük | ℓ_min (en kötü) | Fark |
|---|:---:|:---:|:---:|:---:|:---:|
| tek-η3-tam | 16,62 | 16,61 | 17,49 | 22 | 4,5 bit |
| tek-η2-tam | 16,32 | 16,32 | 17,20 | 21 | 3,8 bit |
| modül-512-tam | 17,12 | 17,11 | 17,92 | 23 | 5,1 bit |
| modül-768-tam | 17,12 | 17,12 | 17,98 | 23 | 5,0 bit |
| modül-1024-tam | 17,32 | 17,33 | 18,16 | 23 | 4,8 bit |

Şekil 3, rastgele girdide gereken tabanın dağılımını ispatın verdiği sınırla birlikte göstermektedir: rastgele girdiler 17–18 bitte kalırken sınır 21–23 bittir. Bu 4–5 bitlik aralık 2.4'teki deneyin konusudur.

*Şekil 1. Tam çarpım serilerinde Model 2 eğrisi ve ölçülen hata oranları (%95 güven aralığı) — `experiments/02-teori-deney/grafik_e24.png`*
*Şekil 2. Negasiklik serilerinde aynı karşılaştırma — `grafik_e24_neg.png`*
*Şekil 3. Rastgele girdide gereken log₂B dağılımı ve ℓ_min — `grafik_fark.png`*

### 2.3. Performans (E3)

**Büyük tamsayı çarpımı.** Operand 8192 bitten 5632 bite inince çarpım süresi 20,35 µs'den 9,94 µs'ye düşmüştür (2,05 kat; Tablo 5). Karatsuba karmaşıklığından beklenen alt sınır (8192/5632)^1,585 ≈ 1,81'di; ölçülen değerin bunun üstünde çıkmasının olası nedeni, CPython'un belirli bir boyutun altında okul yöntemine geçmesi nedeniyle bu boyutlarda etkin üssün 1,585'ten büyük olmasıdır; bu neden ayrıca ölçülmemiştir.

**Tablo 5.** Saf büyük tamsayı çarpımı (15.000 tekrar, medyan)

| Paketleme | Operand (bit) | Medyan (µs) | IQR (µs) | Hızlanma |
|---|:---:|:---:|:---:|:---:|
| 32 bit (işaretsiz) | 8192 | 20,35 | 0,86 | 1,00× |
| 24 bit (bayt hizalı) | 6144 | 11,68 | 0,05 | 1,74× |
| 22 bit (η = 3) | 5632 | 9,94 | 0,18 | 2,05× |
| 21 bit (η = 2) | 5376 | 9,20 | 0,04 | 2,21× |

**Tek polinom çarpımı.** Katsayı alanında verilen iki polinom için bayt hizalı Kronecker varyantları (106–145 µs) saf Python NTT'den (284 µs) hızlı, döngülü açma varyantları ise NTT ile aynı düzeyde veya daha yavaştır (Tablo 6). Dikkat çekici bulgu, en hızlı varyantın işaretsiz 32 bitlik bayt varyantı (106 µs) olmasıdır: merkezlemenin tamsayı çarpımında sağladığı yaklaşık 10 µs'lik kazanç, paketleme ve açma süreleri (yaklaşık 80–90 µs) içinde kaybolmaktadır. Süre dağılımı (Tablo 7, Şekil 6) bunu doğrular: döngülü işaretli açma sürenin %75'ini alırken, Lemma 2'deki bayt ile açma bu süreyi 212 µs'den 55 µs'ye indirmiştir. Yani Python ortamında hız farkını belirleyen şey operand boyutu değil, paketleme/açmanın C düzeyinde (bayt dönüşümüyle) yapılıp yapılmadığıdır.

**Tablo 6.** Tek polinom çarpımı (medyan, µs)

| Yöntem | Medyan | IQR |
|---|:---:|:---:|
| Okul yöntemi | 3290,95 | 322,47 |
| NTT (ileri + çarpım + ters) | 284,28 | 11,53 |
| NTT (yalnızca NTT alanında çarpım) | 21,49 | 1,00 |
| KS isaretsiz32-dongu | 207,79 | 1,61 |
| KS isaretsiz32-bayt | 106,10 | 2,34 |
| KS isaretli22-dongu | 314,83 | 6,49 |
| KS isaretli24-bayt | 130,18 | 2,32 |
| KS isaretli22-negmod | 196,45 | 1,64 |
| KS isaretli24-bayt-negmod | 145,17 | 1,53 |
| KS isaretli24-bayt-modul | 122,85 | 2,24 |
| KS isaretli24-bayt-negmod-modul | 137,27 | 1,25 |

**Tablo 7.** Kronecker varyantlarında süre dağılımı (µs)

| Varyant | Paketleme | Tamsayı çarpımı | Açma / indirgeme | Toplam |
|---|:---:|:---:|:---:|:---:|
| isaretsiz32-dongu | 80,8 | 21,5 | 102,6 | 204,8 |
| isaretsiz32-bayt | 25,4 | 20,6 | 51,8 | 97,7 |
| isaretli22-dongu | 60,3 | 10,3 | 212,4 | 283,0 |
| isaretli24-bayt | 28,8 | 12,5 | 55,0 | 96,3 |
| isaretli22-negmod | 61,6 | 46,1 | 48,9 | 156,6 |
| isaretli24-bayt-negmod | 27,6 | 54,6 | 27,4 | 109,6 |

**Uçtan uca ML-KEM.** Standartla bayt bayt aynı çıktıyı üretmek için yapılan ters NTT dönüşümleri (ML-KEM-768 kapsüllemede 12 adet) Kronecker yolunu NTT yolunun gerisinde bırakmıştır (Tablo 8). NTT, parametre seti büyüdükçe artan oranda önde kalmaktadır: anahtar üretiminde %39 / %49 / %63, kapsüllemede %20 / %32 / %43, kapsül açmada %22 / %36 / %45 (ML-KEM-512 / 768 / 1024). Bu bulgu deneyden önce öngörülmüştü: Kronecker çarpımı sıfır sürede yapılsa bile dönüşüm bedeli kalır. Dolayısıyla "Kronecker ikamesi ML-KEM'i hızlandırır" iddiası bu çalışmanın verileriyle desteklenmemektedir; yöntemin avantajı, verilerin katsayı alanında tutulduğu veya NTT donanımının bulunmayıp büyük tamsayı çarpıcısının bulunduğu ortamlarla sınırlıdır.

**Tablo 8.** Uçtan uca ML-KEM süreleri (100 tekrar, medyan, µs)

| Parametre | Motor | KeyGen | Encaps | Decaps |
|---|---|:---:|:---:|:---:|
| ML-KEM-512 | NTT (standart) | 2692 | 4289 | 4698 |
| | KS isaretli24-bayt-negmod | 3736 | 5167 | 5728 |
| | KS isaretli22-negmod | 3844 | 5493 | 6190 |
| ML-KEM-768 | NTT (standart) | 4138 | 6227 | 6532 |
| | KS isaretli24-bayt-negmod | 6153 | 8242 | 8903 |
| | KS isaretli22-negmod | 6533 | 8729 | 9844 |
| ML-KEM-1024 | NTT (standart) | 5516 | 8156 | 8688 |
| | KS isaretli24-bayt-negmod | 8987 | 11698 | 12579 |
| | KS isaretli22-negmod | 10151 | 13379 | 14709 |

*Şekil 4. Bigint çarpım süreleri — `experiments/04-performans/grafik_e31.png`*
*Şekil 5. Tek polinom çarpımı yöntem kıyaslaması — `grafik_e32.png`*
*Şekil 6. Varyantlarda süre dağılımı — `grafik_e33.png`*
*Şekil 7. Uçtan uca ML-KEM — `grafik_e34.png`*

### 2.4. Sınırın Altında Anahtara Bağlı Davranış (E4)

2.2'de rastgele girdilerin 18 bitte bile hata vermediği görülmüştü. Bu bölüm, "o hâlde 22 yerine 18–20 bit kullanılsın" seçiminin sonucunu inceler. Önerme 1'e göre saldırganın seçebildiği a için taşma koşulu A·‖s‖₁ ≥ 2^(ℓ−1), yani ‖s‖₁ ≥ ⌈2^(ℓ−1)/1664⌉'tür: ℓ = 18 için 79, ℓ = 19 için 158, ℓ = 20 için 316, ℓ = 21 için 631; ℓ = 22 için 1261, ki bu n·η = 768'i aştığından ℓ = 22'de taşma imkânsızdır.

1500 vektörde beş ℓ değeri için ölçülen bozulma ile teorik eşik arasında tek bir uyumsuzluk görülmemiştir; bozulma, normun eşiğe ulaştığı noktada başlayan bir basamak fonksiyonu biçimindedir (Şekil 8). 150 ML-KEM-512 anahtarında, sıkıştırmaya uygun uç değerlerle kurulan şifreli metin için de aynı eşik (316) sıfır uyumsuzlukla gözlenmiştir (Şekil 9).

Bu sonucun ölçüsü dikkatle verilmelidir. Gerçek CBD(3) gizli vektörlerinde E‖s‖₁ = 240'tır ve deneydeki 700 gerçek örneğin hiçbiri 316 eşiğini aşmamıştır (en büyük 282); 75 gerçek anahtarın hiçbiri ℓ = 20'de bozulmamış, bozulma yalnızca normu yapay olarak büyütülmüş anahtarlarda görülmüştür. Buna karşılık ℓ = 19 (eşik 158) ve ℓ = 18 (eşik 79) için gerçek anahtarların tamamı saldırgan girdisiyle bozulmaktadır. Yani "rastgele girdide çalışıyor" gözlemiyle seçilen 18–19 bit, uygun seçilmiş bir girdi karşısında her anahtarda hata verir; 20 bit ise anahtarların küçük bir kesiminde hata verir ve hata verip vermemesi anahtarın normuna bağlıdır.

Bu davranışın bir saldırıya dönüşüp dönüşmediği ayrıca değerlendirilmelidir. FIPS 203'te kapsül açma, mesajı yeniden şifreleyip gelen şifreli metinle karşılaştırır; saldırganın kurduğu şifreli metin geçerli bir kapsülleme olmadığından bu karşılaştırma taşma olsa da olmasa da başarısız olur ve örtük reddetme ile sahte anahtar döner. Dolayısıyla kapsül açma çıktısının kendisi taşmayı dışarı vermez; bilginin sızması için ayrıca bir yan kanal (örneğin zamanlama farkı veya protokol düzeyinde hata bildirimi) gerekir. Bu çalışmada gösterilen şey, sınırın altında çarpımın doğruluğunun gizli anahtara bağımlı hâle geldiğidir; kriptografik uygulamalarda anahtara bağlı davranış, sömürülebilir olduğu gösterilmese bile kabul edilmeyen bir özelliktir. Teorem 1'in sınırı bu bağımlılığı tamamen ortadan kaldırır.

*Şekil 8. ℓ ∈ {18, …, 22} için ‖s‖₁'e karşı çarpım hatası ve teorik eşikler — `experiments/03-guvenlik/grafik_e41.png`*
*Şekil 9. ML-KEM-512 anahtarlarında ℓ = 20 için ‖s₀‖₁'e karşı iç çarpım bozulması — `grafik_e42.png`*

### 2.5. PQC-Drop ve Ağ Yükü (E5)

PQC-Drop ile [boyut] MB'lık bir dosya iki Pardus bilgisayar arasında aktarılmış; alıcıda SHA-256 özeti eşleşmiş, tek biti değiştirilmiş bir parça AES-GCM etiketiyle reddedilmiştir. El sıkışma süresi (anahtar üretimi + kapsül açma, Kronecker motoruyla) [x] ms, aktarım hızı [y] MB/s ölçülmüştür. [Ekran görüntüsü / Wireshark yakalaması eklenecek; şu an repoda yalnızca betik içi simülasyon vardır.]

Aynı içerik için ağ yükü üç durumda karşılaştırılmıştır (Tablo 9): şifresiz HTTP isteği, yalnızca klasik X25519 anahtar değişimiyle kurulmuş AES-GCM yükü ve PQC-Drop yükü. Kuantum sonrası anahtar değişiminin bedeli açık anahtar boyutundadır: 32 bayt yerine 1184 bayt açık anahtar ve 1088 bayt kapsül. Şifresiz yükte dosya içeriği ve adı doğrudan okunabilirken iki şifreli yükte açık metin araması sonuç vermemiştir. Shannon entropisi her üç yük için hesaplanmış; ancak n baytlık bir örneklemin entropisi en çok log₂n olabildiğinden kısa şifreli yük (214 bayt, 7,03 bit/bayt) ile uzun şifreli yük (2422 bayt, 7,92 bit/bayt) arasındaki fark örneklem boyutundan kaynaklanmaktadır ve şifreleme kalitesi hakkında bilgi vermez; iki değer de aynı uzunluktaki saf rastgele bayt dizisinin beklenen entropisine eşittir.

**Tablo 9.** Aynı içerik için ağ yükü karşılaştırması

| Ölçüt | Şifresiz HTTP | Klasik ECDHE + AES-GCM | PQC-Drop (ML-KEM-768 + AES-GCM) |
|---|:---:|:---:|:---:|
| Anahtar değişimi | yok | X25519 | ML-KEM-768 (Kronecker motoru) |
| Açık anahtar | — | 32 bayt | 1184 bayt |
| Toplam yük | 232 bayt | 214 bayt | 2422 bayt |
| Açık metin araması | bulundu | bulunamadı | bulunamadı |
| Shor algoritmasına karşı | — | savunmasız | bilinen kuantum saldırısı yok (NIST Kategori 3 hedefi) |

Günümüzde büyük tarayıcılar ve servisler TLS 1.3'te X25519 ile ML-KEM-768'i birleştiren hibrit anahtar değişimine geçmektedir; tablodaki "klasik ECDHE" sütunu bu nedenle güncel TLS'i değil, yalnızca klasik yöntemle kurulmuş bir bağlantıyı temsil eder.

## Sonuç ve Tartışma

1. **Sınır ispatlandı ve keskin.** Merkezlenmiş Kronecker ikamesinde taşmasız açma için gereken en küçük genişlik ℓ_min = bitlen(n·A·η) + 1 olarak ispatlanmış (η = 3 için 22, η = 2 için 21, modül toplamı için 23 bit), ℓ_min − 1'de kesinlikle bozulan bir girdi verilmiştir. 60 en kötü durum çalıştırması ve 200.000 rastgele denemede açma algoritması ispattaki ölçütle birebir davranmıştır.
2. **Model deneyle uyumlu.** Merkezi Limit Teoremi'ne dayalı Model 2'nin deneyden önce kaydedilen tahminleri, ölçülebilir aralıktaki tüm noktalarda %95 güven aralığı içinde kalmıştır. Modelin bağımsızlık ve normal yaklaşımı nedeniyle çok küçük olasılıklarda (p < 10⁻⁴) sapma yönü bu örneklemle ayırt edilememiştir.
3. **Hız kazancı bigint çarpımında, uçtan uca değil.** Operand küçülmesi tamsayı çarpımını 2,05 kat hızlandırmış; ancak Python'da tek polinom çarpımında süreyi paketleme/açma belirlediğinden işaretsiz 32 bitlik bayt varyantı işaretli 24 bitlik varyantla aynı hızdadır. Uçtan uca ML-KEM'de standardın NTT alanı tercihi nedeniyle NTT %20–63 önde kalmıştır. Bu bulgu, yöntemin kullanım alanını daraltır: katsayı alanında çalışan veya NTT donanımı bulunmayan ortamlar.
4. **Sınırın altı anahtara bağlıdır.** 18–20 bitlik "ortalamada yeterli" seçimler, uygun seçilmiş girdiyle çarpımın doğruluğunu gizli anahtarın normuna bağlar; 18–19 bitte her gerçek anahtar, 20 bitte normu büyük anahtarlar bozulur. FIPS 203'ün örtük reddetmesi bu durumun doğrudan sızmasını engeller; sömürü için yan kanal gerekir. Yine de anahtara bağlı davranış tek başına, sınırın altına inmemek için yeterli gerekçedir.
5. **Prototip çalışıyor.** PQC-Drop, standartla uyumlu ML-KEM-768'i Kronecker motoruyla kullanarak dosya aktarmıştır.

**Sınırlılıklar.** (i) Tüm süreler Python'a aittir; C/donanım uygulamalarında paketleme/açma maliyeti ve bigint çarpım algoritması farklıdır, sonuçlar genellenemez. (ii) Uygulama sabit zamanlı değildir; büyük tamsayı aritmetiği veriye bağlı dallanma içerir (Bernstein ve ark., 2024'teki KyberSlash türü zamanlama sızıntıları bu uygulamaya da uygulanabilir). (iii) Performans ölçümleri tek makinede yapılmıştır; ikinci makine ölçümü (E3.5) tamamlanmamıştır. (iv) E4'teki eşik çevresi yapay normlu vektörlerle taranmıştır; gerçek dağılımda 20 bit eşiğinin aşılma olasılığı ölçülmemiş, yalnızca "ender" olduğu görülmüştür. (v) Ağ yükü karşılaştırması betik içinde üretilen baytlar üzerinden yapılmıştır; gerçek paket yakalaması [eklenecek]. (vi) Prototipte açık anahtar kimlik doğrulaması yoktur. (vii) Kaynakçadaki çalışmaların [şu an L6 dışındakiler] aslından doğrulanması tamamlanmamıştır.

[Yapay zekâ destekli araç kullanımı: şartname ve danışman kararına göre bu bölümde beyan edilecek — bkz. docs/06 S3.]

## Öneriler

1. Donanımda NTT bulunmayan ancak büyük tamsayı çarpıcısı bulunan ortamlar (eski akıllı kart ve IoT koprosesörleri) için merkezlenmiş paketleme, gereken operand genişliğini %31 azaltır; Albrecht ve ark. (2019)'daki halka bölme yaklaşımıyla birlikte değerlendirilmelidir.
2. Kronecker tabanlı herhangi bir uygulamada paketleme genişliği, ortalama durum ölçümleriyle değil Teorem 1'deki en kötü durum sınırıyla seçilmelidir; bu çalışmanın E4 deneyi bunun somut gerekçesidir.
3. Yöntemin C dilinde, sabit zamanlı büyük tamsayı aritmetiğiyle yeniden ölçülmesi, Python bulgularının hangilerinin dile özgü olduğunu ayırt edecektir.
4. E4'teki anahtara bağlı davranışın zamanlama yan kanalına dönüşüp dönüşmediği, ℓ < ℓ_min seçilmiş bir uygulamada kapsül açma sürelerinin ‖s‖₁ ile ilişkisi ölçülerek incelenebilir.
5. PQC-Drop'a açık anahtar imzalama (örneğin ML-DSA, FIPS 204) eklenerek aktif saldırılara karşı kimlik doğrulama sağlanabilir.

## Kaynaklar

Albrecht, M. R., Hanser, C., Höller, A., Pöppelmann, T., Virdia, F., & Wallner, A. (2019). Implementing RLWE-based schemes using an RSA co-processor. *IACR Transactions on Cryptographic Hardware and Embedded Systems, 2019*(1), 169–208.

Bernstein, D. J., Bhargavan, K., Bhasin, S., Chattopadhyay, A., Chia, T. K., Kannwischer, M. J., Kiefer, F., Paiva, T., Ravi, P., & Tamvada, G. (2024). KyberSlash: Exploiting secret-dependent division timings in Kyber implementations. *IACR Cryptology ePrint Archive*, 2024/1049.

Bos, J., Ducas, L., Kiltz, E., Lepoint, T., Lyubashevsky, V., Schanck, J. M., Schwabe, P., Seiler, G., & Stehlé, D. (2018). CRYSTALS-Kyber: A CCA-secure module-lattice-based KEM. *2018 IEEE European Symposium on Security and Privacy (EuroS&P)*, 353–367.

Bos, J. W., Renes, J., & van Vredendaal, C. (2022). Post-quantum cryptography with contemporary co-processors: Beyond Kronecker, Schönhage-Strassen & Nussbaumer. *31st USENIX Security Symposium*, 3683–3700.

Harvey, D. (2009). Faster polynomial multiplication via multipoint Kronecker substitution. *Journal of Symbolic Computation, 44*(10), 1502–1510.

Karatsuba, A., & Ofman, Y. (1963). Multiplication of multidigit numbers on automata. *Soviet Physics Doklady, 7*, 595–596.

Kronecker, L. (1882). Grundzüge einer arithmetischen Theorie der algebraischen Grössen. *Journal für die reine und angewandte Mathematik, 92*, 1–122.

National Institute of Standards and Technology. (2024). *Module-Lattice-Based Key-Encapsulation Mechanism Standard* (FIPS 203). U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.203

National Institute of Standards and Technology. (t.y.). *ACVP-Server: ML-KEM test vectors* [Veri seti]. https://github.com/usnistgov/ACVP-Server

Schönhage, A. (1982). Asymptotically fast algorithms for the numerical multiplication and division of polynomials with complex coefficients. *Computer Algebra, EUROCAM '82*, Lecture Notes in Computer Science 144, 3–15.

Shor, P. W. (1994). Algorithms for quantum computation: Discrete logarithms and factoring. *Proceedings 35th Annual Symposium on Foundations of Computer Science*, 124–134.

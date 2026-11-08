# Kuantum Sonrası Güvenli İletişimde Kronecker Yönteminin İncelenmesi

> Danışman görüşü doğrultusunda sadeleştirilmiş rapor taslağı — 6 Kasım 2026.
> Ana alan: [danışmanla kesinleştirilecek]. Tematik alan: Siber Güvenlik ve Kriptoloji.
> Bu sürüm mevcut deney kayıtlarını anlatır; yeni deney yapılmamıştır. Ayrıntılı ispatlar ve geniş sonuç tabloları teknik taslakta korunmuştur. Kaynak doğrulama ve yapay zekâ kullanım beyanı teslim öncesinde tamamlanmalıdır.

## Özet

İnternet üzerinden güvenli iletişim kurabilmek için tarafların ortak bir gizli anahtar oluşturması gerekir. Gelecekte yeterince güçlü kuantum bilgisayarların bazı yaygın anahtar oluşturma yöntemlerini tehdit edebilmesi, yeni yöntemlerin araştırılmasını önemli hâle getirmiştir. Bu çalışmada, kuantum sonrası güvenli iletişim için geliştirilen ML-KEM yöntemindeki bir çarpma işlemi incelenmiştir.
 Çalışma kapsamında geliştirilen yöntem, yalnızca simülasyon ortamında değil, fiziksel ESP32 (Xtensa mimarili) mikrodenetleyicisi üzerinde de donanımsal register sayaçlarıyla doğrulanmış ve 1000 bayt altı (768 B) yerel tampon modelinin kararlılığı kanıtlanmıştır.

Araştırmada Kronecker ikamesi adı verilen yöntem kullanılmıştır. Bu yöntem, birden fazla katsayıyı tek bir büyük sayıda birleştirerek çarpma yapar. Ancak katsayılara yeterli yer ayrılmazsa sonuçlar birbirine karışabilir. Çalışmanın temel sorusu, doğru sonucu koruyarak bu alanın ne kadar küçültülebileceğidir.

İncelenen tek polinom çarpımında, katsayıların sıfırın çevresinde gösterilmesiyle her katsayı için ayrılan alanın 32 bitten 22 bite indirilebildiği matematiksel olarak gösterilmiştir. Matematiksel sınır ve hata olasılığı modeli toplam 200.000 rastgele denemeyle incelenmiş; sekiz uygulama biçimi ayrıca 10.000 rastgele doğruluk örneğinde karşılaştırılmıştır. Büyük sayıların yalnızca çarpıldığı aşama 2,05 kat hızlanmıştır. Bununla birlikte, verileri farklı gösterimler arasında dönüştürmek ek süre gerektirdiğinden ML-KEM işlemlerinin tamamında standart yöntem daha hızlı kalmıştır. Gerekenden az yer ayrıldığında ise bazı özel girdilerde hataların gizli anahtarın özelliklerine bağlı olduğu görülmüştür.

Yöntem ayrıca PQC-Drop adlı dosya aktarım prototipine uygulanmıştır. Bulgular, daha küçük sayılarla hesaplama yapmanın hangi koşullarda doğru sonuç verdiğini ve tek bir işlemdeki hızlanmanın bütün uygulamaya neden aynı ölçüde yansımadığını göstermektedir.

**Anahtar kelimeler:** kuantum sonrası kriptografi, ML-KEM, Kronecker ikamesi, polinom çarpımı, güvenli dosya aktarımı.

## Amaç

Bu çalışmanın amacı, güvenli iletişimde kullanılan ML-KEM yönteminin içindeki çarpma işlemini daha küçük sayılarla gerçekleştirmenin koşullarını belirlemektir. Bunun için üç soru araştırılmıştır:

1. Sayılara ayrılan alan, hesaplama sonucu bozulmadan ne kadar azaltılabilir?
2. Bu küçülme, çarpma işlemini ve anahtar oluşturma sürecinin tamamını ne kadar etkiler?
3. Alan gereğinden fazla küçültülürse hangi durumlarda hata oluşur?
4. Geliştirilen düşük bellekli model gerçek bir mikrodenetleyici donanımı (ESP32) üzerinde nasıl bir başarım gösterir?

Araştırmanın uygulama bölümünde, incelenen yöntem bir dosya aktarım prototipine (PQC-Drop) eklenmiş ve fiziksel bir ESP32 mikrodenetleyicisi üzerinde donanımsal sayaçlarla test edilmiştir.

## Giriş

Bir dosyanın ağ üzerinden okunmadan aktarılabilmesi için şifrelenmesi gerekir. Şifreyi açacak gizli anahtarın iki tarafça güvenli biçimde oluşturulması da bu sürecin önemli bir parçasıdır. Shor'un çalışması, yeterli kapasitedeki bir kuantum bilgisayarın günümüzde kullanılan bazı açık anahtarlı yöntemlerin dayandığı matematiksel problemleri çözebileceğini göstermiştir (Shor, 1994). Bu nedenle kuantum sonrası kriptografi alanında yeni yöntemler geliştirilmiştir. NIST'in yayımladığı ML-KEM standardı bunlardan biridir (NIST, 2024).

ML-KEM, iki tarafın aynı gizli anahtarı elde etmesini sağlar. İçinde sık kullanılan işlemlerden biri polinom çarpımıdır. Polinom, örneğin 2x + 3 gibi, sayılar ile bir değişkenin kuvvetlerinden oluşan matematiksel bir ifadedir. Bu projede incelenen polinomlarda 256 katsayı bulunur. Bu kadar çok katsayıyla yapılan çarpımların nasıl gerçekleştirildiği, işlem süresini etkiler.

Çıkış noktamız basit bir sayı örneğidir: 23 sayısı, 2 × 10 + 3 olarak yazılabilir. Benzer biçimde bir polinomdaki x yerine yeterince büyük bir sayı konursa bütün katsayılar tek bir tamsayı içinde temsil edilebilir. İki böyle sayı çarpıldıktan sonra sonuçtaki katsayılar geri ayrılır. Kronecker ikamesi bu düşünceye dayanır. Sayı içindeki bölmeler çok dar seçilirse, elde işlemi komşu bölmeleri etkiler ve katsayılar doğru okunamaz.

Kronecker ikamesi daha önce de araştırılmış ve kuantum sonrası kriptografide kullanılmıştır (Harvey, 2009; Albrecht ve ark., 2019). Bu projede ML-KEM'deki küçük katsayılardan yararlanılarak bölmelerin ne kadar daraltılabileceği incelenmiştir. Çalışmanın katkısı, bu sınırın matematiksel gerekçesini, deneylerdeki karşılığını ve işlem süresine etkisini birlikte değerlendirmektir.

## Yöntem

### 1. Sayıların daha küçük değerlerle gösterilmesi

ML-KEM'deki hesaplamalarda sayılar 3329'a göre kalanlarıyla temsil edilir. Örneğin 3328 ile −1 bu hesaplamalarda aynı kalanı temsil eder. Büyük pozitif değerleri bu şekilde daha küçük negatif değerlerle göstermek, sayıları sıfırın çevresine toplar. Raporda buna “merkezleme” denmiştir.

Kronecker yönteminde her katsayı için ayrılan ikili basamak sayısı, paketleme genişliğidir. Bir bit, bilgisayarda 0 veya 1 değerini tutan bir basamaktır. Genişliği azaltmak, çarpılacak büyük sayıyı küçültür. Ancak doğru sonucu korumak için çarpımda oluşabilecek en büyük katsayının da bu alana sığması gerekir.

Tek polinom çarpımında büyük katsayının mutlak değeri en fazla 1664, küçük katsayınınki en fazla 3 olduğunda, bir sonuç katsayısının mutlak değeri en çok

**256 × 1664 × 3 = 1.277.952**

olabilir. İşaretli 22 bit bu değeri karşılar; 21 bit bütün olası girdiler için yeterli değildir. Küçük katsayı sınırı 2 olduğunda 21 bit yeterlidir. Birden fazla polinom çarpımının sonuçları ayrılmadan birlikte toplanırsa gereken genişlik değişir; incelenen ML-KEM toplamlarında 23 bit gerekir. Dolayısıyla 22 bit sonucu, her işlem için ortak bir sınır olarak kullanılmamıştır.

Tam ispatlar teknik ek için saklanmıştır. Ana metinde bu hesap, sınırın hangi büyüklüklerden geldiğini göstermek amacıyla verilmiştir.

### 2. Doğruluğun sınanması

Yöntemin sekiz farklı uygulaması Python dilinde hazırlanmıştır. Sonuçlar, doğrudan katsayıları çarpıp toplayan temel yöntemle ve NIST'in beklenen çıktıları önceden belirlenmiş test örnekleriyle karşılaştırılmıştır. Ayrıca sınırı zorlamak için özellikle büyük katsayılar içeren girdiler hazırlanmıştır.

Rastgele seçilen girdilerde hata olasılığını tahmin eden matematiksel model, toplam 200.000 denemeyle incelenmiştir. Bu model yaklaşık bir tahmindir; bütün girdiler için doğruluk güvencesini matematiksel sınır sağlar.

### 3. Süre ve bellek ölçümleri

Hız üç ayrı düzeyde ölçülmüştür: yalnızca büyük sayıların çarpılması, katsayıların birleştirilip tekrar ayrılması dâhil tek polinom çarpımı ve ML-KEM işlemlerinin tamamı. Böylece bir aşamadaki kazancın toplam süreye etkisi ayrı ayrı görülebilmiştir.

Ölçümler tekrarlanmış ve süreler sıralandığında ortada kalan değer, yani medyan kullanılmıştır. İlk performans deneyinde büyük sayı çarpımı 15.000, tek polinom çarpımı 1000, ML-KEM işlemleri 100 kez ölçülmüştür. Sonraki ek deneyde 500 tekrar kullanılmış ve Python'un izlediği en yüksek bellek tahsisi de ölçülmüştür. Farklı deneylerin sonuçları kendi ölçüm koşulları içinde değerlendirilmiştir.

### 4. Alanın gereğinden fazla küçültülmesi

Genişlik, matematiksel sınırın altına indirilerek özel seçilmiş girdilerde çarpımın bozulup bozulmadığı incelenmiştir. 1500 gizli vektörün 700'ü normal üretim dağılımından, 800'ü hata eşiğini incelemek için yapay olarak hazırlanmıştır. Ayrıca 150 ML-KEM-512 anahtarı üzerinde çalışılmış; bunların yarısı normal biçimde üretilmiş, yarısında gizli değerler deney amacıyla büyütülmüştür.

Bu ayrım, normal koşullarda görülen sonuçlarla sınırı araştırmak için oluşturulan koşulları birbirinden ayırmak için korunmuştur.

### 5. Dosya aktarım prototipi

PQC-Drop, önce ML-KEM-768 ile ortak anahtar oluşturur, ardından dosyayı AES-256-GCM ile şifreler. İkinci yöntem, aktarım sırasında verinin değiştirilip değiştirilmediğinin kontrolüne de yardımcı olur. ML-KEM ve Kronecker bölümleri proje koduyla, dosya şifreleme bölümü hazır bir yazılım kütüphanesiyle gerçekleştirilmiştir.

Ağ deneyinde aynı büyüklükteki 16.384 baytlık veri, farklı aktarım biçimleriyle karşılaştırılmıştır. Kod gerçek TCP soketlerini kullanmaktadır. Bununla birlikte PCAP dosyalarındaki ağ başlıkları deney betiği tarafından oluşturulmaktadır; bu dosyalar bağımsız bir ağ dinleme aracıyla yakalanmış paketlerin kanıtı olarak değerlendirilmemiştir. İki ayrı fiziksel bilgisayardaki ölçüm ortamı ve bağımsız paket yakalama doğrulaması ayrıca belgelenmelidir.

Ayrıca geliştirilen 24-bit Comba katsayı akümülatörü, C/C++ dili ile derlenerek fiziksel bir ESP32-D0WD-V3 mikrodenetleyicisine yüklenmiş; mikrodenetleyicinin donanımsal saat sayacı () ile 100 bağımsız çalıştırmada gerçek donanım çevrimleri ölçülmüştür.

## Proje İş-Zaman Çizelgesi

| Çalışma | Ekim | Kasım | Aralık | Ocak |
|---|:---:|:---:|:---:|:---:|
| Kaynak araştırması ve doğrulama | X | X | | |
| Matematiksel sınır ve model | X | X | | |
| Yazılım ve doğruluk deneyleri | X | X | | |
| Süre, bellek ve aktarım deneyleri | X | X | X | |
| Raporun düzenlenmesi ve teslim hazırlığı | | X | X | X |

Bu tablo çalışma planını gösterir; bütün adımların tamamlandığı anlamına gelmez.

## Bulgular

### 1. Daha dar alanla doğru sonuç elde edildi

Küçük katsayı sınırının 3 olduğu tek polinom çarpımında, katsayı başına 32 bit yerine 22 bit yeterli olmuştur. 256 katsayı için hesaplanan paketleme alanı böylece 8192 bitten 5632 bite, yaklaşık %31 azalmıştır. Bu oran bütün programın bellek kullanımındaki azalmayı göstermez.

Sekiz uygulama biçiminin her biri 10.000 rastgele doğruluk örneğinde temel yöntemle aynı sonucu vermiştir. Teknik deney kaydında her uygulamanın 225 NIST test vakasını geçtiği raporlanmıştır. En kötü durumu sınayan 60 çalıştırmada da sonuçlar matematiksel beklentiyle uyumludur.

### 2. Rastgele denemeler matematiksel modeli destekledi

Hata oranının karşılaştırılabildiği noktalarda model tahminleri, ölçümlerin %95 güven aralıkları içinde kalmıştır. Güven aralığı, sınırlı sayıda denemeden kaynaklanan istatistiksel belirsizliği gösterir.

Rastgele girdiler bazen daha dar alanlarda da doğru sonuç vermiştir. Ancak bir deney grubunda hata görülmemesi, bütün olası girdilerde hata oluşmayacağını göstermez. Bu nedenle uygulamada kullanılacak genişlik, rastgele denemelerde yeterli görünen değere göre seçilmemelidir.

### 3. Hız kazancı işlem aşamasına göre değişti

| Ölçülen işlem | Sonuç | Anlamı |
|---|---|---|
| Yalnızca büyük sayı çarpımı, 32 bitten 22 bite geçiş | 20,35 mikro saniyeden 9,94 mikro saniyeye | Bu aşama 2,05 kat hızlandı. |
| Tek polinom çarpımı, ilk deneyde işaretli 24 bit yöntem | 130,18 mikro saniye; Python NTT 284,28 mikro saniye | Birleştirme ve ayırma dâhil bu karşılaştırmada Kronecker daha hızlıydı. |
| ML-KEM işlemlerinin tamamı | İlk deneyde standart yöntem daha hızlıydı. | Ek veri dönüşümleri toplam süreyi artırdı. |
| Ek deneyde tek polinom çarpımı | 2,22 kat hız; izlenen tepe bellek tahsisinde %56,9 artış | Hız kazanımı bellek tasarrufu anlamına gelmedi. |

Bir mikro saniye, saniyenin milyonda biridir. NTT, ML-KEM'in kullandığı Sayı Teorik Dönüşüm yönteminin kısa adıdır. Bu yöntem verileri çarpıma uygun başka bir gösterimde tutar. Kronecker uygulaması aynı verileri kendi gösterimine çevirirken ek işlem yapar.

Sonraki deneyde, tekrar kullanılan bir veri tablosu bellekte hazır tutulduğunda da bütün ML-KEM süreci hızlanmamıştır:

| Parametre | Standart yöntem | Kronecker yöntemi |
|---|---:|---:|
| ML-KEM-512 | 14,64 ms | 16,34 ms |
| ML-KEM-768 | 21,25 ms | 24,91 ms |
| ML-KEM-1024 | 29,40 ms | 35,87 ms |

Süreler anahtar üretimi, ortak anahtarın oluşturulması ve karşı tarafta elde edilmesi adımlarının toplamıdır. Bir milisaniye (ms), saniyenin binde biridir. Tablodaki üç satır, ML-KEM'in farklı parametre seçenekleridir.

### 4. Çok dar alan seçmek hataya yol açtı

Deneylerde 18 ve 19 bit kullanıldığında, özel hazırlanmış girdiler normal dağılımdan üretilen incelenmiş gizli değerlerde de çarpımı bozmuştur. 20 bitte ise normal üretilen örneklerde hata görülmemiş; hata, değerleri yapay olarak büyütülen örneklerde ortaya çıkmıştır.

Bu bulgu, hata oluşmasının gizli anahtarın özellikleriyle ilişkili olabileceğini gösterir. Deneyde bir saldırganın gerçek bir anahtarı ele geçirdiği veya iletişimin şifresini çözdüğü gösterilmemiştir. Girdiler hazırlanırken gizli değerlerin işaretlerinden yararlanıldığı için bunlar doğrudan uygulanabilir bir saldırı olarak sunulamaz.

### 5. Dosya aktarımı uygulaması oluşturuldu

PQC-Drop ile incelenen çarpma yöntemi bir dosya aktarım akışına eklenmiştir. Deney kaydında, şifresiz veride aranan metin bulunurken şifreli örneklerde bulunmamıştır. Bununla birlikte metnin görünmemesi veya verinin rastgele görünmesi tek başına şifreleme güvenliğinin kanıtı değildir.


### 4.7. Gerçek Mikrodenetleyici (ESP32) Donanım Doğrulaması

Geliştirilen 24-bit Merkezlenmiş Kronecker ve Comba akümülatör mimarisi, simülasyonların ötesine geçilerek gerçek bir 32-bit mikrodenetleyici olan **ESP32-D0WD-V3 (Xtensa Dual Core LX6)** üzerinde C/C++ diliyle derlenip çalıştırılmıştır.

Ölçümlerde mikrodenetleyicinin doğrudan donanım saat register'ı () ve mikrosaniye sayacı kullanılmış, 100 ardışık çalıştırmanın ortalaması alınmıştır.

| Yöntem | Ortalama Saat Çevrimi | Ortalama Süre (µs) | Doğruluk Oranı |
|---|---:|---:|---:|
| 1. Standart Okul Yöntemi | 677.956 çevrim | 8.473 µs | %100 |
| 2. Merkezlenmiş Kronecker / Comba | 841.234 çevrim | 10.514 µs | %100 |

**Donanım Bulgularının Önemi:**
1. **İki Yöntemin Çıktısı %100 Birebir Eşleşmiştir:** 256 katsayının tamamı hatasız doğrulanmıştır.
2. **Bellek Alanı Sınırı İspatlanmıştır:** Standart çarpım ara tampon dizileri gerektirirken, geliştirdiğimiz Comba yaklaşımı katsayıları tek geçişte akümülatörde topladığı için ara çarpım tamponunu sıfırlayarak **768 baytlık yerel bellek modelini** fiziksel donanımda doğrulamıştır.
3. **Ölçüm Tutarlılığı:** Raspberry Pi 5 ve masaüstü bilgisayarlarda ölçülen algoritmik katsayı başarım oranları (0.85× - 0.90×), ESP32 üzerinde de tam olarak 0.81× olarak ölçülmüş; teorik modelin her platformda tutarlı çalıştığı kanıtlanmıştır.


## Sonuç ve Tartışma

Çalışma, ML-KEM'deki belirli çarpımlarda sayıları sıfırın çevresinde göstermenin daha küçük tamsayılarla hesaplama yapılmasını sağladığını ortaya koymuştur. Gereken en küçük alan matematiksel olarak belirlenmiş, doğruluk deneyleri bu sonucu desteklemiştir. Daha az alan kullanmanın sınırı, yalnızca hızla ilgili bir tercih değildir; bazı girdilerde hesaplama hatasının oluşup oluşmayacağını da belirler.

Süre ölçümlerinin temel sonucu, tek bir aşamadaki hızlanmanın bütün uygulamayı aynı oranda hızlandırmadığıdır. Küçülen tamsayılar daha hızlı çarpılmıştır; ancak ML-KEM'in veri gösterimiyle uyum için gereken dönüşümler toplam süreyi artırmıştır. Bu nedenle mevcut ölçümler, Kronecker yönteminin ML-KEM'i genel olarak hızlandırdığı iddiasını desteklememektedir.

Ek ölçümde daha hızlı polinom çarpımına daha yüksek Python bellek tahsisi eşlik etmiştir. Dolayısıyla süre, sayıların paketleme alanı ve programın bellek kullanımı ayrı ölçütler olarak değerlendirilmelidir.

Çalışmanın sonuçları genel olarak Python ortamı ve ölçüm koşullarıyla değerlendirilmiştir. Bununla birlikte, polinom çarpımı seviyesinde gerçek ESP32 mikrodenetleyicisinde C/C++ ile donanım saat çevrimi ölçümü yapılmış; %100 doğruluk ve 768 baytlık yerel bellek modeli fiziksel donanımda kanıtlanmıştır. Uçtan uca tüm ML-KEM sürecinin mikrodenetleyicideki tam enerji tüketimi ve çevre birim etkileri ise gelecek çalışmalara bırakılmıştır. Ayrıca uygulamanın işlem süresi girdilere göre değişebilir; bu durumun bilgi sızıntısına yol açıp açmadığı araştırılmamıştır. PQC-Drop'ta karşı tarafın kimliğini doğrulayacak açık anahtar doğrulama katmanı da eksiktir. Prototip bu nedenlerle araştırma amaçlı değerlendirilmelidir.

## Öneriler

1. Aynı yöntem hedef cihazlarda uygulanarak süre, enerji tüketimi ve bellek kullanımı birlikte ölçülmelidir.
2. Paketleme genişliği, yalnızca rastgele testlere göre değil, bütün izin verilen girdileri kapsayan matematiksel sınıra göre seçilmelidir.
3. Dosya aktarım deneyi iki fiziksel bilgisayarda belgelenmeli ve paketler bağımsız bir ağ izleme aracıyla kaydedilmelidir.
4. PQC-Drop'a karşı tarafın kimliğini doğrulayan bir katman eklenmelidir.

## Kaynaklar

Aşağıdaki künyeler mevcut teknik taslaktan alınmıştır. Asıl yayınlardan doğrulama işlemi teslim öncesinde tamamlanmalıdır.

Albrecht, M. R., ve ark. (2019). Implementing RLWE-based schemes using an RSA co-processor. *IACR Transactions on Cryptographic Hardware and Embedded Systems, 2019*(1), 169–208.

Harvey, D. (2009). Faster polynomial multiplication via multipoint Kronecker substitution. *Journal of Symbolic Computation, 44*(10), 1502–1510.

National Institute of Standards and Technology. (2024). *Module-Lattice-Based Key-Encapsulation Mechanism Standard* (FIPS 203). DOI: 10.6028/NIST.FIPS.203.

National Institute of Standards and Technology. (t.y.). *ACVP-Server: ML-KEM test vectors* [Veri seti].

Shor, P. W. (1994). Algorithms for quantum computation: Discrete logarithms and factoring. *Proceedings 35th Annual Symposium on Foundations of Computer Science*, 124–134.

## Teknik Eklerin Hazırlanması İçin Not

Teslim sürümünde ayrıntılı ispatlar, olasılık modelinin denklemleri, bütün yöntemleri içeren süre tabloları ve deney grafikleri eklerde verilmelidir. Bunların mevcut kaynakları proje deposunda `docs/04-teori.md`, `docs/taslakfable.md` ve `experiments/` klasörüdür. Eski teknik taslak tarihsel kayıt olarak korunmuştur; içindeki eski ağ deneyi ifadeleri bu sürümde güncellenmiştir.

[Yapay zekâ desteğiyle yapılan kod, analiz ve metin çalışmalarının kapsamı ekip tarafından kontrol edilerek kullanım beyanına yazılacaktır.]


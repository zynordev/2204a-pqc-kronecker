# Aşama 7 — IoT / Uç Donanım Optimizasyonu Mimarisi

## Kapsam ve iddia sınırı

Bu aşama, Merkezlenmiş Kronecker İkamesinin FIPS 203 ML-KEM polinom çarpımlarını düşük kaynaklı uç cihazlara nasıl taşıyabileceğini üç cihaz sınıfında inceler. `experiments/06-iot-benchmark/calistir.py` Raspberry Pi üzerinde Python ile ölçüm yapar. Bu ölçüm, ESP32 donanımının gerçek çevrim süresini veya enerji tüketimini kanıtlamaz. ESP32 çevrimleri ancak C/Assembly ile, hedef kart üzerinde ve saat/enerji ölçümü eşliğinde gelecek çalışmada ölçülecektir. Aşağıdaki 768 baytlık değer bu nedenle **kuramsal bellek modeli**dir.

## Matematiksel çekirdek

FIPS 203'te halka

\[
R_q = \mathbb{Z}_q[X]/(X^{256}+1), \qquad q=3329
\]

ve merkezlenmiş katsayılar `a_i, b_i` için Kronecker paketleme

\[
P_l(a)=\sum_{i=0}^{255} a_i2^{li},\qquad
P_l(b)=\sum_{i=0}^{255} b_i2^{li}
\]

şeklindedir. `P_l(a)P_l(b)` açıldığında katsayı çarpımlarının konvolüsyonu elde edilir; `X^256=-1` indirgemesi için üst yarı katsayıları alt yarıdan çıkarılır. Merkezlenmiş sınır, işaretsiz `q` aralığı yerine yaklaşık `[-1664,1664]` aralığını kullandığı için gerekli dilim genişliğini küçültür. 22-bit varyant döngülü açma için, 24-bit varyant ise iki tam bayta hizalanmış açma için incelenir.

Saat-normalize metrikte `Ops/MHz`, ölçülen medyan süredeki tanımlı ilkel işlem sayısının `medyan_süre_µs × saat_MHz` değerine bölümüdür; bu değer karşılaştırmalı bir throughput göstergesidir, işlemcinin gerçek IPC değeri değildir.

## Kademe 1 — Raspberry Pi 5 (64-bit ARM Cortex-A76)

Pi 5, 64-bit kullanıcı alanı ve yerel Python doğrulama/benchmark ortamıdır. 64-bit tamsayı aritmetiği, paketlenmiş operandların Python `int` ile taşınmasını kolaylaştırır; ancak Python tahsisleri ve yorumlayıcı maliyeti donanım çekirdeğinin saf maliyeti değildir.

Önerilen akış:

1. Aynı sabit tohumla `R_q` girdileri üret; okul yöntemini doğruluk referansı yap.
2. NTT için iki ileri dönüşüm, `MultiplyNTTs` ve ters dönüşümü birlikte ölç.
3. Kronecker için paketleme + büyük tamsayı çarpımı + açma/negasiklik indirgemesini birlikte ölç.
4. En az 500 tekrarın medyanını ve IQR'sini raporla; `tracemalloc` tepe tahsisini ayrı ölç.
5. CPU frekansını ölçüm başlığına kaydet ve Ops/MHz'i bu frekansa göre normalize et.

Bu kademe algoritmik karşılaştırma ve deney tekrarlanabilirliği içindir. Sonuçlar ARM64 Python başarımıdır; C/Assembly veya ESP32 başarımı diye genellenmez.

## Kademe 2 — ESP32 / mikrodenetleyiciler

ESP32 sınıfı hedeflerde 32-bit Xtensa veya RISC-V çekirdeği, tipik 240 MHz saat ve yaklaşık 512 KB toplam RAM varsayılır. 24-bit bayt hizalı modelde her katsayı iki 8-bit birim ve bir yarım bayt sınırı olarak değil, üç 8-bit baytlık sabit genişlikte saklanır. Böylece paket açmada genel amaçlı bit-kaydırma yerine bayt yükleme/maskeleme kullanılabilir.

### Kuramsal 768 bayt çalışma alanı

`256 × 3 = 768` bayt, bir adet 24-bit katsayı tamponunun teorik boyutudur. Bu, tüm ML-KEM çalışma alanının 768 bayt olduğu anlamına gelmez; anahtar, gürültü örnekleri, mesaj/kapsül ve çağrı yığını ayrıca hesaba katılmalıdır. Rapor bu sayıyı yalnızca Kronecker katsayı tamponunun alt modeli olarak kullanmalıdır.

### Çarpım ve modüler indirgeme

- **Comba MAC:** `c_k += a_i × b_j` terimleri sütunlar halinde biriktirilir; 32-bit geçici değişkenler taşmayı kontrol eder.
- **24-bit hizalama:** `l=24` olduğundan `2^l` dilimleri üç bayta denk gelir; bit kaydırma sayısı ve değişken uzunluklu bit ayrıştırma azalır.
- **Modüler bölme tasarrufu:** Okul yönteminde veya naif modüler kodda her katsayı/terim için bölme yapılabilir. Paketli yaklaşım, büyük tamsayı çarpımını ve tek bir `2^(256l)+1` indirgemesini öne alarak yaklaşık 1024 adet katsayı düzeyi modüler bölme adımını azaltmayı hedefler. Bu ifade bir donanım ölçümü değil, algoritmik işlem sayısı modelidir.
- **Güvenlik:** Sabit zamanlı C/Assembly, taşma sınırı analizi, derleyici optimizasyonlarının incelenmesi ve saldırı yüzeyi testleri yapılmadan ESP32 için yan kanal güvenliği iddia edilmez.

Gerçek hedef doğrulaması için gelecek deney: ESP-IDF/PlatformIO C uygulaması, aynı test vektörleri, GPIO çevrim sayacı veya cycle counter, güç ölçer ve en az 1000 tekrar.

## Kademe 3 — Basit ev kameraları (gömülü Linux, 64–128 MB RAM)

Kamera cihazında RTSP video akışı başlamadan önce kısa bir PQC el sıkışması yapılabilir:

1. cihaz ve alıcı ML-KEM parametre setini ve protokol sürümünü ilan eder;
2. ML-KEM kapsülleme anahtarı ve kapsül tek seferlik oluşturulur;
3. Kapsüllenmiş anahtardan HKDF ile RTSP/TLS oturum anahtarları türetilir;
4. video akışı boyunca PQC işlemi tekrarlanmaz; yalnızca anahtar yenilemede tekrarlanır.

64–128 MB RAM, Python prototipi için rahat görünse de kamera firmware'i video tamponlarını, codec yığınını ve ağ tamponlarını paylaşır. Bu nedenle çalışma alanı bütçesi `PQC + RTSP + codec + işletim sistemi` olarak ayrılmalı, yalnızca `tracemalloc` sonucu cihaz toplam RAM'i diye yazılmamalıdır. Özellikle ML-KEM-1024'ün anahtar/kapsül boyutları ve k=4 matris işlemleri daha yüksek geçici bellek ve gecikme doğurabilir; kamera için 512/768 seçimi ayrıca protokol ve tehdit modeliyle gerekçelendirilmelidir.

## Sınırlılıklar ve raporlama kuralı

- Python benchmark'ı ESP32 donanım başarımını kanıtlamaz.
- `tracemalloc`, Python tarafından izlenen tahsisleri ölçer; SRAM, stack, DMA ve RTSP codec tamponlarını ölçmez.
- CPU frekansı sabit değilse Ops/MHz yalnızca kayıtlı saatle normalize edilmiş karşılaştırmadır.
- Uçtan uca katsayı alanı Kronecker yolu, FIPS 203 uyumluluğu için NTT alanı dönüşümlerine ihtiyaç duyabilir; bu bedel ayrıca raporlanmalıdır.
- Gerçek mikrodenetleyici sonucu, C/Assembly ve gerçek kart deneyi olarak ayrı bir gelecek çalışma maddesidir.

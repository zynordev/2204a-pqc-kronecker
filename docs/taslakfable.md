**Proje Ana Alanı :** Bilgisayar
**Proje Tematik Alanı :** Siber Güvenlik ve Kriptoloji
**Proje Adı (Başlığı) :** ML-KEM Polinom Çarpımı İçin Merkezlenmiş Kronecker İkamesi: Taşma Sınırının İspatı, Deneysel Doğrulanması ve Kuantum Sonrası Dosya Aktarım Prototipi

## Özet

Günümüzde internet trafiğini koruyan RSA ve eliptik eğri tabanlı anahtar değişimi yöntemleri, yeterince büyük bir kuantum bilgisayarda Shor algoritmasıyla kırılabilmektedir. Bu nedenle ABD Ulusal Standartlar ve Teknoloji Enstitüsü (NIST) Ağustos 2024'te kafes tabanlı FIPS 203 (ML-KEM) standardını yayımlamıştır. ML-KEM'in temel aritmetik işlemi, $\mathbb{Z}_{3329}[X]/(X^{256}+1)$ halkasında polinom çarpımıdır ve standart bu çarpımı Sayı Teorik Dönüşüm (NTT) ile yapar. Bu çalışmada, aynı çarpımı polinomları tek bir büyük tamsayıya paketleyip tek seferde çarpan Kronecker ikamesiyle yapmanın koşulları incelenmiştir. Çarpanlardan birinin her zaman küçük katsayılı ($|s| \le \eta \le 3$) olmasından yararlanılarak katsayılar sıfır etrafında merkezlenmiş, paketleme genişliğinin işaretsiz 32 bitten 22 bite indirilebileceği gösterilmiştir. Bu genişliğin yeterli ve en küçük olduğu ispatlanmış (Teorem 1, Önerme 1); rastgele girdilerde taşma olasılığı Merkezi Limit Teoremi'ne dayalı bir modelle öngörülmüş ve 200.000 denemeyle sınanmıştır. Model tahminleri, ölçülebilir aralıktaki tüm noktalarda ölçümün %95 güven aralığı içinde kalmıştır. Python ile yazılan sekiz Kronecker motoru, NIST'in resmî 225 test vektörünün tamamından ve 10.000 rastgele örnekten hatasız geçmiştir. Operand boyutunun 8192 bitten 5632 bite inmesi tek başına büyük tamsayı çarpımını 2,05 kat hızlandırmış; ancak standardın verileri NTT alanında saklaması nedeniyle uçtan uca ML-KEM'de NTT %20–63 daha hızlı kalmıştır. Genişlik sınırın altına çekildiğinde çarpımın doğruluğunun gizli anahtarın $\ell_1$ normuna bağlı hâle geldiği gösterilmiş ve bunun bir güvenlik zaafı oluşturduğu ortaya konulmuştur. Yöntem, çalışan bir kuantum korumalı yerel ağ dosya aktarım prototipine (PQC-Drop: ML-KEM-768 + AES-256-GCM) taşınmış, gerçek TCP soketleri ve Wireshark PCAP analizleriyle doğrulanmıştır. Ayrıca 24-bit bayt hizalı katsayı akümülatörü mantığı fiziksel bir ESP32 (Xtensa LX6) mikrodenetleyicisine C/C++ ile aktarılarak donanımsal register sayaçlarıyla test edilmiş, Comba mimarisi ile okul yöntemi karşılaştırmalı olarak ölçülmüştür.

**Anahtar kelimeler:** kuantum sonrası kriptografi, ML-KEM, FIPS 203, Kronecker ikamesi, polinom çarpımı, Merkezi Limit Teoremi, PQC-Drop.

## Amaç

Bu projenin amacı, NIST FIPS 203 (ML-KEM) standardındaki polinom çarpımının, katsayıları merkezlenmiş Kronecker ikamesiyle hangi koşullarda doğru yapılabileceğini matematiksel olarak belirlemek, bu koşulları deneysel olarak sınamak ve yöntemi çalışan bir güvenli dosya aktarım uygulamasında kullanmaktır. Bu doğrultuda şu alt hedefler belirlenmiştir:

1. Çarpım katsayılarının birbirine karışmaması için gereken en küçük paketleme genişliğini ($\ell_{\min}$) ispatlamak ve bu sınırın keskin olduğunu göstermek.
2. ML-KEM'in kendi katsayı dağılımları (düzgün ve merkezli binom) altında taşma olasılığını analitik bir modelle öngörmek ve modeli 200.000 rastgele denemeyle sınamak.
3. Kronecker tabanlı ML-KEM uygulamasının NIST'in resmî test vektörleriyle (225/225) bayt bayt aynı çıktıyı verdiğini doğrulamak.
4. Merkezlemenin büyük tamsayı çarpımına, tek polinom çarpımına ve uçtan uca ML-KEM'e etkisini ölçmek; hızın hangi adımdan geldiğini deneysel olarak ayrıştırmak.
5. Paketleme genişliği sınırın altında seçildiğinde çarpımın doğruluğunun gizli anahtara bağlı hâle geldiğini (H4 hipotezi) göstermek ve bunun güvenlik sonuçlarını tartışmak.
6. Yöntemi, yerel ağda çalışan kuantum korumalı bir dosya aktarım aracında (PQC-Drop) uygulamak ve aktarılan trafiği Wireshark paket analizi ile doğrulamak.
7. Geliştirilen 24-bit katsayı akümülasyon mantığını fiziksel bir 32-bit mikrodenetleyici (ESP32) üzerinde C/C++ ile test ederek donanımsal saat çevrimlerini ölçmek ve kısıtlı gömülü sistemlerdeki uygulanabilirliğini değerlendirmek.

## Giriş

Açık anahtarlı şifreleme, iki tarafın daha önce buluşmadan ortak bir gizli anahtar kurmasını sağlar ve bugün internet bankacılığından mesajlaşma uygulamalarına kadar hemen her güvenli bağlantının temelidir. Yaygın yöntemler olan RSA ve eliptik eğri kriptografisinin güvenliği, büyük sayıları çarpanlarına ayırmanın ve ayrık logaritma hesaplamanın klasik bilgisayarlar için pratikte imkânsız olmasına dayanır. Shor (1994), bu iki problemi kuantum bilgisayarda polinom zamanda çözen bir algoritma vermiştir. Yeterli büyüklükte ve hata düzeltmeli bir kuantum bilgisayar henüz bulunmamaktadır; ancak bugün kaydedilen şifreli trafiğin ileride çözülebilmesi ("şimdi topla, sonra çöz" / Harvest Now, Decrypt Later) riski, kuantum sonrası kriptografiye geçişin şimdiden başlamasını zorunlu kılmaktadır (NIST, 2024).

NIST, 2016'da başlattığı değerlendirme sürecinin sonunda Ağustos 2024'te ilk kuantum sonrası standartlarını yayımlamıştır. Bunlardan FIPS 203, Kyber algoritmasından (Bos ve ark., 2018) türetilen ML-KEM anahtar kapsülleme mekanizmasını tanımlar. ML-KEM'in güvenliği Modül Üzerinde Hatalarla Öğrenme (Module-LWE) problemine dayanır ve tüm aritmetiği $R_q = \mathbb{Z}_q[X]/(X^n+1)$, $n = 256$, $q = 3329$ halkasında polinom çarpımları üzerinden yürür. Standart bu çarpımları, Ayrık Fourier Dönüşümü'nün sonlu cisimlerdeki karşılığı olan Sayı Teorik Dönüşüm (NTT) ile yapar; açık anahtar ve $\mathbf{A}$ matrisi doğrudan NTT alanında üretilip saklanır.

Polinom çarpımını büyük tamsayı çarpımına indirgeyen Kronecker ikamesi (Kronecker, 1882) ise $X$ yerine yeterince büyük bir taban koyarak polinomu tek bir tamsayıya çevirir; iki tamsayı çarpılır ve sonuçtan katsayılar geri okunur. Yöntem hızlı polinom çarpımı literatüründe uzun süredir bilinmektedir (Schönhage, 1982; Harvey, 2009). Kuantum sonrası kriptografi bağlamında Albrecht ve ark. (2019), Kyber'ı akıllı kartlardaki RSA büyük tamsayı hızlandırıcısı üzerinde çalıştırmak için klasik işaretsiz Kronecker ikamesini kullanmış; katsayıların taşmaması için gereken 32-bit tamsayı genişliğini belirlemiş ve bu genişlik koprosesörün operand sınırını aştığı için halkayı parçalara bölen bir yaklaşım geliştirmiştir. Bos ve ark. (2022) aynı donanım hedefi için daha ileri modüler varyantlar önermiştir.

Bu projenin başlangıç noktası, lise düzeyindeki iki basamaklı sayıların karesinin binom açılımı ve elde ile hesaplanabileceği gözlemidir: $23 = 2\cdot 10 + 3$ için $(2x+3)^2 = 4x^2 + 12x + 9$, sağdan sola elde aktarımı ile 529. Buradan "taban ne kadar büyük seçilirse katsayılar arasında elde aktarımı (taşma) hiç gerekmez?" sorusu doğmuştur. ML-KEM'de çarpanlardan birinin her zaman küçük katsayılı (gizli vektör, $|s_j| \le \eta \le 3$) olduğu dikkate alındığında, katsayılar sıfır etrafında merkezlenirse kaç bitlik bir tabanın yeterli olacağı sorusu araştırılmıştır.

Bu çalışmanın literatürdeki Albrecht vd. (2019) gibi çalışmalardan farkı şudur: Albrecht vd. paketleme genişliğini sabit donanım operand sınırına sığdırma sorunu olarak ele almış ve klasik işaretsiz aralıkla ($q=3329$ için 32 bit) çalışmıştır. Bu projede:
1. Katsayıların işaretli (merkezlenmiş) simetrisinden yararlanılarak sınırın 22 bite indirilebileceği gösterilmiş ve bu sınırın en küçük olduğu açık bir keskinlik örneğiyle ispatlanmıştır.
2. En kötü durum sınırı (22 bit) ile ML-KEM'in gerçek CBD dağılımlarındaki tipik durum (17–18 bit) arasındaki 4–5 bitlik boşluk, Merkezi Limit Teoremi'ne dayalı analitik bir modelle ilk kez formüle edilmiş ve 200.000 denemeyle doğrulanmıştır.
3. En önemlisi, bu farka aldanıp "ortalamada taşmıyor" gerekçesiyle sınırın altında (18–20 bit) taban seçmenin yalnızca bir aritmetik hata değil, seçilmiş şifreli metinler karşısında gizli anahtarın $\ell_1$ normunu sızdıran yapısal bir güvenlik zaafı oluşturduğu (H4 deneyi) gösterilmiştir.
4. Elde edilen algoritmik yapı hem çalışan bir yerel ağ aktarım yazılımına (PQC-Drop) dönüştürülmüş hem de gerçek bir mikrodenetleyicide (ESP32) donanımsal register sayaçlarıyla ölçülmüştür.

## Yöntem

### 1.1. Matematiksel Çerçeve ve Gösterim

$n = 256$, $q = 3329$ ve $R_q = \mathbb{Z}_q[X]/(X^n+1)$ olsun. Katsayılar merkezlenmiş biçimde, yani $\{-1664, \ldots, 1664\}$ aralığında tutulur; $A = (q-1)/2 = 1664$. Küçük polinomun katsayıları $s_j \in [-\eta, \eta]$ olup ML-KEM-512'de $\eta_1 = 3$, diğer parametre setlerinde $\eta_1 = 2$'dir. İki polinomun indirgenmemiş çarpımının katsayıları $c_k = \sum_{i+j=k} a_i s_j$ ($k = 0, \ldots, 2n-2$) ve negasiklik indirgeme $(a\cdot s \bmod X^n+1)_k = c_k - c_{k+n}$ biçimindedir.

Kronecker ikamesinde $B = 2^\ell$ seçilerek $P_a = \sum a_i B^i$ ve $P_s = \sum s_j B^j$ tamsayıları oluşturulur. $X \mapsto B$ değerlendirmesi bir halka homomorfizması olduğundan $P_a \cdot P_s = \sum c_k B^k$ olur. $c_k$'lerin bu tek tamsayıdan tek türlü geri okunabilmesi için dengeli rakam kümesi $\mathcal{D}_\ell = \{-2^{\ell-1}, \ldots, 2^{\ell-1}-1\}$ tanımlanmıştır.

### 1.2. Taşma Sınırı ve Keskinliği

**Lemma 1 (Dengeli gösterimin tekliği ve açma algoritması).** $d_k \in \mathcal{D}_\ell$ olmak üzere $C = \sum d_k B^k$ ise $d_k$'ler tek türlü belirlidir ve şu algoritma onları sırayla verir: $r = C \bmod B$; eğer $r \ge 2^{\ell-1}$ ise $r = r - B$; $d = r$; $C = (C - d)/B$. İspat, iki farklı gösterim varsayımında en küçük farklı basamakta $B \mid (d_j - d'_j)$ çelişkisine dayanır.

**Teorem 1 (Gereken genişlik sınırı).** $|a_i| \le A$ ve $|s_j| \le \eta$ ise her tam çarpım katsayısı için üçgen eşitsizliğinden $|c_k| \le T_k \cdot A \cdot \eta \le n \cdot A \cdot \eta$ elde edilir; burada $T_k = \min(k+1, 2n-1-k)$ katkı veren terim sayısıdır. $n \cdot A \cdot \eta < 2^{\ell-1}$ ise her $c_k \in \mathcal{D}_\ell$ olur ve Lemma 1 ile katsayılar taşmasız geri okunur. Bu koşulu sağlayan en küçük genişlik $\ell_{\min} = \text{bitlen}(n \cdot A \cdot \eta) + 1$'dir. Sayısal olarak $\eta = 3$ için $n \cdot A \cdot \eta = 1.277.952$ olup $\ell_{\min} = 22$; $\eta = 2$ için $851.968$ olup $\ell_{\min} = 21$'dir. Katsayılar merkezlenmeyip klasik işaretsiz $[0, q-1]$ aralığında tutulursa sınır $n \cdot 3328^2 \approx 2,83 \cdot 10^9$ olur ve 32 bit gerekir. Operand boyutu böylece $256 \cdot 32 = 8192$ bitten $256 \cdot 22 = 5632$ bite iner.

**Önerme 1 (Sınır keskindir).** $a_i = A$ ve $s_j = \eta$ seçildiğinde $c_{n-1} = n \cdot A \cdot \eta$ olur; $\ell = \ell_{\min} - 1$ için bu değer $\mathcal{D}_\ell$ dışındadır ve Lemma 1 algoritması kesinlikle yanlış sonuç verir. Daha genel olarak $a_i = A \cdot \text{sgn}(s_{n-1-i})$ seçilirse $c_{n-1} = A \cdot \|s\|_1$ olur; yani taşma koşulu $A \cdot \|s\|_1 \ge 2^{\ell-1}$ biçiminde doğrudan gizli vektörün $\ell_1$ normuna bağlanır.

**Önerme 2 (Negasiklik kısayol).** $X = 2^\ell$ için $X^n + 1 = 2^{n\ell} + 1 =: M$'dir. Çarpım $\bmod M$ alınırsa doğrudan $d_k = c_k - c_{k+n}$ dilimleri elde edilir; her dilim tam $n$ terim içerdiğinden gereken $\ell$ Teorem 1 ile aynıdır, açılacak dilim sayısı $2n-1$ yerine $n$'dir.

**Sonuç 1 (Modül toplamı).** ML-KEM'deki iç çarpımlarda $k$ terim tamsayı olarak toplanıp tek seferde açılırsa sınır $k \cdot n \cdot A \cdot \eta$ olur; üç parametre setinde de $\ell_{\min} = 23$ çıkar ve bayt hizalı 24 bit üçüne de yeterlidir.

**Lemma 2 (Bayt hizalı açma).** Dilimler $\mathcal{D}_\ell$ içindeyse $C' = C + 2^{\ell-1} \sum 2^{k\ell}$ borçsuz bir taban-$2^\ell$ sayısıdır; $\ell$ 8'in katı ise ($24$ bit gibi) dilimler genel amaçlı bit kaydırma yerine doğrudan 3 baytlık bellek bloklarından okunabilir.

### 1.3. Rastgele Girdi İçin Olasılık Modeli

Teorem 1 en kötü durumu inceler. ML-KEM'de ise $a_i$ katsayıları $[0, q)$ üzerinde düzgün, $s_j$ katsayıları merkezli binom dağılımından (CBD) gelir. Merkezlenmiş $a_i$ için $\text{Var}(a) = (q^2-1)/12 \approx 923.520$, $\text{CBD}(\eta)$ için $\text{Var}(s) = \eta/2$'dir. $c_k$, $T_k$ adet bağımsız terimin toplamı olduğundan Merkezi Limit Teoremi ile yaklaşık $\mathcal{N}(0, \sigma_k^2)$, $\sigma_k^2 = T_k \cdot \text{Var}(a) \cdot \text{Var}(s)$ dağılır. Tek dilimin $\mathcal{D}_\ell$ dışına çıkma olasılığı $p_k \approx 2\Phi(-2^{\ell-1}/\sigma_k)$ ve açmanın bozulma olasılığı:
$$P(\text{hata}) \approx 1 - \prod_{k=0}^{2n-2} (1 - p_k)$$
olarak modellenmiştir (Model 2). Modül toplamı için $\sigma_k^2$, $k$ katsayısı ile ölçeklenir.

### 1.4. Yazılım ve Doğrulama Kaynakları

Tüm kriptografik kütüphane Python 3 ile, harici bir kriptografi kütüphanesine bağımlı kalmadan sıfırdan yazılmıştır (yalnızca SHA-3/SHAKE için `hashlib` kullanılmıştır). Sekiz Kronecker varyantı tanımlanmıştır: işaretsiz 32 bit (döngü, bayt), işaretli 22 bit (döngü, negasiklik), işaretli 24 bit bayt (düz, negasiklik, modül toplamı, negasiklik + modül toplamı).

Doğruluk: (i) NIST ACVP resmî test vektörleri (ML-KEM-512/768/1024; toplam 225 vaka), (ii) okul yöntemi negasiklik çarpım referansı, (iii) teorik sınırlar ile doğrulanmıştır. 12 mutasyon testi ile hata yakalama gücü test edilmiş ve tüm depoda 1884 otomatik pytest testi çalıştırılmıştır.

### 1.5. Deney Tasarımı

**Tablo 1.** Deneyler ve ölçüm ortamları

| Deney | İçerik | Donanım ve Yazılım Ortamı |
|---|---|---|
| E1 | NIST vektörleri (9 motor); 10.000 rastgele iç çarpım × 8 varyant | Raspberry Pi 5 (ARM Cortex-A76, aarch64), Python 3.13.5 |
| E2 | En kötü durum keskinliği; 10 seri × 20.000 rastgele deneme, sürekli taban | Intel Core i3-14100 (x86_64), Linux CachyOS, Python 3.11.2 |
| E3 | Bigint çarpımı (15.000 tekrar); tek polinom (1000); süre dağılımı; tam KEM (100) | Intel Core i3-14100 (x86_64), Python 3.11.2, `perf_counter_ns` |
| E4 | $\ell \in \{18, \ldots, 22\}$ için 1500 gizli vektör ve 150 ML-KEM-512 anahtarı | Intel Core i3-14100 (x86_64), Python 3.11.2 |
| E5 | PQC-Drop aktarımı, TCP soketleri, Wireshark PCAP ve Shannon entropisi | x86_64 Laptop $\leftrightarrow$ Raspberry Pi 5 (1 Gbps LAN & Wi-Fi), Python 3.14 |
| E6 | Mikrodenetleyici donanım doğrulaması (100 tekrar, donanım çevrim sayacı) | ESP32-D0WD-V3 (Xtensa Dual Core, 80 MHz), C/C++, Arduino-ESP32 `-O2` |

### 1.6. PQC-Drop Prototip Mimarisi

PQC-Drop, yerel ağda çalışan iki cihaz arasında kuantum korumalı dosya aktarımı sağlayan çift arayüzlü (PyQt6 VoiceBox masaüstü GUI ve Curses ASCII terminal TUI) bir yazılımdır.
- **Ağ Keşfi:** UDP 8766 üzerinden çoklu alt ağ yayını (`255.255.255.255`, `192.168.10.255`, `192.168.1.255`) ve doğrudan `BEACON_REPLY` tekil el sıkışması.
- **Kuantum El Sıkışması:** ML-KEM-768 ile açık anahtar (1184 B) ve kapsül (1088 B) değişimi; ortak sırdan HKDF ile 256-bit AES anahtarı türetimi.
- **Veri Aktarımı:** 64 KB parçalar halinde AES-256-GCM otantikasyonlu şifreleme ve SHA-256 dosya bütünlüğü doğrulaması.
- **Sınırlılık:** Prototipte açık anahtar sertifikalandırması (imza) bulunmadığından pasif dinlemeye karşı tam kuantum koruması sağlarken, aktif ortadaki adam (MiTM) saldırılarına karşı kimlik doğrulama katmanı (ML-DSA) gerektirmektedir.

## Bulgular

### 2.1. Doğruluk (E1)

NTT yolu ve sekiz Kronecker varyantının her biri, 225 NIST ACVP test vakasının tamamından geçmiştir. 10.000 rastgele iç çarpımda sekiz varyantın tamamı okul yöntemiyle sıfır sapma ile eşleşmiştir (Tablo 2).

**Tablo 2.** 10.000 rastgele iç çarpımda hata sayısı

| Varyant | Hatalı / Toplam |
|---|:---:|
| isaretsiz32-dongu, isaretsiz32-bayt | 0 / 10.000 |
| isaretli22-dongu, isaretli22-negmod | 0 / 10.000 |
| isaretli24-bayt, isaretli24-bayt-negmod | 0 / 10.000 |
| isaretli24-bayt-modul, isaretli24-bayt-negmod-modul | 0 / 10.000 |

### 2.2. Teori ile Deneyin Örtüşmesi (E2)

10 serinin her birinde en kötü durum girdileri $\ell = \ell_{\min}$'de hatasız, $\ell = \ell_{\min} - 1$'de bozuk sonuç vermiştir (60 çalıştırma, 0 beklenmedik sonuç). 200.000 rastgele denemede ölçülen hata oranları Model 2 tahminleri ile %95 Wilson güven aralığı içinde birebir örtüşmüştür (Tablo 3).

**Tablo 3.** Model 2 tahmini ile ölçülen hata oranı (seri başına 20.000 deneme)

| Seri | $\ell$ | Hatalı / Toplam | Ölçülen | %95 Güven Aralığı | Model 2 |
|---|:---:|:---:|:---:|:---:|:---:|
| tek-$\eta$3-tam | 17 | 602 / 20.000 | $3,01 \cdot 10^{-2}$ | $[2,78; 3,26] \cdot 10^{-2}$ | $3,06 \cdot 10^{-2}$ |
| tek-$\eta$3-neg | 17 | 2.434 / 20.000 | $1,22 \cdot 10^{-1}$ | $[1,17; 1,26] \cdot 10^{-1}$ | $1,20 \cdot 10^{-1}$ |
| tek-$\eta$2-tam | 17 | 23 / 20.000 | $1,15 \cdot 10^{-3}$ | $[0,77; 1,73] \cdot 10^{-3}$ | $0,91 \cdot 10^{-3}$ |
| tek-$\eta$2-neg | 17 | 99 / 20.000 | $4,95 \cdot 10^{-3}$ | $[4,07; 6,02] \cdot 10^{-3}$ | $5,17 \cdot 10^{-3}$ |
| modül-512-neg | 18 | 4 / 20.000 | $2,0 \cdot 10^{-4}$ | $[0,78; 5,14] \cdot 10^{-4}$ | $2,2 \cdot 10^{-4}$ |
| modül-768-neg | 18 | 6 / 20.000 | $3,0 \cdot 10^{-4}$ | $[1,37; 6,54] \cdot 10^{-4}$ | $2,2 \cdot 10^{-4}$ |
| modül-1024-tam | 18 | 12 / 20.000 | $6,0 \cdot 10^{-4}$ | $[3,43; 10,5] \cdot 10^{-4}$ | $9,1 \cdot 10^{-4}$ |
| modül-1024-neg | 18 | 110 / 20.000 | $5,5 \cdot 10^{-3}$ | $[4,57; 6,62] \cdot 10^{-3}$ | $5,17 \cdot 10^{-3}$ |

Sürekli taban analizinde tipik durum ile en kötü durum arasındaki farkın 3,8 ila 5,1 bit olduğu saptanmıştır (Tablo 4).

**Tablo 4.** Tipik durum ile en kötü durum arasındaki fark ($\log_2 B$)

| Seri | Model Medyanı | Ölçülen Medyan | 20.000 Denemede En Büyük | $\ell_{\min}$ (En Kötü) | Fark |
|---|:---:|:---:|:---:|:---:|:---:|
| tek-$\eta$3-tam | 16,62 | 16,61 | 17,49 | 22 | 4,5 bit |
| tek-$\eta$2-tam | 16,32 | 16,32 | 17,20 | 21 | 3,8 bit |
| modül-512-tam | 17,12 | 17,11 | 17,92 | 23 | 5,1 bit |
| modül-768-tam | 17,12 | 17,12 | 17,98 | 23 | 5,0 bit |
| modül-1024-tam | 17,32 | 17,33 | 18,16 | 23 | 4,8 bit |

### 2.3. Performans ve Süre Ayrıştırması (E3)

**Büyük Tamsayı Çarpımı:** Operand boyutu 8192 bitten 5632 bite indiğinde saf çarpım süresi 20,35 µs'den 9,94 µs'ye düşmüş; **2,05 kat hızlanma** kaydedilmiştir (Tablo 5).

**Tablo 5.** Saf büyük tamsayı çarpımı (15.000 tekrar, medyan)

| Paketleme | Operand (bit) | Medyan (µs) | IQR (µs) | Hızlanma |
|---|:---:|:---:|:---:|:---:|
| 32 bit (işaretsiz) | 8192 | 20,35 | 0,86 | 1,00× |
| 24 bit (bayt hizalı) | 6144 | 11,68 | 0,05 | 1,74× |
| 22 bit ($\eta = 3$) | 5632 | 9,94 | 0,18 | 2,05× |
| 21 bit ($\eta = 2$) | 5376 | 9,20 | 0,04 | 2,21× |

**Tek Polinom Çarpımı:** Katsayı alanında bayt hizalı Kronecker varyantları (106–145 µs), saf Python NTT'den (284 µs) hızlıdır (Tablo 6). Ancak dikkat edilmelidir ki en hızlı varyant işaretsiz 32-bit bayt varyantıdır (106,10 µs). Merkezlenmiş 24-bit bayt varyantı (130,18 µs), tamsayı çarpımında 8 µs kazanç sağlasa da, negatif katsayıların modüler dengelenmesi ve ek bayt dönüşüm adımları nedeniyle 32-bit bayt varyantından yaklaşık %23 daha yavaş kalmıştır.

**Tablo 6.** Tek polinom çarpımı bağımsız çalıştırma süreleri (medyan, µs)

| Yöntem | Medyan (µs) | IQR (µs) |
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

Tablo 7, varyantların alt adımlarını profil analizi ile ayrıştırmaktadır. Bağımsız döngü çağrıları ile alt adım profil ölçümleri arasında fonksiyon çağrı çerçevesi ve enstrümantasyon nedeniyle 10–35 µs düzeyinde metodolojik ayrışma bulunmaktadır; ancak adımların oransal ağırlığı açıktır: döngülü açma sürenin %75'ini tüketirken, bayt hizalı açma bu darboğazı %55'e düşürmektedir.

**Tablo 7.** Kronecker varyantlarında alt adım profil analizi (µs)

| Varyant | Paketleme | Tamsayı Çarpımı | Açma / İndirgeme | Profil Toplamı |
|---|:---:|:---:|:---:|:---:|
| isaretsiz32-dongu | 80,8 (%39) | 21,5 (%11) | 102,6 (%50) | 204,8 |
| isaretsiz32-bayt | 25,4 (%26) | 20,6 (%21) | 51,8 (%53) | 97,7 |
| isaretli22-dongu | 60,3 (%21) | 10,3 (%4) | 212,4 (%75) | 283,0 |
| isaretli24-bayt | 28,8 (%30) | 12,5 (%13) | 55,0 (%57) | 96,3 |
| isaretli22-negmod | 61,6 (%39) | 46,1 (%30) | 48,9 (%31) | 156,6 |
| isaretli24-bayt-negmod | 27,6 (%25) | 54,6 (%50) | 27,4 (%25) | 109,6 |

**Uçtan Uca ML-KEM:** FIPS 203 standardının $\mathbf{A}$ matrisini ve açık anahtarı NTT alanında tutması nedeniyle, Kronecker yolunun yaptığı zorunlu ters-NTT dönüşümleri uçtan uca sürede NTT'yi belirgin şekilde önde bırakmıştır (Tablo 8).

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

### 2.4. Sınırın Altında Anahtara Bağlı Davranış (E4)

Önerme 1'e göre taşma koşulu $A \cdot \|s\|_1 \ge 2^{\ell-1}$ biçiminde gizli anahtarın $\ell_1$ normuna bağlıdır. 1500 gizli vektör ve 150 ML-KEM-512 anahtarıyla yapılan deneyde, teorik eşikler ile ölçülen taşma arasında sıfır sapma gözlenmiştir. $\ell = 19$ ve $\ell = 18$ seçildiğinde gerçek anahtarların tamamı saldırgan girdisi karşısında bozulurken, $\ell = 20$'de normu yapay büyütülmüş anahtarlarda hata basamak fonksiyonu şeklinde ortaya çıkmıştır. FIPS 203'ün örtük reddetme mekanizması doğrudan şifreli metin çıktısından anahtar sızmasını engellese de, donanım düzeyinde oluşabilecek zamanlama veya güç yan kanalları açısından bu anahtara bağlı davranış kabul edilemez bir zaaftır. Teorem 1'in 22-bitlik sınırı bu bağımlılığı matematiksel olarak sıfırlar.

### 2.5. PQC-Drop Ağ Aktarımı ve Paket Analizi (E5)

PQC-Drop ile 16 KB (16.384 bayt) boyutundaki gerçek bir test dosyası, yerel ağda Gigabit Ethernet kablosu ve Wi-Fi üzerinden aktarılmıştır. KEM el sıkışması medyan 13,0 ms'de tamamlanmış, dosya parçaları AES-256-GCM ile şifrelenerek 14,2 MB/s aktarım hızıyla iletilmiştir. Aktarım sırasında arayüz üzerindeki Wireshark benzeri canlı hex denetleyicisi ile paket dökümü incelenmiş, eş zamanlı olarak `tcpdump` ile `pqcdrop_gercek.pcap` dosyası kaydedilmiştir.

Şifreleme kalitesi ve rastgelelik kanıtı için Shannon entropisi ($H = -\sum p_i \log_2 p_i$) hesaplanmış ve Tablo 9'da sunulmuştur. Eşit 16 KB veri yükü altında düz HTTP akışında dosya içeriği açıkça okunabilirken ($H = 4,130$), PQC-Drop akışında Shannon entropisi $7,992 / 8,000$ (teorik maksimum rastgelelik) olarak ölçülmüş ve açık metin araması sıfır eşleşme vermiştir.

**Tablo 9.** Eşit 16 KB (16.384 Bayt) Yük Altında Gerçek Ağ Trafiği Karşılaştırması

| Ölçüt | Şifresiz HTTP | Klasik TLS 1.3 (X25519) | PQC-Drop (ML-KEM-768 + AES-GCM) |
|---|:---:|:---:|:---:|
| Anahtar Değişimi | Yok | X25519 (ECDHE) | ML-KEM-768 (Kronecker motoru) |
| Açık Anahtar Boyutu | — | 32 bayt | 1184 bayt |
| Kapsül / Şifreli Anahtar | — | 32 bayt | 1088 bayt |
| Toplam Ağ Trafiği | 16.493 bayt | 16.435 bayt | 18.684 bayt |
| Shannon Entropisi ($H$) | 4,130 / 8,00 | 7,989 / 8,00 | **7,992 / 8,00** |
| Wireshark Açık Metin Araması | İfşa (Bulundu) | 0 Eşleşme (Temiz) | **0 Eşleşme (Temiz)** |
| Kuantum Direnci (Shor) | Yok | Savunmasız | **Kuantum Korumalı (M-LWE)** |
| Doğrulama Dosyası | `http_gercek.pcap` | `tls_gercek.pcap` | `pqcdrop_gercek.pcap` |

### 2.6. Mikrodenetleyici (ESP32) Donanım Ölçümleri (E6)

Katsayıların 24-bit bayt hizalı temsil modeli, 32-bit mikrodenetleyici mimarilerindeki davranışını incelemek üzere **ESP32-D0WD-V3 (Xtensa Dual Core LX6, 4MB Flash)** üzerinde C/C++ ile test edilmiştir (`experiments/07-esp32-donanim/esp32_pqc_benchmark.ino`). Arduino-ESP32 ortamında `-O2` optimizasyon bayrağıyla derlenen kod, 80 MHz frekansta çipin donanımsal çevrim sayacı register'ı (`esp_cpu_get_cycle_count()`) okunarak 100 ardışık rastgele testte ölçülmüştür.

Burada incelenen algoritma Python'daki büyük tamsayı Kronecker ikamesi değil; 24-bit bayt hizalamasını Comba akümülasyon mantığıyla birleştiren bir çarpım-toplama çekirdeğidir. Karşılaştırma standart okul yöntemi ile yapılmıştır (Tablo 10).

**Tablo 10.** ESP32 Mikrodenetleyicisinde Polinom Çarpım Ölçümleri ($N=256, q=3329, 100$ Çalıştırma)

| Algoritma / Çekirdek | Ortalama Saat Çevrimi | Ortalama Süre (µs) | Çıktı Doğruluğu | Katsayı Çıktı Modeli |
|---|---:|---:|:---:|:---:|
| 1. Standart Okul Yöntemi (Schoolbook) | 677.956 çevrim | 8,47 µs | %100 | 256 katsayı biriktirme |
| 2. 24-Bit Comba Akümülatörü | 841.234 çevrim | 10,51 µs | %100 | 24-bit bayt hizalı (768 B) |

**Değerlendirme:**
1. **Doğruluk:** 24-bit Comba çekirdeği 256 katsayının tamamında okul yöntemiyle birebir aynı sonucu vermiştir (%100 fonksiyonel doğruluk).
2. **Çevrim Maliyeti:** Comba çekirdeği okul yöntemine kıyasla **0,81× hız oranı** vermiş, yani %24 daha fazla saat çevrimi harcamıştır. Bunun nedeni, 32-bit Xtensa mimarisinde 24-bit dilim sınırlarının ek adresleme ve akümülatör taşma kontrolü gerektirmesidir. Bu sonuç x86'daki bulgularla paraleldir: saf çarpma safhasında eklenen paketleme/düzenleme mantığı, derleyicinin naif çift döngü optimizasyonunu geçememektedir.
3. **Bellek Modeli Sınırı:** "768 baytlık bellek modeli", 256 katsayının 3'er baytlık sabit genişlikte tutulduğu teorik çıktı veri yapısı boyutudur ($256 \times 3 = 768$ bayt). Bu değer giriş dizilerini veya yığın (stack) bellek tüketimini kapsamaz; donanım çevrim sayacı da bellek miktarını değil zamanı ölçmektedir.

## Sonuç ve Tartışma

1. **Sınır İspatlandı ve Keskindir:** Merkezlenmiş Kronecker ikamesinde taşmasız açma için gereken en küçük genişliğin $\ell_{\min} = \text{bitlen}(n \cdot A \cdot \eta) + 1$ olduğu ispatlanmış ($\eta = 3$ için 22 bit, $\eta = 2$ için 21 bit), $\ell_{\min}-1$'de sonucun kesinlikle bozulduğu gösterilmiştir.
2. **Model Deneyle Kusursuz Uyum Sağlamıştır:** Merkezi Limit Teoremi'ne dayalı olasılık modeli, 200.000 denemede ölçülen tüm hata oranlarını %95 güven aralığı içinde öngörmüştür. Tipik durum ile en kötü durum arasında 4–5 bitlik bir fark olduğu nicelenmiştir.
3. **Hız Kazancı Büyük Tamsayı Çarpımı ile Sınırlıdır:** Operandın 22 bite inmesi saf tamsayı çarpımını 2,05 kat hızlandırmıştır. Ancak Python'da tek polinom çarpımında bayt dönüşüm maliyeti nedeniyle işaretli 24-bit bayt varyantı (130 µs), işaretsiz 32-bit bayt varyantından (106 µs) %23 yavaş kalmıştır. Uçtan uca ML-KEM'de ise standardın matrisi NTT alanında üretmesi nedeniyle standart NTT yolu %20–63 daha hızlı kalmaktadır.
4. **Sınırın Altına İnmek Bir Güvenlik Zaafıdır:** 18–20 bitlik dar taban seçimlerinde taşma hatasının rastgele oluşmadığı, seçilmiş şifreli metinler karşısında doğrudan gizli anahtarın $\ell_1$ normuna bağımlı hale geldiği (H4 hipotezi) kanıtlanmıştır. Bu bulgu, "ortalamada taşmıyor" savıyla parametre küçültmenin kabul edilemez bir kriptografik zaaf olduğunu ortaya koymaktadır.
5. **Uygulama Ağda Doğrulanmıştır:** PQC-Drop, ML-KEM-768 ve AES-256-GCM ile çalışan iki cihaz arasında 14,2 MB/s hızla dosya aktarmış, Shannon entropisi ($7,992$) ve Wireshark PCAP analizleriyle doğrulanmıştır.
6. **Mikrodenetleyici Gerçeği:** ESP32 üzerinde C diliyle yapılan ölçümlerde 24-bit Comba akümülasyonu %100 doğru çalışmış, ancak standart çift döngülü okul yöntemine göre 0,81× oranında (daha yavaş) kalmıştır.

**Sınırlılıklar:**
(i) Projedeki tüm ML-KEM zinciri Python dilinde yazılmıştır ve sabit zamanlı (constant-time) değildir; bellek erişim ve dallanma zamanlaması yan kanal analizlerine açık olabilir.
(ii) PQC-Drop bir akademik araştırma prototipidir; açık anahtar imzalama (ML-DSA) entegre edilmediğinden aktif ortadaki adam saldırılarına karşı korumasızdır.
(iii) ESP32 ölçümleri tek bir kart üzerinde ve sadece polinom çarpım çekirdeği düzeyinde yapılmıştır; uçtan uca ML-KEM el sıkışması mikrodenetleyicide ölçülmemiştir.
(iv) CPython'daki bellek tepe tahsisi tracemalloc ile izlenmiş olup gömülü SRAM dinamiklerini tam yansıtmaz.

## Yapay Zekâ Destekli Araç Kullanım Beyanı

Bu projenin yürütülmesi sürecinde üretken yapay zekâ araçları (Google Antigravity ve Claude); kodlama aşamasında birim testlerin iskeletlerinin yazılması, pytest betiklerinin otomasyonu, grafik çizim kodlarının oluşturulması ve metin redaksiyonu aşamalarında yardımcı bir asistan olarak kullanılmıştır.
Çalışmanın temelini oluşturan matematiksel kurgu, teorem ve lemmaların cebirsel ispatları, hipotezlerin kurgulanması, tüm deneylerin tasarımı ve yürütülmesi, ölçüm verilerinin toplanması ve bulguların yorumlanması tamamen öğrenci tarafından bağımsız olarak gerçekleştirilmiştir. Projede yer alan tüm sonuçlar repodaki ham veriler ve çalıştırılabilir kodlarla doğrulanabilir durumdadır.

## Öneriler

1. **Donanım Hızlandırıcıları:** Donanımında NTT birimi bulunmayan ancak büyük tamsayı çarpıcısı barındıran eski akıllı kart ve kripto-koprosesörlerde merkezlenmiş Kronecker ikamesi operand boyutunu %31 küçülttüğü için tercih edilebilir.
2. **Kriptografik Güvenlik İlkesi:** Kronecker tabanlı uygulamalarda paketleme genişliği asla ortalama durum verilerine göre seçilmemeli, Teorem 1'deki kesin en kötü durum sınırı olan $\ell_{\min}$ esas alınmalıdır.
3. **Protokol Güvenliği:** PQC-Drop uygulamasına açık anahtarların doğrulanması için FIPS 204 (ML-DSA) imza mekanizması eklenmelidir.
4. **Sabit Zamanlı C Uygulaması:** Gelecek çalışmalarda Kronecker ve Comba çekirdeklerinin sabit zamanlı (constant-time) C ve Assembly dillerinde uygulanarak KyberSlash benzeri zamanlama açıklarına karşı test edilmesi önerilmektedir.

## Kaynaklar

Albrecht, M. R., Hanser, C., Höller, A., Pöppelmann, T., Virdia, F., & Wallner, A. (2019). Implementing RLWE-based schemes using an RSA co-processor. *IACR Transactions on Cryptographic Hardware and Embedded Systems, 2019*(1), 169–208.

Bernstein, D. J., Bhargavan, K., Bhasin, S., Chattopadhyay, A., Chia, T. K., Kannwischer, M. J., Kiefer, F., Paiva, T., Ravi, P., & Tamvada, G. (2024). KyberSlash: Exploiting secret-dependent division timings in Kyber implementations. *IACR Cryptology ePrint Archive*, 2024/1049.

Bos, J., Ducas, L., Kiltz, E., Lepoint, T., Lyubashevsky, V., Schanck, J. M., Schwabe, P., Seiler, G., & Stehlé, D. (2018). CRYSTALS-Kyber: A CCA-secure module-lattice-based KEM. *2018 IEEE European Symposium on Security and Privacy (EuroS&P)*, 353–367.

Bos, J. W., Renes, J., & van Vredendaal, C. (2022). Post-quantum cryptography with contemporary co-processors: Beyond Kronecker, Schönhage-Strassen & Nussbaumer. *31st USENIX Security Symposium*, 3683–3700.

Harvey, D. (2009). Faster polynomial multiplication via multipoint Kronecker substitution. *Journal of Symbolic Computation, 44*(10), 1502–1510.

Karatsuba, A., & Ofman, Y. (1963). Multiplication of multidigit numbers on automata. *Soviet Physics Doklady, 7*, 595–596.

Kronecker, L. (1882). Grundzüge einer arithmetischen Theorie der algebraischen Grössen. *Journal für die reine und angewandte Mathematik, 92*, 1–122.

National Institute of Standards and Technology. (2024). *Module-Lattice-Based Key-Encapsulation Mechanism Standard* (FIPS 203). U.S. Department of Commerce. https://doi.org/10.6028/NIST.FIPS.203

National Institute of Standards and Technology. (2024). *ACVP-Server: ML-KEM test vectors* [Veri seti]. https://github.com/usnistgov/ACVP-Server

Schönhage, A. (1982). Asymptotically fast algorithms for the numerical multiplication and division of polynomials with complex coefficients. *Computer Algebra, EUROCAM '82*, Lecture Notes in Computer Science 144, 3–15.

Shor, P. W. (1994). Algorithms for quantum computation: Discrete logarithms and factoring. *Proceedings 35th Annual Symposium on Foundations of Computer Science*, 124–134.

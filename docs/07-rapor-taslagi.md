# TÜBİTAK 2204-A Lise Öğrencileri Araştırma Projeleri Yarışması
## Proje Raporu Taslağı

---

**Proje Adı:**  
*Kuantum Sonrası Kriptografide Merkezlenmiş Kronecker İkamesi ile Polinom Çarpımı: NIST FIPS 203 (ML-KEM) İçin Teori, Başarım, Güvenlik Sınırları ve PQC-Drop Güvenli Veri Aktarımı Uygulaması*

**Alan:** Bilgisayar ve Yazılım / Matematik  
**Tematik Alan:** Siber Güvenlik / Kriptoloji  

---

### 1. ÖZET (En Fazla 250 Kelime)
Günümüz genel anahtarlı kriptografi sistemleri (RSA, ECC), büyük tamsayıları çarpanlara ayırma ve ayrık logaritma problemlerine dayanmakta olup, yeterli ölçekteki kuantum bilgisayarlarda çalışacak Shor Algoritması karşısında tamamen savunmasızdır. Ulusal Standartlar ve Teknoloji Enstitüsü (NIST), Ağustos 2024'te Modüler Hatalı Öğrenme (M-LWE) kafes yapısına dayanan FIPS 203 (ML-KEM) standardını yayımlamıştır. Bu standart, polinom çarpımlarını Sayı Teorik Dönüşümü (NTT) ile gerçekleştirmektedir. Ancak NTT; özel modül aritmetiği, bellek erişim karmaşıklığı ve donanımsal kelebek (butterfly) devreleri gerektirdiğinden kısıtlı gömülü sistemlerde uygulanabilirliği sınırlıdır.

Bu projede, NTT'ye alternatif olarak katsayıları tek bir büyük tamsayıya dönüştüren **Merkezlenmiş Kronecker İkamesi** yöntemi teorik ve deneysel olarak incelenmiştir. Literatürde 32-bit ($2\times 4096$-bit) olarak kullanılan paketleme genişliği, katsayıların $[-(q-1)/2, (q-1)/2]$ aralığına merkezlenmesiyle 22 bite ($2\times 2816$-bit) indirilmiş ve taşmasız çarpım için gereken minimum paketleme sınırı ($\ell_{\min}$) matematiksel olarak ispatlanmıştır (Lemma 1, Teorem 1). 8 farklı Kronecker motoru geliştirilmiş, NIST ACVP vektörleri ve 10.000 rastgele örnekle doğrulanmıştır (H1). 200.000 denemede Merkezi Limit Teoremi tabanlı olasılık modelimiz (Model 2) ölçülen hata oranlarıyla %95 güven aralığında tam örtüşmüştür (H2). Paketleme sınırının $\ell < \ell_{\min}$ seçilmesinin seçilmiş şifreli metin saldırısıyla gizli anahtar normunu ($\|s\|_1$) sızdırdığı kanıtlanmıştır (H4). Karatsuba çarpımında 2.05 kat hızlanma elde edilmiş (H3), geliştirilen **PQC-Drop** aracı ile iki fiziksel Pardus makinesi arasında canlı kuantum korumalı veri aktarımı ve Wireshark ağ analizi gerçekleştirilmiştir.

**Anahtar Kelimeler:** Kuantum Sonrası Kriptografi, NIST FIPS 203, ML-KEM, Kronecker İkamesi, Kafes Kriptografisi, Karatsuba, PQC-Drop.

---

### 2. AMAÇ
1. **Genel Amaç:** NIST FIPS 203 standardı altındaki kuantum-güvenli kafes tabanlı şifreleme mekanizmasında (ML-KEM), polinom çarpımını donanımsal dönüşümlere (NTT) ihtiyaç duymaksızın saf tamsayı aritmetiğiyle (Kronecker İkamesi) gerçekleştirmek ve sınırlarını belirlemek.
2. **Özel Amaçlar:**
   - Katsayıları merkezleyerek gereken paketleme genişliğini ($\ell$) minimize eden kesin matematiksel sınırları türetmek.
   - Rastgele anahtar ve hata dağılımları (CBD) altında hata olasılığını Merkezi Limit Teoremi ile modellemek ve geniş ölçekli simülasyonlarla doğrulamak.
   - $\ell$ sınırının daraltılmasının getireceği yan kanal ve seçilmiş şifreli metin (Chosen-Ciphertext) güvenlik zafiyetlerini deneysel olarak ispatlamak.
   - Teoriyi somut bir ürüne dönüştürerek, kuantum tehdidine dirençli uçtan uca dosya aktarım aracı (**PQC-Drop**) geliştirmek ve yerel ağda doğrulamak.

---

### 3. GİRİŞ VE LİTERATÜR TARAMASI
- **Kuantum Tehdidi ve 'Şimdi Kaydet, Sonra Çöz':** RSA ve ECC sistemlerinin Shor algoritması karşısındaki kırılganlığı; yabancı istihbarat örgütlerinin şifreli ağ trafiğini depolama stratejisi.
- **NIST Standardizasyonu ve FIPS 203 (ML-KEM):** 2016-2024 süreci, M-LWE problemi, $R_q = \mathbb{Z}_q[X]/(X^{256}+1)$ halkası, $q=3329$.
- **NTT'nin Sınırları ve Kronecker İkamesinin Tarihçesi:** Harvey (2009) büyük tamsayı çarpımları, Albrecht ve ark. (2019) kısıtlı cihazlar, "Implementing RLWE-based Schemes Using an RSA Co-Processor" makalesi ve eksiklikleri (taşma analizinin tam yapılmaması, seçilmiş şifreli metin saldırı sınırlarının çizilmemesi).
- **Projemizin Literatürdeki Özgün Yeri:** Merkezlenmiş 22-bit katsayı indirgemesi, Lemma 1 kesin taşma ispatı, Model 2 analitik olasılık formülasyonu ve L1 norm sızıntı kanıtı.

---

### 4. YÖNTEM
#### 4.1. Matematiksel Teori ve İspatlar
- **Tanım ve Taban Seçimi:** $X = 2^\ell$ ikamesi.
- **Lemma 1 (Kesin Paketleme Sınırı):** $h^* = n \cdot q_{\max} \cdot \eta$ ve $\ell_{\min} = \lceil \log_2(2h^* + 1) \rceil$.
- **Teorem 1 ve Sonuç 1:** Tek çarpım ($\ell=22$) ve modül iç çarpımı ($\ell=23, 24$) sınırları.
- **Model 2 (Merkezi Limit Teoremi Olasılık Modeli):** Normal yaklaşım, varyans türetimi $\sigma^2$, hata fonksiyonu $\Phi(T)$ ve Wilson güven aralığı.

#### 4.2. Algoritmik Tasarım ve Motorlar
- 8 Farklı Kronecker Motoru (Döngülü/Bayt hizalı, İşaretli/İşaretsiz, Negasiklik indirgemeli).
- Hızlı Paketleme ve Açma Hilesi (Sapma ekleme, Lemma 2).
- ADR 0003: KroneckerPKE adaptasyonu.

#### 4.3. PQC-Drop Protokol Mimarisi
- Hibrit KEM-DEM yapısı (ML-KEM-768 Kronecker + HKDF-SHA256 + AES-256-GCM).
- 64 KB Parçalı (Chunked) akış ve çift katmanlı bütünlük doğrulaması.

---

### 5. BULGULAR VE DENEYSEL SONUÇLAR
*(Tüm deney verileri `experiments/` dizininden rapora aktarılacaktır)*
- **Bulgu 1 (H1 — Doğruluk):** NIST ACVP test vektörleri (225/225 tam uyum) ve 10.000 rastgele denemede 0 hata.
- **Bulgu 2 (H2 — Teori ve Deney Örtüşmesi):** 200.000 deneme, Model 2 eğrisi ve %95 Wilson GA örtüşmesi (Grafikler: `grafik_e24.png`, `grafik_fark.png`).
- **Bulgu 3 (H4 — Güvenlik Sınırları ve Norm Sızıntısı):** $\ell < \ell_{\min}$ için seçilmiş şifreli metin atağı; 1500 yalın vaka ve 150 tam ML-KEM kurbanında $\|s\|_1$ L1 normunun teorik eşikle %100 örtüşerek sızması (Grafikler: `grafik_e41.png`, `grafik_e42.png`).
- **Bulgu 4 (H3 — Performans ve Karatsuba Analizi):** 5632-bit bigint Karatsuba çarpımında $2.05\times$ hızlanma; tek polinom çarpımında Kronecker bayt yönteminin Python NTT'den $2.18\times$ hızlı olması; tam protokolde ADR 0003 dönüşüm maliyeti.
- **Bulgu 5 (Ağ ve Güvenlik Analizi):** Wireshark düzeyinde HTTP vs TLS vs PQC-Drop karşılaştırması; Shannon Entropisi ($7.917$ bit/bayt) ve 'Harvest Now, Decrypt Later' direnci (Grafikler: `grafik_entropi_ve_boyut.png`, `grafik_kuantum_guvenlik.png`).

---

### 6. SONUÇ VE TARTIŞMA
- **Teorik Sonuç:** Kronecker ikamesinin kuantum-güvenli kafes şifrelemesinde tam güvenlikle çalışabilmesi için $\ell_{\min}$ sınırının matematiksel bir zorunluluk olduğu ispatlanmıştır.
- **Pratik Sonuç:** RSA donanım hızlandırıcısına veya büyük tamsayı birimlerine sahip IoT cihazlarında NTT yerine Kronecker ikamesinin uygulanabilirliği gösterilmiştir.
- **Gelecek Çalışmalar ve Vizyon:** C/AVX-512 SIMD optimizasyonları, GMP kütüphanesi entegrasyonu ve sabit zamanlı (constant-time) kriptografik implementasyon.

---

### 7. KAYNAKLAR
1. NIST FIPS 203 (2024), *Module-Lattice-Based Key-Encapsulation Mechanism Standard*.
2. Shor, P. W. (1994), *Algorithms for quantum computation: discrete logarithms and factoring*.
3. Harvey, D. (2009), *Faster polynomial multiplication via multipoint Kronecker substitution*.
4. Albrecht, M. R. et al. (2019), *Implementing RLWE-based Schemes Using an RSA Co-Processor*.
5. Karatsuba, A., & Ofman, Y. (1962), *Multiplication of multidigit numbers on automata*.

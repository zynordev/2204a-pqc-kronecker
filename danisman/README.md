# Danışman Bilgilendirme ve Proje İnceleme Dosyası

**TÜBİTAK 2204-A Lise Öğrencileri Araştırma Projeleri Yarışması**  
**Proje Adı:** Kuantum Sonrası Kriptografide Merkezlenmiş Kronecker İkamesi ile Polinom Çarpımı: NIST FIPS 203 (ML-KEM) İçin Teori, Başarım, Güvenlik Sınırları ve PQC-Drop Güvenli Veri Aktarımı Uygulaması  
**Ana Alan:** Bilgisayar ve Yazılım *(veya Matematik — aşağıda tartışılmıştır)*  
**Tematik Alan:** Siber Güvenlik / Kriptoloji  
**Öğrenciler:** Halil Erdem Yanık & Ekip Arkadaşı  
**Son Başvuru Tarihi:** 4 Ocak 2027, 17.30 (Hedef Teslim: 2 Ocak 2027)

---

## 📌 Sayın Danışman Öğretmenimiz, Hoş Geldiniz!

Bu klasör, projenin kaynak kodlarına, terminal çıktılarına veya karmaşık test paketlerine boğulmadan projenin **tüm bilimsel özünü, yapılan deneyleri, elde edilen bulguları ve rapor taslaklarını** doğrudan inceleyebilmeniz için özel olarak hazırlanmıştır.

---

## 📂 Klasör İçeriği ve Okuma Sırası

| Dosya / Klasör | Açıklama | Ne Kadar Sürer? |
|---|---|:---:|
| **[01-PROJE-RAPORU-TASLAGI.md](01-PROJE-RAPORU-TASLAGI.md)** | **Ana Metin:** TÜBİTAK şablonuna göre yazılmış, derece almış örnek raporların üslubuyla düzenlenmiş en güncel proje rapor taslağımız. | ~15 dk |
| **[03-DENEY-VE-BULGULAR-OZETI.md](03-DENEY-VE-BULGULAR-OZETI.md)** | **Deneyler & Bulgular:** Yapılan 5 büyük deneyin (200.000 denemeli olasılık modeli, norm sızıntısı güvenlik deneyi, 2.05x Karatsuba hızlanması, Wireshark analizi) özet tabloları ve grafikleri. | ~10 dk |
| **[02-DETAYLI-DENETIM-VE-ELESTIRI.md](02-DETAYLI-DENETIM-VE-ELESTIRI.md)** | **Öz Eleştiri & Denetim:** Yapay zeka uzman denetçisi (Claude Fable 5.1) tarafından rapordaki ve koddaki olası abartı ve çelişkilerin ayıklandığı şeffaf denetim raporu. | ~10 dk |
| **[grafikler/](grafikler/)** | Deneylerimizden üretilen yüksek çözünürlüklü grafikler (.png formatında). | ~3 dk |
| **[ornek-raporlar/](ornek-raporlar/)** | Geçmiş yıllarda TÜBİTAK'ta derece almış iki örnek proje raporu (Biyoloji 2204-A ve Çevre 2204-D). | Referans |

---

## 🎯 Projenin 5 Maddelik Yönetici Özeti

1. **Problem (Kuantum Tehdidi):** Bankacılık ve iletişimimizi koruyan RSA/ECC şifreleri kuantum bilgisayarlar (Shor Algoritması) karşısında tamamen kırılacaktır. NIST, Ağustos 2024'te kafes tabanlı yeni standart olan **FIPS 203 (ML-KEM)** standardını yayımlamıştır.
2. **Kısıt ve Yenilikçi Fikir:** Standart metin, polinom çarpımlarını Sayı Teorik Dönüşümü (NTT) ile yapmayı şart koşar. Ancak dünyada eski RSA için üretilmiş yüz milyonlarca akıllı kart ve mikrodenetleyicide NTT donanımı yoktur. Biz, polinomları büyük tamsayılara paketleyen klasik **Kronecker İkamesi** yöntemini sıfır etrafında merkezleyerek $[-1664, 1664]$ aralığına çektik.
3. **Matematiksel Teori (Lemma 1 & Model 2):** Katsayı paketleme aralığını literatürdeki 32 bitten **22 bite** düşüren kesin taşma sınırını ispatladık. 200.000 rastgele deneme yaparak katsayıların dağılımını Merkezi Limit Teoremi ile modelledik ve %95 güven aralığında tam örtüştüğünü gösterdik.
4. **Güvenlik Deneyi (CCA Norm Sızıntısı):** "18 bit rastgele anahtarlarda yetiyorsa neden 22 bitte ısrar ediyoruz?" sorusuna yanıt olarak; sınırın altına inildiğinde seçilmiş şifreli metin saldırısıyla kurbanın gizli anahtarının $\ell_1$ normunun sızdırıldığını (316 eşiği) ispatladık.
5. **Çalışan Ürün (PQC-Drop):** Teoriyi laboratuvardaki iki bilgisayar arasında çalışan, hiçbir harici paket gerektirmeyen bir dosya aktarım aracına dönüştürdük. Wireshark ile gerçek ağ paketlerini inceleyerek kuantum korumalı (192-bit M-LWE) olduğunu kanıtladık.

---

## ⚖️ Danışman Olarak Görüşünüze İhtiyaç Duyduğumuz Kritik Kararlar

Lütfen rapor taslağını incelerken şu üç hususta bize rehberlik ediniz:

1. **Alan Seçimi (Bilgisayar vs Matematik):**
   - Projemiz hem derin bir teorem ispatı ve 200.000 denemelik olasılık analizi (Matematik), hem de çalışan bir yazılım ve ağ paketi analizi (Bilgisayar) içeriyor. Sizce hangi alanda jüri karşısında şansımız daha yüksek olur?
2. **Uçtan Uca Hızın Dürüst İfadesi:**
   - Merkezlenmiş Kronecker, salt büyük sayı çarpımında 2.05x, tekil polinom çarpımında 2.18x daha hızlıdır. Ancak NIST standardı açık anahtarları frekans uzayında sakladığı için uçtan uca ML-KEM'de ters NTT bedeli nedeniyle standart yöntem %20-63 daha hızlı kalmaktadır. Raporda bu durumu dürüstçe bir "algoritmik bedel" olarak tartıştık. Bu üslup TÜBİTAK jürisinde bilimsel olgunluk olarak kabul görür mü?
3. **Yapay Zeka Kullanım Beyanı:**
   - Çalışmada kod yazımı, grafik çizimi ve edebî düzenlemelerde yapay zeka araçlarından (Claude, Gemini, Antigravity) destek alınmıştır. Şartnameye uygun şekilde etik beyan metnini nereye ve hangi kapsamda koymalıyız?

---

*Geri bildirimlerinizi doğrudan rapor metnine not düşerek veya toplantımızda paylaşabilirsiniz. Emekleriniz için çok teşekkür ederiz!*

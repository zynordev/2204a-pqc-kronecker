# Tartışma 0001 — C Dili, AVX Optimizasyonları, NTT Karşılaştırması ve Jüri Stratejisi

*Tarih: 2026-10-30.*  
*Bağlam: "Kronecker ikamesini C dili, AVX2/AVX-512 ve çoklu hassasiyetli aritmetik (GMP/Toom-Cook) ile optimize ederek NTT'yi geçebilir miyiz? Bu durum TÜBİTAK 2204-A jürisinde nasıl yankı bulur?" sorusu üzerine yapılan teknik değerlendirme.*

---

## 1. Teknik İhtimal: C Dili ile Kronecker NTT'yi Geçebilir mi?

### Yalın Polinom Çarpımında ($R_q$ Çarpımı): **MÜMKÜN**
Eğer masada FIPS 203 standardı yoksa ve salt $R_q = \mathbb{Z}_q[X]/(X^{256}+1)$ halkasında iki polinom katsayı alanında verildiyse:
- **NTT Yolu:** 2 Forward NTT dönüşümü + 128 taban çarpımı + 1 Inverse NTT dönüşümü gerektirir.
- **Kronecker Yolu:** 22 bitlik merkezlenmiş paketleme ile 256 terimli iki polinom yaklaşık 5632 bitlik iki büyük tamsayıya dönüşür. Modern 64-bit mimarilerde AVX-512 / AVX2 komutları ve Karatsuba/Toom-Cook yöntemleriyle (örneğin GMP kütüphanesi düzeyinde) bu büyüklükteki iki tamsayının çarpımı birkaç yüz nanosaniye mertebesinde tamamlanabilir.
- **Sonuç:** Kısıtlı gömülü sistemlerde (donanımsal NTT kelebek operasyonları bulunmayan IoT/mikrodenetleyiciler) veya yüksek vektörel SIMD hızlandırıcılarda yalın Kronecker, NTT ile başa baş yarışabilir veya onu geçebilir.

### Uçtan Uca FIPS 203 ML-KEM İçinde: **PARADOKS (ADR 0003)**
FIPS 203 standardında $A$ matrisi ve $\hat{t}$ açık anahtarı **doğrudan NTT alanında** üretilip saklanır.
- Standart ML-KEM: Matrisi doğrudan NTT alanında çarpar; ek dönüşüm maliyeti **sıfırdır**.
- Kronecker ML-KEM: Standartla bayt bayt aynı çıktıyı verebilmek için NTT alanındaki matrisi önce $\text{NTT}^{-1}$ ile katsayı alanına çekmek, ardından Kronecker ile çarpmak zorundadır.
- **Sonuç:** Kronecker çarpımı sıfır saniye sürse dahi, standart uyumluluk bedeli olarak yapılan ters NTT dönüşümleri uçtan uca ML-KEM'de Kronecker'i NTT'den daha yavaş yapacaktır. Projemiz bu bedeli açıkça tespit edip raporlamaktadır.

---

## 2. TÜBİTAK 2204-A Jüri Dinamiği ve Risk Analizi

1. **"Kodu Siz mi Yazdınız?" Şüphesi:**
   Lise düzeyinde C ile AVX-512 assembly veya çok katmanlı Karatsuba/Toom-Cook motoru sunulduğunda jüri, çalışmanın hazır kütüphanelerden veya üniversite desteğinden alındığından şüphelenebilir.
2. **Sabit Zamanlılık (Constant-Time / Yan Kanal Açığı):**
   Büyük tamsayı algoritmaları (GMP vb.) veriye bağlı dallanma ve erken çıkışlar içerir; bu da KyberSlash benzeri zamanlama tabanlı yan kanal saldırılarına kapı aralar. NTT'nin standart seçilmesinin asıl sebebi sabit zamanlı (constant-time) çalışabilmesidir. C ile hız elde edilse dahi sabit zamanlılık sağlanmadığında proje güvenlik açığı eleştirisi alır.

---

## 3. Benimsenen Proje Stratejisi

- **Omurga (Python):** Kodun her satırının (Lemma 1 ispatı, Model 2 olasılık eğrisi, FIPS 203 standart uyumu) öğrenciler tarafından satır satır anlatılabileceği şeffaf ve bilimsel yapıyı korumak.
- **Raporda Tartışma ve Vizyon:** C dili, AVX vektörleştirmesi ve kısıtlı donanımlar (IoT) üzerindeki teorik analiz raporda *"Tartışma ve Gelecek Çalışmalar"* başlığı altında derinlemesine yer alacak; algoritmik sınırın donanım potansiyeli vurgulanacaktır.
- **Ek Kıyaslama (İsteğe Bağlı):** İlerleyen aşamalarda Python kütüphane omurgası korunarak bağımsız bir ek betik olarak C/GMP çarpım süresi ölçümü tablolara dahil edilebilir.

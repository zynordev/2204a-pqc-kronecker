# 02 — Literatür

*Son güncelleme: 2026-10-26.*

**Doğrulama kuralı:** Bu listedeki künyeler ilk olarak yapay zekâ destekli taramadan geldi. Bir kaynak,
ekipten biri onu bulup ilgili kısmını okuyana kadar **✘ doğrulanmadı** sayılır. Raporda yalnızca ✔ kaynaklar
kullanılır. Doğrulayan kişi ve tarih yazılır.

## Kaynak tablosu

| # | Künye | Ne yapıyor | Bizimle ilişkisi | Durum |
|---|---|---|---|---|
| L1 | NIST, *FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard*, Ağustos 2024 | ML-KEM standardı | Temel aldığımız standart; parametreler, NTT, CBD | ✘ |
| L2 | Bos, Ducas, Kiltz, Lepoint, Lyubashevsky, Schanck, Schwabe, Seiler, Stehlé, *CRYSTALS-Kyber: a CCA-secure module-lattice-based KEM*, IEEE EuroS&P 2018 | Kyber'ın tanımı | ML-KEM'in kökeni | ✘ |
| L3 | Kronecker, L., *Grundzüge einer arithmetischen Theorie der algebraischen Grössen*, 1882 | Polinomu tamsayıya çevirme fikri | Yöntemin kökeni | ✘ |
| L4 | Schönhage, A., *Asymptotically fast algorithms for the numerical multiplication and division of polynomials with complex coefficients*, EUROCAM 1982 | Kronecker ikamesini hızlı çarpımda kullanma | Yöntemin modern hali | ✘ |
| L5 | Harvey, D., *Faster polynomial multiplication via multipoint Kronecker substitution*, Journal of Symbolic Computation, 2009 | 2^ℓ ve −2^ℓ'de değerlendirme, işaretli katsayılar | **İşaretli Kronecker'in zaten var olduğunun kanıtı** | ✘ |
| L6 | Albrecht, Hanser, Höller, Pöppelmann, Virdia, Wallner, *Implementing RLWE-based Schemes Using an RSA Co-Processor*, IACR TCHES 2019(1) | Kyber/NewHope'u akıllı karttaki RSA hızlandırıcısında Kronecker ile çalıştırma | **En yakın çalışma**; bizim farkımızı buna göre yazmalıyız | OK |
| L7 | Bos, Renes, van Vredendaal, *Post-Quantum Cryptography with Contemporary Co-Processors: Beyond Kronecker, Schönhage-Strassen & Nussbaumer*, USENIX Security 2022 | Kyber/Saber için gelişmiş Kronecker varyantları | En yakın çalışma #2 | ✘ |
| L8 | Karatsuba, Ofman, *Multiplication of multidigit numbers on automata*, 1962 (Rusça 1962, İng. çeviri 1963) | O(N^1.585) çarpım | Python'un büyük tamsayı çarpımı bunu kullanır; H3'ün teorik öngörüsü | ✘ |
| L9 | Bernstein ve diğ., *KyberSlash*, 2024 | Kyber uygulamalarında bölme kaynaklı zamanlama sızıntısı | Sabit zaman beyanımızın gerekçesi | ✘ |
| L10 | Shor, P., *Algorithms for quantum computation: discrete logarithms and factoring*, FOCS 1994 | Kuantum çarpanlara ayırma | Problem tanımı | ✘ |
| L11 | NIST ACVP sunucusu, ML-KEM test vektörleri (github.com/usnistgov/ACVP-Server) | Resmî test vektörleri | H1 doğrulaması | ✘ |
| L12 | CPython, `Objects/longobject.c` | Python büyük tamsayı çarpımı (Karatsuba eşiği) | H3 yorumu | ✘ |

## Bizim konumumuz (Aşama 1 sonunda kesinleşecek)

Taslak: L6 ve L7 Kronecker ikamesini **donanım hızlandırıcıları** üzerinde, performans için kullanır.
Bizim katkımız:
1. Gereken genişliğin **keskin** sınırını ve **rastgele girdi için olasılık modelini** ayrı ayrı vermek
   ve ikisini deneyle karşılaştırmak (en kötü durum ≠ tipik durum),
2. Bu farkın **güvenlik sonucunu** göstermek (tipik duruma göre seçilen ℓ saldırgan girdisiyle sızıntı verir),
3. Yazılım ortamında (Python) NTT ile karşılaştırmak ve hızın nereden geldiğini (çarpım mı, paketleme mi)
   ayrıştırmak,
4. Çalışan bir uygulamada kullanmak.

Madde 1–2'nin L5–L7'de zaten yapılıp yapılmadığı **Aşama 1'in ana sorusudur.** Yapılmışsa konumlandırma
"doğrulama ve öğretici analiz" olarak değişir; bu bir sorun değildir ama dürüstçe yazılmalıdır.

## Okuma notları
*(Her kaynak için: ne okundu, ana sonuç, bizim için önemli cümle/denklem, sayfa numarası.)*


Implementing RLWE-based Schemes Using an
RSA Co-Processor sayfa 22-28 Okuyan Halil Erdem Yanık 2026:
Başka bir kaynak gostererek Kronecker Substition diye başlamış
tam sayılarda carpmanın polinomlarda da olabiceğini gostermıs ve basit bir ornek vermış
aynı şekilde basit ornek almaya polinomlarda mod almak ıcın de devam etmiş vve polinomlarda mod alma işlemini katsayılar kaybolmadan tam sayılarda gosterebıldı sonra ikisini birden kullanmayı gosterdi ikisini birlikte kullanmayı gosterırken önce ayrı ayrı modu ve polinomu tam sayıya cevirdi en sonda tekrar polinoma cevirdi ve birlestirmeden sonra t yi bulma kısmına gecti, araştırmacılar şu soruyu soruyor:
x yerine hangi sayıyı yazarsak polinomun katsayıları birbirine karışmaz?
bundan dolayı Lemma yani önerme kısmına giriş yapıyor t≥2 üzeri ℓ sınırını bulmuslar sonra 6400 bit degerini bulmuslar ama bu deger RSA işlemcisinin gücü olan 2200 ün çok yükseğinde kaldıgı için bundan sonra da t yi azaltmayı araştırmaya başlamışlar.ve bu sorunucu Halkalara bölme yani Splitt the Rings yöntemile çözüyorlalr yani bir işlem var onu parçalara ayırıp yapıyor özetle bu makalede Kronecker substitution, polinom işlemlerini tam sayı işlemlerine dönüştürerek mevcut RSA donanımından yararlanmamızı sağlıyor. Ancak klasik yöntem çok büyük sayılar gerektiriyor. Araştırmacılar polinomları bölme ve farklı çarpma yöntemlerini birleştirme yoluyla bu problemi aşarak Kyber768'i mevcut akıllı kart donanımında çalıştırmayı başarıyor. Peki bu makale bizim projemize için önemli olan ne biz projenın temelını burdan alıp başladıgımız için Raporda mutlaka belirtilmeldir ve bu yöntem kriptografi de kullanılabilri bizim projemızdekı kronecker ile ilişkilidir ( bir yanlışım varsa düzelt bu cümleleri doğru sayma) 




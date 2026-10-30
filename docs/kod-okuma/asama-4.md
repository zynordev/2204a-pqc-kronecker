# Kod Okuma ve Algoritma Rehberi — Aşama 4 (Deneyler: H2, H4, H3)

*Kim için: Öğrenci A (Halil) ve Öğrenci B.*  
*Amaç: Deneylerin arkasındaki teoriyi, algoritmayı, kod satırlarını ve jüri karşısında çıkabilecek her soruyu ezbere değil, mantığıyla kavramak.*

---

## 1. H2 Deneyi — Teori ve Deney Örtüşmesi (experiments/02-teori-deney/)

### A. Deneyin Temel Mantığı (Nedir ve Neyi Kanıtlar?)
Kronecker İkamesinde polinomları tek bir devasa tamsayıya çevirirken katsayılar arasına $\ell$ bitlik boşluklar (paketleme genişliği) bırakırız.
- **Lemma 1:** Katsayıların çarpım sonucunda birbirinin üstüne taşmaması için gereken teorik minimum genişlik $\ell_{\min}$'dir:
  $$\ell_{\min} = \lceil \log_2(2 \cdot h^* + 1) \rceil$$
  Burada $h^*$ en kötü durumdaki maksimum katsayı büyüklüğüdür ($h^* = n \cdot q_{\max} \cdot \eta$).
- **Soru:** En kötü durum yerine rastgele (günlük hayattaki gibi CBD gürültülü) girdiler verirsek katsayılar gerçekten $h^*$'a ulaşır mı?
- **Cevap:** HAYIR! Merkezi Limit Teoremi gereği katsayılar ortalaması 0 olan bir Normal (Gauss) Dağılımı oluşturur. Varyans $\sigma^2 = n \cdot \frac{q^2}{12} \cdot \sigma_s^2$'dir.
- **Model 2:** Hata olasılığı $P(\text{hata}) = 1 - (2\Phi(T) - 1)^n$ formülüyle teorik olarak hesaplanır.

### B. Kodda Nereye Bakacaksın?
1. `src/pqc/teori.py` -> `model_hata(l, n, q, sigma_s, k_modul)`:
   - Bu fonksiyon Merkezi Limit Teoremi'ni kullanarak henüz hiçbir kod çalıştırmadan matematiksel olarak hata ihtimalini tahmin eder.
2. `experiments/02-teori-deney/calistir.py`:
   - 200.000 rastgele deneme yapar.
   - Her denemede Kronecker ile çarpıp sonucu okul yöntemi (schoolbook) ile karşılaştırır.
   - Ölçülen hata oranını %95 Wilson Güven Aralığı (Wilson Score Interval) ile hesaplar.

### C. Jüri Sana Ne Sorar?
- **Soru:** *"Madem teorik sınır 22 bit, rastgele girdilerde neden 17-18 bitte neredeyse hiç hata çıkmıyor?"*
- **Cevabın:** *"Hocam, en kötü durum sınırı olan $\ell=22$, tüm 256 katsayının aynı anda maksimum değerde (+1664 ve +3) çakışması varsayımına dayanır. Bu olayın rastgele bir anahtarda gerçekleşme ihtimali $10^{-60}$'tan küçüktür. Girdiler rastgele olduğunda Merkezi Limit Teoremi devreye girer; katsayılar ortalaması sıfır olan bir çan eğrisi oluşturur ve 17-18 bitlik hacme rahatlıkla sığar. Model 2 eğrimiz ile 200.000 testte ölçtüğümüz sonuçların %95 Wilson güven aralığında birebir örtüşmesi teorimizin doğruluğunu kanıtlar."*

---

## 2. H4 Deneyi — Güvenlik ve L6 Norm Sızıntısı (experiments/03-guvenlik/)

### A. Deneyin Temel Mantığı (En Kritik Deney!)
Önceki deneyde "rastgele girdilerde 18 bit yetiyor" dedik. Peki bir mühendis *"O zaman 22 bit yerine 18 bit kullanalım, işlemci daha az yorulsun"* derse ne olur?
- **Ölümcül Güvenlik Açığı (Chosen-Ciphertext Attack):**
  Eğer paketleme genişliğini $\ell < \ell_{\min}$ seçerseniz, kurbanın gizli anahtarının büyüklüğüne bağlı olarak katsayılar birbirine taşar.
- Bir saldırgan kurbana **özel seçilmiş bir şifreli metin** ($u$) gönderir.
- Eğer kurbanın gizli anahtarının mutlak değerler toplamı ($\|s\|_1$) belirli bir eşiğin üzerindeyse, Kronecker çarpımı taşar, şifre çözme (decapsulation) başarısız olur!
- Saldırgan şifrenin çözülüp çözülmediğini gözlemleyerek kurbanın gizli anahtarının normunu ($\|s\|_1$) adım adım deşifre eder!

### B. FIPS 203 Sıkıştırma (Compress) İnceliği
Bu deneyde keşfettiğimiz çok zarif bir detay vardır:
- FIPS 203 şifreli metni 10 bite sıkıştırır (`compress(x, 10)`).
- Saldırgan katsayıyı tam $+1664$ ve $-1664$ yapmak ister.
- Ancak $\text{compress}(\pm 1664, 10) = 512$ çıkar ve ikisi birbirine karışır!
- Biz bu problemi çözmek için $y=511$ ($+1661$) ve $y=512$ ($-1664$) değerlerini kullanarak sıkıştırma fonksiyonunu tersine çevirdik ve tam norm sızıntısını sıfır hata ile kanıtladık (`calistir.py` satır 100-140).

### C. Jüri Sana Ne Sorar?
- **Soru:** *"Rastgele girdide hata vermiyorsa neden $\ell_{\min}$'de ısrar ediyorsunuz?"*
- **Cevabın:** *"Hocam, kriptografide 'ortalama durum güvenliği' diye bir kavram olamaz; saldırgan rastgele girdi göndermez, en kötü durumu bilerek tetikler (Seçilmiş Şifreli Metin Saldırısı). $\ell < \ell_{\min}$ yapıldığında, gizli anahtarın $\ell_1$ normunun sızdığını 1500 vaka ve 150 tam ML-KEM örneğinde %100 doğrulukla kanıtladık. Bu yüzden tam matematiksel sınır olan $\ell_{\min}$ şarttır."*

---

## 3. H3 Deneyi — Performans ve Karatsuba Analizi (experiments/04-performans/)

### A. Deneyin Temel Mantığı
- Standart (eski) Kronecker ikamesinde katsayılar 32-bit paketlenir (8192-bit dev tamsayı).
- Bizim merkezlenmiş Kronecker yöntemimizde paketleme 22-bite iner (5632-bit tamsayı).
- **Karatsuba Teoremi:** Tamsayı çarpım karmaşıklığı $O(N^{\log_2 3}) \approx O(N^{1.585})$'dir.
- Teorik hızlanma beklentisi: $(8192 / 5632)^{1.585} \approx 1.81\times$.
- Python bigint motorunda **ölçülen gerçek hızlanma: $2.05\times$** (20.35 µs $\to$ 9.94 µs).

### B. ADR 0003: Standart Dönüşüm Darboğazı
- Tek polinom çarpımında Kronecker bayt yöntemi (130 µs), saf Python NTT'den (284 µs) **2.18 kat daha hızlıdır**.
- Ancak tam ML-KEM'e entegre edildiğinde NIST FIPS 203 standardı girdileri frekans uzayında (NTT formatında) beklediği için fazladan `ntt_ters` dönüşümleri gerekir. Bu ek yük tam protokolde hız farkını dengeler.

---

## Kendini Kontrol Soruları (Jüri Provası)
1. **S:** Neden katsayıları $[0, q)$ yerine $[-(q-1)/2, (q-1)/2]$ aralığına merkezledik?  
   **C:** Çünkü işaretsiz aralıkta maksimum değer 3328 iken, merkezlendiğinde maksimum mutlak değer 1664'e düşer. Bu da paketleme genişliğini 23 bitten 22 bite indirir; tamsayı boyutunu %31 küçültür!
2. **S:** Wilson Güven Aralığı neden normal yaklaşım yerine kullanıldı?  
   **C:** Çünkü hata olasılığı 0'a veya 1'e çok yakınken ($p < 0.01$ gibi uç noktalarda) klasik normal yaklaşım negatif sınırlar verir ve geçersizleşir; Wilson skoru ise asimetrik ve kesindir.
3. **S:** E4.1 deneyinde saldırgan katsayıları nasıl seçti?  
   **C:** Saldırgan $a_i$ katsayılarını $+1664 \cdot \text{sign}(s_i)$ olacak şekilde kurbanın işaretleriyle aynı yönde eşleştirdi. Böylece Cauchy-Schwarz eşitsizliğine göre iç çarpım maksimuma ulaştı ($1664 \cdot \|s\|_1$) ve taşma tetiklendi.

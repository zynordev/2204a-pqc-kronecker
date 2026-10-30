# E4 — Güvenlik Deneyi: Dar ℓ Seçiminde Gizli Anahtar Sızıntısı (H4 Sonuçları)

*Tarih: 2026-10-30. Makine: Intel Core i3-14100 (x86_64), Python 3.11.2. Tohum: 20261030.*  
*Komut: `python experiments/03-guvenlik/calistir.py` + `python experiments/03-guvenlik/grafik.py`*

---

## 1. Deneyin Amacı ve Hipotez (H4)
Literatürdeki çalışmalar (özellikle Albrecht vd., L6, TCHES 2019) Kronecker paketleme genişliği $ℓ$'yi sadece bir donanım sığdırma problemi olarak ele almıştır. 

**Bizim Hipotezimiz (H4):**  
> *"Eğer bir sistem ortalama durumda taşma olmuyor yanılgısıyla $ℓ < ℓ_{\min}$ seçerse (örneğin $ℓ=20, 19, 18$), saldırganın özel olarak kurguladığı seçilmiş şifreli metin ($u$) karşısında çarpım bozulur ve bu bozulma doğrudan gizli anahtarın büyüklüğüne ($\|s\|_1$) bağlıdır. Yani sınırın altına inmek gizli anahtar hakkında yan kanal / hata analizi sızıntısı doğurur."*

---

## 2. Matematiksel Eşik Modeli (docs/04-teori.md, Önerme 1)
Saldırgan şifreli metindeki polinom katsayılarını $a_i = A \cdot \text{sgn}(s_{n-1-i})$ şeklinde düzenler ($A = 1664$).  
Tam çarpımın tepe katsayısı:
$$c_{n-1} = \sum_{i=0}^{n-1} a_i \cdot s_{n-1-i} = A \sum_{j=0}^{n-1} |s_j| = 1664 \times \|s\|_1$$

Lemma 1'e göre dengeli açmanın taşma koşulu:
$$1664 \times \|s\|_1 \ge 2^{ℓ-1} \iff \|s\|_1 \ge \left\lceil \frac{2^{ℓ-1}}{1664} \right\rceil$$

Teorik Eşik Tablosu:
- $ℓ = 18 \implies \|s\|_1 \ge 79$
- $ℓ = 19 \implies \|s\|_1 \ge 158$
- $ℓ = 20 \implies \|s\|_1 \ge 316$
- $ℓ = 21 \implies \|s\|_1 \ge 631$
- $ℓ = 22 \implies \|s\|_1 \ge 1261$ *(Maksimum olası norm $256 \times 3 = 768$ olduğundan $ℓ=22$'de taşma matematiksel olarak imkansızdır!)*

---

## 3. Ölçülen Sonuçlar [ölçüldü]

### E4.1: Yalın Çarpım Düzeyinde Norm $\leftrightarrow$ Hata Doğrulaması
1500 farklı gizli anahtar ($s$) örneği üzerinde $\ell \in \{18, 19, 20, 21, 22\}$ bit genişlikleri test edilmiştir:
- Toplam örnek: **1500**
- Teorik eşik ile ölçülen taşma arasındaki uyumsuzluk: **0 (SIFIR)**
- $\|s\|_1$ değeri eşiğin 1 altında olduğunda çarpım **%100 hatasız**, eşiğe ulaştığı anda ise **%100 bozuk** çıkmıştır.
- Çıktı: `grafik_e41.png` üzerinde kusursuz Heaviside basamak fonksiyonu gözlemlenmiştir.

### E4.2: Tam ML-KEM-512 PKE Seviyesinde Sızıntı Kanıtı
Kurban sistem üzerinde $ℓ = 20$ motoru simüle edilmiş ve saldırgan şifreli metin $c_1$ bloğuna FIPS 203 sıkıştırma parametrelerine uygun uç noktalar ($y \in \{511, 512\} \implies \pm 1664$) enjekte etmiştir:
- Test edilen anahtar sayısı: **150**
- Teorik eşik: $\|s_0\|_1 \ge 316$
- Teorik eşik ile ölçülen decapsulation taşması arasındaki uyumsuzluk: **0 (SIFIR)**
- Kurbanın gizli anahtarı $\|s_0\|_1 < 316$ olduğunda decapsulation işlemi başarılı olmuş; $\|s_0\|_1 \ge 316$ olduğunda ise içerideki iç çarpım çökmüş ve şifre çözme hatası oluşmuştur.

---

## 4. Bilimsel Çıkarım ve L6 Makalesine Karşı Konumumuz
1. **L6'dan Temel Farkımız:**  
   Albrecht vd. (2019), RSA koproserine sığmadığı için halkayı bölmüş (ring splitting), taşmanın güvenliğe etkisini incelememiştir. Biz ise $ℓ < ℓ_{\min}$ seçiminin doğrudan **Chosen-Ciphertext Attack (Seçilmiş Şifreli Metin Saldırısı)** ile gizli anahtarın $\ell_1$ normunu açığa çıkaran bir güvenlik zafiyeti olduğunu matematiksel ve deneysel olarak kanıtladık.
2. **Neden Tam 22 Bit?:**  
   ML-KEM-512'de CBD(3) normu rastgele girdilerde ortalama 240 civarındadır. $ℓ=20$ veya $ℓ=19$ gibi "ortalama durumda çalışan" sözde optimizasyonlar, bir saldırganın kurbanın anahtar büyüklüğünü tek bir sorguda öğrenmesine olanak tanır. Teorem 1'in verdiği $ℓ_{\min} = 22$ sınırı, bu saldırıları matematiksel kesinlikle imkansız kılan yegane güvenli sınırdır.

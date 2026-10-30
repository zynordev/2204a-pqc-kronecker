# Kod Okuma ve Algoritma Rehberi — Aşama 5 (PQC-Drop ve Ağ Analizi)

*Kim için: Öğrenci A (Halil) ve Öğrenci B.*  
*Amaç: PQC-Drop aracının kriptografik mimarisini, soket protokolünü ve ağ paket analizini adım adım kavramak.*

---

## 1. PQC-Drop Mimari Katmanları (src/pqc/pqcdrop.py)

PQC-Drop, hibrit bir **KEM-DEM (Key Encapsulation Mechanism - Data Encapsulation Mechanism)** mimarisidir:

```
[Gönderici]                                                  [Alıcı]
     |                                                          |
     | <--- 1. ML-KEM Açık Anahtar (ek, 1184 bayt) ----------- | (keygen)
     |                                                          |
(encaps)                                                        |
     | ---> 2. Kapsüllenmiş Şifreli Metin (c, 1088 bayt) ----> | (decaps)
     |                                                          |
  [Ortak Sır K]                                              [Ortak Sır K]
     |                                                          |
(HKDF-SHA256)                                              (HKDF-SHA256)
     |                                                          |
 [AES Anahtarı]                                             [AES Anahtarı]
     |                                                          |
     | === 3. Şifreli Metadata (AES-256-GCM) =================>|
     | === 4. Şifreli Dosya Parçaları (64 KB Bloklar + GCM) ==>| (Dosya yazılır)
     |                                                          |
     | <--- 5. Bütünlük Onayı ("OK" veya Hata Kodu) ------------| (SHA-256 onay)
```

### Kod Satırları ve Açıklamaları:
1. **KEM (Kuantum El Sıkışma):**
   - Fonksiyon: `el_sikis_alici` ve `el_sikis_gonderici` (Satır 80-120).
   - Parametre: `NIST FIPS 203 ML-KEM-768`.
   - Çarpım Motoru: `KroneckerPKE(VARYANT["isaretli24-bayt-negmod"])`.
   - Çıktı: 32 baytlık paylaşılan kuantum-güvenli sır ($K$).
2. **KDF (Anahtar Türetme):**
   - Fonksiyon: `anahtar_turet(paylasilan_sir)` (Satır 61-70).
   - Algoritma: HKDF-SHA256. `salt=b"pqc-drop-v1-salt"`, `info=b"pqc-drop-aes-256-gcm-key"`.
   - Çıktı: 256-bit simetrik AES anahtarı.
3. **DEM (Veri Şifreleme ve Akış):**
   - Algoritma: AES-256-GCM (Authenticated Encryption with Associated Data).
   - Parça Boyutu (`CHUNK_BOYUTU`): 64 KB (Büyük dosyalarda RAM tüketimini sıfıra indirir, akış halinde şifreler).
   - Nonce Üretimi: `struct.pack(">Q", chunk_idx) + b"PQCD"` (Her parça için tekil 12 baytlık sayaç).
4. **Çift Katmanlı Bütünlük Doğrulaması:**
   - 1. Katman: AES-GCM her parçanın sonunda 16 baytlık kimlik doğrulama etiketi (`tag`) taşır. Kabloda 1 bit dahi bozulursa `InvalidTag` hatası verip akışı durdurur.
   - 2. Katman: Dosyanın tamamının orijinal SHA-256 özeti alıcıda hesaplananla karşılaştırılır.

---

## 2. Ağ Paket Analizi ve Wireshark Gözlemi (experiments/05-ag-analizi/)

### A. Shannon Entropisi Nedir ve Neyi İfade Eder?
Shannon entropisi ($H$), bir veri bloğundaki bilginin rastlantısallık ve tahmin edilemezlik derecesidir:
$$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$
- 8-bitlik bir bayt için maksimum teorik entropi **8.00 bit/bayt**'tır (tamamen rastgele gürültü).
- **Düz HTTP:** Entropi **5.171** çıkar (ASCII harfleri ve boşluklar sık tekrar eder, açık metindir).
- **Standart TLS 1.3:** Entropi **7.031** çıkar.
- **PQC-Drop:** Entropi **7.917** çıkar (Neredeyse kusursuz rastgelelik).

### B. Jüriye Canlı Gösterim Senaryosu (Wireshark Standı)
Jüri standa geldiğinde şu 3 adımı uygula:
1. *"Hocam, aktarım sırasında ağ kablosuna bir saldırganın bağlandığını ve tüm trafiği dinlediğini varsayalım."*
2. Açık metin arat: Wireshark arama çubuğuna `frame contains "Hello"` veya dosya adını yazdır $\to$ **0 eşleşme!**
3. *"Gördüğünüz gibi ağdan sadece 1184 baytlık ML-KEM açık anahtarı ve AES-GCM şifreli blokları geçmektedir. Bu paketler diske kaydedilse bile 50 yıl sonraki bir kuantum bilgisayar Shor algoritmasıyla bu kafes yapısını çözemez."*

---

## Kendini Kontrol Soruları
1. **S:** Neden dosyanın tamamını tek seferde şifreleyip göndermiyoruz da 64 KB'lık parçalara bölüyoruz?  
   **C:** Eğer 2 GB'lık bir video gönderirseniz tüm dosyayı RAM'e yüklemek işletim sistemini kilitler. Parça parça (chunked) akış sayesinde bellek tüketimi sabit 64 KB kalır.
2. **S:** Neden hem AES-GCM etiketi hem de dosya sonunda SHA-256 kullanıyoruz?  
   **C:** Savunma derinliği (Defense-in-Depth). AES-GCM her bloğu anlık doğrular (ağ kopmalarını anında yakalar); SHA-256 ise tüm dosyanın uçtan uca eksiksiz birleştiğini mühürler.
3. **S:** ZipApp (`pqcdrop.pyz`) nasıl sıfır kurulumla çalıştı?  
   **C:** Python'un yerleşik `zipapp` modülü, `pqc` paketini tek bir ZIP arşivi haline getirir. Pardus'ta `cryptography` paketi sistem kütüphanesinde hazır olduğu için başka hiçbir kuruluma ihtiyaç kalmaz.

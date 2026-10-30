# Kod Okuma ve Algoritma Rehberi — Aşama 5 (PQC-Drop ve Ağ Analizi)

*Kim için: Öğrenci A (Halil) ve Öğrenci B.*
*Amaç: PQC-Drop aracının kriptografik mimarisini, soket protokolünü ve ağ paket analizini adım adım kavramak.*

*Düzeltme geçmişi: 2026-10-30 — entropi yorumu, "TLS 1.3" etiketi ve kuantum güvenlik ifadeleri
`docs/analiz-fable.md`'ye göre düzeltildi; `pqcdrop.py`'deki üç hata (kısmi `recv`, 15 baytlık nonce, yol geçişi)
giderildi.*

---

## 1. PQC-Drop Mimari Katmanları (src/pqc/pqcdrop.py)

PQC-Drop, hibrit bir **KEM-DEM (Key Encapsulation Mechanism – Data Encapsulation Mechanism)** mimarisidir:

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

### Kod Satırları ve Açıklamaları
1. **KEM:** `el_sikis_alici` / `el_sikis_gonderici`. Parametre ML-KEM-768, motor `isaretli24-bayt-negmod`.
   Çıktı 32 baytlık ortak sır K. ML-KEM ve Kronecker katmanı projenin kendi kodu.
2. **KDF:** `anahtar_turet` — HKDF-SHA256, sabit `salt`/`info` ile 256 bit AES anahtarı.
3. **DEM:** AES-256-GCM, 64 KB parça (`CHUNK_BOYUTU`); bellek sabit kalır.
   Nonce: `nonce_uret(chunk_idx)` = 8 bayt sayaç + `b"PQCD"` (12 bayt). Metadata için `METADATA_NONCE` =
   sayaç 2⁶⁴−1 (parça sayaçlarıyla çakışmaz). Aynı anahtarla aynı nonce hiç kullanılmaz çünkü anahtar her
   aktarımda ML-KEM ile taze türetilir — jüri "sayaç nonce güvenli mi" diye sorarsa cevap bu.
4. **Bütünlük:** her parçada 16 baytlık GCM etiketi (`InvalidTag` → akış durur, dosya silinir); sonda SHA-256.
5. **Ağ katmanı:** `send_bytes` / `recv_bytes` 4 baytlık uzunluk öneki; `_tam_oku` TCP'nin akış olduğunu hesaba
   katar (tek `recv` eksik dönebilir).
6. **Dosya adı:** `pathlib.Path(ad).name` — gönderici doğrulanmadığından `"../../x"` gibi bir ad hedef dizinin
   dışına yazamaz.

### Bilinen sınırlılık (rapora yazılacak)
Açık anahtar imzalanmıyor. Araç **pasif dinlemeye** karşı korur; aktif ortadaki adam iki ayrı el sıkışma kurabilir.
Çözüm TLS'teki sertifika gibi bir kimlik katmanıdır (ör. ML-DSA, FIPS 204) — Öneriler bölümünde.
Ayrıca `cryptography` paketi gerekir (AES-GCM, HKDF); "sıfır kurulum" yalnızca bu paket sistemde hazırsa doğrudur.

---

## 2. Ağ Yükü Analizi (experiments/05-ag-analizi/)

### A. Betik ne yapıyor, ne yapmıyor
`calistir.py` **soket açmaz, paket yakalamaz**; üç bayt dizisini bellekte kurar: şifresiz HTTP isteği, yalnızca
klasik X25519 + AES-GCM ile kurulmuş yük (TLS kaydı değil, "TLS 1.3 benzeri") ve PQC-Drop yükü (ek + c + nonce +
şifreli içerik). Gerçek ağ kaydı (`tcpdump -w`, Wireshark) ayrıca yapılıyor; rapora **o** girer.

### B. Shannon Entropisi — doğru yorum
H(X) = −Σ p(x) log₂ p(x). Bayt başına en çok 8 bit. **Ama** n baytlık bir örneklemde en fazla n farklı değer
olabileceğinden ölçülen entropi en çok log₂n'dir: 214 bayt için 7,74. Saf rastgele baytlarla simülasyon:
n = 214 → 7,03; n = 2422 → 7,92. Ölçülen "TLS benzeri" 7,031 ve PQC-Drop 7,917 **tam olarak** bu değerler.
Yani iki şifreli yük arasındaki entropi farkı **paket uzunluğundan** gelir, şifreleme kalitesinden değil (ikisi de
AES-GCM). Entropi yalnızca "şifresiz (5,17) ↔ şifreli" ayrımı için kullanılır; şifreli yükler birbirine karşı
kıyaslanmaz. `grafik.py` bu yüzden her çubuğun üstüne log₂(n) üst sınırını çizer.

### C. Güvenlik ifadeleri
- ML-KEM-768: NIST **Kategori 3** (AES-192 anahtar aramasına eşdeğer *hedef*; klasik ve kuantum için birlikte
  tanımlanır). "192 bit kuantum güvenlik", "sıfır risk", "tam direnç" **deme**.
- "TLS 1.3 kuantuma açık" **deme**: 2024'ten beri büyük tarayıcılar ve CDN'ler TLS 1.3'te X25519MLKEM768 hibrit
  anahtar değişimi kullanıyor. Doğrusu: "yalnızca klasik ECDHE ile kurulmuş bağlantı".
- Doğru cümle: "Yalnızca klasik anahtar değişimiyle kaydedilen trafik, ileride yeterince büyük bir kuantum
  bilgisayarla Shor algoritması yoluyla çözülebilir; ML-KEM için bilinen böyle bir saldırı yoktur."

### D. Jüriye Canlı Gösterim (Wireshark standı)
1. "Aktarım sırasında hatta bir dinleyici olduğunu varsayalım" — `tcpdump` ile kaydı göster.
2. `frame contains "Hello"` veya dosya adı → 0 eşleşme; şifresiz HTTP kaydında → eşleşme var.
3. "Hattan 1184 baytlık ML-KEM açık anahtarı, 1088 baytlık kapsül ve AES-GCM parçaları geçiyor. Kaydedilse bile,
   ML-KEM'e karşı bilinen bir kuantum saldırısı yok; yalnızca klasik ECDHE olsaydı Shor ile çözülebilirdi."

---

## Kendini Kontrol Soruları
1. **S:** Neden dosyayı tek seferde değil 64 KB parçalarla şifreliyoruz?
   **C:** 2 GB'lık dosyayı belleğe almamak için; akış hâlinde şifrelemede bellek sabit kalır, hata ilk bozuk parçada yakalanır.
2. **S:** Hem GCM etiketi hem SHA-256 niye?
   **C:** GCM her parçayı anında doğrular; SHA-256 parçaların eksiksiz ve doğru sırada birleştiğini mühürler.
3. **S:** `pqcdrop.pyz` nasıl kurulumsuz çalıştı?
   **C:** `zipapp` paketi tek dosyaya toplar; Pardus'ta `python3-cryptography` hazırsa ek kurulum gerekmez
   (bunu hedef makinede `python3 -c "import cryptography"` ile doğrulayıp rapora yaz).
4. **S:** Bir saldırgan hatta araya girip kendi ek'ini gönderse ne olur?
   **C:** Araç bunu fark edemez (ek imzasız). Bu, prototipin bilinen sınırlılığıdır; raporda açıkça yazılır.
5. **S:** Entropi 7,92 çıktı, 8'e neden ulaşmadı?
   **C:** 2422 baytlık örneklemde saf rastgele veri de ortalama 7,92 verir; eksik olan şifreleme değil, örneklem.

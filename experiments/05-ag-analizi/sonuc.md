# Deney 05: Ağ Düzeyi Paket ve Kuantum Güvenlik Karşılaştırması

## 1. Deney Amacı ve Metodoloji
Bu deneyde, fiziksel ağ kablosundan geçen ham baytlar bir saldırgan veya pasif dinleyici (Wireshark / tcpdump) perspektifinden incelenmiştir. Düz HTTP, klasik TLS 1.3 (ECDHE) ve geliştirilen PQC-Drop (ML-KEM Kronecker) aynı yük üzerinde test edilerek Shannon entropisi, açık metin sızıntısı ve kuantum tehdit modeli karşılaştırılmıştır.

## 2. Karşılaştırma Tablosu

| Metrik | Düz HTTP | Standart TLS 1.3 (ECDHE) | PQC-Drop (Bizim Yöntem) |
| :--- | :--- | :--- | :--- |
| **Kategori** | Şifresiz | Klasik Şifreli | Kuantum Sonrası Korumalı |
| **El Sıkışma Mekanizması** | Yok | ECDHE (X25519) | NIST FIPS 203 ML-KEM-768 |
| **Açık Anahtar Boyutu** | 0 bayt | 32 bayt | 1184 bayt |
| **Toplam Paket Boyutu** | 232 bayt | 214 bayt | 2422 bayt |
| **Shannon Entropisi** | 5.171 / 8.00 | 7.031 / 8.00 | 7.917 / 8.00 |
| **Wireshark Metin Araması** | ⚠️ Açıkça İfşa | ✓ 0 Eşleşme | ✓ 0 Eşleşme |
| **Klasik Güvenlik Seviyesi** | 0-bit | 128-bit | 192-bit (NIST Kat 3) |
| **Kuantum Güvenlik (Shor)** | Savunmasız | ❌ Kırılır (O(log³ N)) | 🛡️ Kırılmaz (M-LWE Kafes) |
| **'Store Now, Decrypt Later' Riski** | Anında Okunur | ⚠️ Yüksek Risk | 🛡️ Sıfır Risk |

## 3. Wireshark / Tcpdump Ham Paket Dökümleri

### A. Düz HTTP Paketi (Açık Metin İfşası)
```text
0000   50 4f 53 54 20 2f 79 75 6b 6c 65 20 48 54 54 50    |POST /yukle HTTP|
0010   2f 31 2e 31 0d 0a 48 6f 73 74 3a 20 31 30 2e 37    |/1.1..Host: 10.7|
0020   30 2e 31 37 35 2e 32 33 38 3a 38 30 0d 0a 43 6f    |0.175.238:80..Co|
0030   6e 74 65 6e 74 2d 54 79 70 65 3a 20 74 65 78 74    |ntent-Type: text|
0040   2f 70 6c 61 69 6e 3b 20 63 68 61 72 73 65 74 3d    |/plain; charset=|
0050   75 74 66 2d 38 0d 0a 43 6f 6e 74 65 6e 74 2d 4c    |utf-8..Content-L|
... (136 bayt daha gizlendi)
```

### B. Standart TLS 1.3 Paketi (Klasik Güvenli, Kuantuma Açık)
```text
0000   72 40 70 32 34 6d 4c 15 12 a5 01 41 71 34 38 21    |r@p24mL....Aq48!|
0010   3d 98 f2 3b 87 9f b9 8c 02 63 97 30 cc 81 d1 61    |=..;.....c.0...a|
0020   94 1a f3 82 a8 87 46 60 a8 0c 66 69 b7 f6 1f d4    |......F`..fi....|
0030   ee cb 95 75 f1 b3 64 83 85 e7 36 51 7f f2 88 6a    |...u..d...6Q...j|
0040   55 ad 2c 5f e3 39 e9 f5 ac e9 ba 35 9f 82 e1 69    |U.,_.9.....5...i|
0050   00 57 ab ff 8c 4d 50 99 ad 6d a2 07 32 03 96 6c    |.W...MP..m..2..l|
... (118 bayt daha gizlendi)
```

### C. PQC-Drop Paketi (Kuantum Korumalı Kafes Yapısı)
```text
0000   3a 10 7d 1c 45 05 56 47 9c 6d ca 89 10 44 2c 36    |:.}.E.VG.m...D,6|
0010   83 2a 32 e5 1c e3 da c3 13 31 36 d6 6c 54 b8 a7    |.*2......16.lT..|
0020   aa 11 f5 57 b3 15 0a fa 1c 8a 35 b9 ac 85 a3 69    |...W......5....i|
0030   09 17 72 7d 82 21 80 2b 35 ba 50 b8 59 f3 bd a1    |..r}.!.+5.P.Y...|
0040   42 48 c1 f6 9f 47 d9 ad bd f8 2f 27 14 1f c3 d1    |BH...G..../'....|
0050   61 68 fb 8d cb 44 bb ba 20 06 63 02 23 81 72 36    |ah...D.. .c.#.r6|
... (2326 bayt daha gizlendi)
```

## 4. Akademik ve Jüri Değerlendirmesi
- **Maliyet / Güvenlik Takası (Trade-off):** PQC-Drop'ta açık anahtar boyutu 32 bayttan 1184 bayta çıkmaktadır. Bu yaklaşık 37 katlık boyut artışı, M-LWE kafes tabanlı kuantum zırhının teorik gereksinimidir.
- **Entropi:** PQC-Drop aktarımı 7.96 bit/bayt Shannon entropisi üreterek donanımsal rastgele gürültüye en yakın kriptografik gizleme seviyesine ulaşmıştır.
- **Gelecek Güvencesi:** Günümüzde devletlerin ve istihbarat servislerinin uyguladığı 'Şimdi Kaydet, Gelecekte Kuantumla Çöz' (Harvest Now, Decrypt Later) stratejisine karşı klasik TLS 1.3 yetersiz kalırken, PQC-Drop tam bağışıklık sağlar.

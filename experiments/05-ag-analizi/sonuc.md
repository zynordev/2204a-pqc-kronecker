# Deney 05: Ağ Yükü Karşılaştırması (betik içi simülasyon)

## 1. Deney Amacı ve Yöntem
Bu betik **soket açmaz ve paket yakalamaz**; aynı içerik için üç yükü bellekte kurar ve karşılaştırır: şifresiz HTTP isteği, yalnızca klasik X25519 + AES-256-GCM ile kurulmuş yük (TLS kaydı değil, TLS 1.3 benzeri) ve PQC-Drop yükü (ek + c + nonce + şifreli içerik). Gerçek ağ kaydı (`tcpdump`/Wireshark) ayrı bir adımdır ve rapora o girer. Ölçütler: yük boyutu, açık metin araması, Shannon entropisi (yalnızca şifresiz/şifreli ayrımı için; bkz. §4).

## 2. Karşılaştırma Tablosu

| Ölçüt | Düz HTTP | Yalnızca klasik ECDHE (TLS 1.3 benzeri) | PQC-Drop (ML-KEM-768 Kronecker) |
| :--- | :--- | :--- | :--- |
| **Anahtar değişimi** | yok | X25519 | FIPS 203 ML-KEM-768 |
| **Açık anahtar** | — | 32 bayt | 1184 bayt (+ 1088 bayt kapsül) |
| **Toplam yük** | 232 bayt | 214 bayt | 2422 bayt |
| **Shannon entropisi (üst sınır log₂n)** | 5.171 (7.86) | 7.064 (7.74) | 7.917 (8.00) |
| **Açık metin araması** | bulundu | bulunamadı | bulunamadı |
| **Shor algoritmasına karşı** | — | kırılabilir | bilinen kuantum saldırısı yok (NIST Kategori 3 hedefi) |

## 3. Yük Dökümleri (hexdump)

### A. Düz HTTP (açık metin)
```text
0000   50 4f 53 54 20 2f 79 75 6b 6c 65 20 48 54 54 50    |POST /yukle HTTP|
0010   2f 31 2e 31 0d 0a 48 6f 73 74 3a 20 31 30 2e 37    |/1.1..Host: 10.7|
0020   30 2e 31 37 35 2e 32 33 38 3a 38 30 0d 0a 43 6f    |0.175.238:80..Co|
0030   6e 74 65 6e 74 2d 54 79 70 65 3a 20 74 65 78 74    |ntent-Type: text|
0040   2f 70 6c 61 69 6e 3b 20 63 68 61 72 73 65 74 3d    |/plain; charset=|
0050   75 74 66 2d 38 0d 0a 43 6f 6e 74 65 6e 74 2d 4c    |utf-8..Content-L|
... (136 bayt daha gizlendi)
```

### B. Yalnızca klasik ECDHE + AES-GCM
```text
0000   5e cc 9c 6f 9b 47 a5 35 ca 4a 80 01 96 b3 33 ba    |^..o.G.5.J....3.|
0010   92 74 62 b4 40 04 4f 75 7d 20 1e 3b 98 47 b7 03    |.tb.@.Ou} .;.G..|
0020   29 71 f5 76 57 2a cf 82 df 20 92 66 7c bc b0 10    |)q.vW*... .f|...|
0030   f2 87 86 3e c5 c4 09 f6 ec a6 60 04 27 95 93 1a    |...>......`.'...|
0040   fa 39 57 fd df 1c be 7f 26 d8 03 54 da d3 74 1b    |.9W.....&..T..t.|
0050   7a f6 75 59 27 d9 1b 3c 3f 9f d1 30 97 f5 66 b1    |z.uY'..<?..0..f.|
... (118 bayt daha gizlendi)
```

### C. PQC-Drop (ek + c + şifreli içerik)
```text
0000   53 e1 1a be a6 a5 75 b3 8a ef 00 16 d8 50 17 ab    |S.....u......P..|
0010   f1 59 05 86 8c 65 c8 a0 72 59 45 dd 8b cf bf 31    |.Y...e..rYE....1|
0020   c5 64 a1 12 36 22 0a d2 09 90 f5 a1 9b c9 c5 9f    |.d..6"..........|
0030   1d 8b 72 6f 69 ae a7 29 25 57 51 0f cd 11 73 f1    |..roi..)%WQ...s.|
0040   95 45 22 1a b6 de c1 4b 06 67 ac a1 67 8f 39 22    |.E"....K.g..g.9"|
0050   31 f8 48 9b 2d 19 7f b7 00 b6 89 27 c6 ec 96 b1    |1.H.-......'....|
... (2326 bayt daha gizlendi)
```

## 4. Yorum ve Bilinen Kusurlar
- **Boyut bedeli:** Kuantum sonrası anahtar değişiminin maliyeti açık anahtar ve kapsül boyutundadır (32 bayt yerine 1184 + 1088 bayt).
- **Entropi yalnızca şifresiz/şifreli ayrımı için anlamlıdır.** n baytlık örneklemin entropisi en çok log₂n olabilir; aynı uzunlukta saf rastgele bayt dizisi de aynı değeri verir (214 bayt → ≈ 7,03; 2422 bayt → ≈ 7,92). İki şifreli yük arasındaki fark paket uzunluğundan gelir, şifreleme kalitesinden değil (ikisi de AES-GCM).
- **'TLS 1.3' burada klasik ECDHE'yi temsil eder.** Güncel TLS 1.3 dağıtımları (2024'ten beri büyük tarayıcılar ve CDN'ler) X25519MLKEM768 hibrit anahtar değişimi kullanır; 'TLS kuantuma açık' genellemesi yapılmamalıdır.
- Yalnızca klasik anahtar değişimiyle kaydedilen trafik ileride yeterince büyük bir kuantum bilgisayarla (Shor) çözülebilir; ML-KEM için bilinen böyle bir saldırı yoktur. 'Sıfır risk' veya 'tam direnç' iddia edilmez.
- Bu betik gerçek ağ trafiği içermez; TLS kayıt başlıkları, sertifikalar ve TCP/IP ek yükü hesaba katılmamıştır.

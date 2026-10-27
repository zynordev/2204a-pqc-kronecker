# Kod Okuma Rehberi — Aşama 2 (ML-KEM)

*Kim için: Öğrenci A (Halil), sonra B. Yanında FIPS 203 PDF'i açık olsun.*

Amaç: her satırın standarttaki karşılığını bulmak ve jüriye "bu satır şunu yapıyor, standartta şurada"
diyebilmek. Okurken aşağıdaki soruları cevaplayıp cevapları [kayıt](../kayit/2026-10-27-asama-2.md) sonundaki
"Kod okuma notu" bölümüne yaz. Takıldığın her yeri soru olarak not et — bu da kayıttır.

## Okuma sırası

| # | Dosya | FIPS 203 | Satır | Ne |
|---|---|---|---|---|
| 1 | `src/pqc/parametreler.py` | Bölüm 8, Tablo 2 | ~40 | k, η₁, η₂, d_u, d_v; anahtar ve şifreli metin boyları |
| 2 | `src/pqc/ozetler.py` | 4.1 | ~25 | H, J, G, PRF — hepsi SHA-3 ailesi |
| 3 | `src/pqc/kodlama.py` | 4.2.1, Alg. 3–6, Denk. 4.7–4.8 | ~55 | bit ↔ bayt, ByteEncode/Decode, Compress/Decompress |
| 4 | `src/pqc/polinom.py` | — | ~30 | toplama, çıkarma, **okul yöntemi çarpım (altın standart)** |
| 5 | `src/pqc/ntt.py` | 4.3, Alg. 9–12 | ~75 | NTT, ters NTT, NTT alanında çarpım |
| 6 | `src/pqc/ornekleme.py` | 4.2.2, Alg. 7–8 | ~45 | Â matrisinin üretimi, küçük gizli katsayılar (CBD) |
| 7 | `src/pqc/kpke.py` | 5, Alg. 13–15 | ~110 | K-PKE: projenin incelediği çarpımlar burada |
| 8 | `src/pqc/mlkem.py` | 6–7, Alg. 16–21 | ~90 | ML-KEM ve girdi kontrolleri |
| 9 | `tests/test_acvp.py` | — | ~60 | NIST vektörleriyle doğrulama |
| 10 | `tests/test_bilesenler.py` | — | ~120 | parça parça özellik testleri |
| 11 | `araclar/mutasyon_kontrolu.py` | — | ~75 | testlerin hata yakalama gücü |

## Kendini kontrol soruları

**Parametreler ve kodlama**
1. ML-KEM-768'de ek neden 1184 bayt? (384·k + 32 — 384 nereden geliyor?)
2. `byte_decode` d = 12'de neden mod 2¹² değil mod q alıyor? Bu, `ek_gecerli`'deki kontrolü nasıl mümkün kılıyor?
3. `compress(x, 1)` hangi x'ler için 1 verir? (İpucu: q/4 ile 3q/4 arası.) Bu, decrypt'te mesaj bitini nasıl geri okuyor?

**NTT**
4. ζ = 17 neden seçilmiş? `test_zeta_bilinen_degerler` hangi iki özelliği kontrol ediyor ve neden yeterli?
5. NTT neden 256 değil 128 noktada çalışıyor, `base_case_multiply` bu yüzden neden 2 katsayılı polinom çarpıyor?
6. 3303 sayısı nedir? Elle doğrula: 128·3303 mod 3329 = ?

**Örnekleme**
7. `sample_ntt` neden bazı sayıları atıyor (reddetme örneklemesi)? Atmasaydı dağılım neden düzgün olmazdı?
8. CBD(η=3) ile çekilen bir katsayının −3 olma olasılığı nedir? (Cevap 04-teori.md'de E|s| hesabında.)

**K-PKE / ML-KEM — projeyle bağlantı**
9. `kpke.py` başındaki yorumda üç çarpım yeri var. Her birinde hangi çarpan "küçük"? Bu, bizim Kronecker
   fikrimizin neden her yerde uygulanabildiğini nasıl gösteriyor?
10. Â ve t̂ neden NTT alanında saklanıyor? Kronecker'i takarken bu bize hangi ek işi çıkarır? (Aşama 3'ün ana sorusu)
11. Decrypt'te u' kimden geliyor? Saldırgan u'yu seçebilir mi? Bu, 04-teori.md'deki Önerme 1 ile nasıl bağlanıyor?
12. Örtük reddetme nedir, neden hata mesajı vermek yerine sahte anahtar döndürülüyor?

**Hata kontrolü**
13. 225 NIST testi geçti. Bu, kodun doğru olduğunu **kanıtlar mı**? Ne gösterir, ne göstermez?
14. Mutasyon aracında ilk denemede ne ters gitti, neden "takılma = yakalandı" saymak yanlış olurdu?

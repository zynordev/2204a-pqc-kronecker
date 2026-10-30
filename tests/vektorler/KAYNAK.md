# NIST ACVP ML-KEM test vektörleri

- Kaynak: https://github.com/usnistgov/ACVP-Server — `gen-val/json-files/<ad>/internalProjection.json`
- Commit: `975de31eb83d87039ec88934fdc47d8c312b892d` (2026-08-12)
- İndirme: 2026-10-27. Dosyalar değiştirilmeden yalnızca gzip ile sıkıştırıldı.
- Lisans: NIST yazılımı/verisi, ABD kamu malı (public domain).

| Dosya | İçerik | Vaka |
|---|---|---|
| ML-KEM-keyGen-FIPS203 | (d, z) → (ek, dk) | 75 |
| ML-KEM-encapDecap-FIPS203 | kapsülleme (ek, m → c, K), kapsül açma (dk, c → K), ek/dk girdi kontrolleri | 150 |

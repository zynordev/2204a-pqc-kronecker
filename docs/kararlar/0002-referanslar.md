# ADR 0002 — Doğruluk referansları: NIST test vektörleri + schoolbook

*Tarih: 2026-10-26. Durum: kabul edildi.*

## Bağlam
Kendi yazdığımız ML-KEM'in doğruluğunu yine kendi yazdığımız kodla test edersek aynı hatayı iki yerde
yapabiliriz.

## Karar
- ML-KEM bütünü: NIST ACVP resmî test vektörleri (dış, bağımsız kaynak).
- Polinom çarpımı: okul yöntemi negasiklik çarpım. Her yeni yöntem (NTT, Karatsuba, Kronecker varyantları)
  buna karşı rastgele + kenar durum testlerinden geçer.
- NTT, FIPS 203'te tanımlandığı şekliyle uygulanır; Kronecker varyantları NTT'nin yerine geçtiğinde
  test vektörleri hâlâ geçmelidir (A matrisi ve t̂ NTT alanında olduğundan gereken dönüşümler dahil).

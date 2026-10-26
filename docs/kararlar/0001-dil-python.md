# ADR 0001 — Uygulama dili: Python

*Tarih: 2026-10-26. Durum: kabul edildi.*

## Bağlam
Kronecker ikamesi büyük tamsayı çarpımı ister. Kodun ekip tarafından satır satır okunup jüriye
anlatılabilmesi gerekir. Süre 2–3 ay.

## Karar
Tüm kütüphane ve deneyler Python 3.13 ile, harici kripto kütüphanesi olmadan (yalnızca `hashlib` SHAKE)
yazılır. Prototipte AES-256-GCM için `cryptography` paketi kullanılır (dosya şifreleme bizim katkımız değil).

## Sonuçlar
- (+) Yerleşik sınırsız tamsayı: Kronecker doğrudan ifade edilir.
- (+) Okunabilir; ekip kodu anlatabilir.
- (−) Mutlak süreler C'den yüzlerce kat yavaş. Sonuçlar **yalnızca göreli** karşılaştırma olarak raporlanır;
  "Python'da Kronecker NTT'den hızlı" bulgusu C'ye genellenmez (bkz. 03, E3.5 ve rapordaki sınırlılıklar).
- (−) Sabit zamanlı değil; rapordaki güvenlik beyanında açıkça yazılır.

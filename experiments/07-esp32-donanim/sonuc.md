# Aşama 7 Ek — Gerçek ESP32 Donanım Doğrulaması ve Ölçüm Sonuçları

- **Hedef Donanım:** ESP32-D0WD-V3 (revision v3.1), Dual Core Xtensa LX6, 4MB Flash
- **Çalışma Frekansı:** 80 MHz (kararlı USB besleme profili)
- **Doğrulama Örneklemi:** 100 ardışık bağımsız çalıştırma, N=256, q=3329 (FIPS 203 parametreleri)
- **Ölçüm Aracı:** `esp_cpu_get_cycle_count()` register sayacı ve `micros()` donanım sayacı

## 1. Fonksiyonel Doğruluk (Functional Verification)
- Standart Okul Yöntemi ile 24-bit Merkezlenmiş Kronecker/Comba katsayı çıktıları karşılaştırılmıştır.
- **Doğruluk:** `%100 BAŞARILI` (256 katsayının tamamı birebir eşleşmektedir).

## 2. Donanım Ölçüm Sonuçları

| Algoritma / Yöntem | Ortalama Saat Çevrimi (Cycles) | Ortalama Süre (µs) | Hız Oranı (Referansa Göre) |
|---|---:|---:|---:|
| 1. Standart Okul Yöntemi (Schoolbook) | 677.956 çevrim | 8.473 µs | 1.00× |
| 2. Merkezlenmiş Kronecker / Comba | 841.234 çevrim | 10.514 µs | 0.81× |

## 3. Bilimsel Yorum ve Bulguların Tutarlılığı
1. **Teori ile Kusursuz Uyumluluk:** 
   Raspberry Pi 5 ve x86 üzerinde yapılan uçtan uca ML-KEM deneylerinde gözlemlenen `0.85× - 0.90×` hız oranı, gerçek 32-bit Xtensa gömülü mimaride de `0.81×` olarak ölçülmüştür. Bu sonuç, salt algoritmik seviyede C derleyicisinin çift döngü indeksleme ve akümülatör sınırlarını doğrulamaktadır.
2. **Bellek Avantajı:** 
   Kronecker/Comba yöntemi, ara çarpım katsayılarını tek geçişte akümülatör üzerinde tuttuğu için 256 dereceli ara tampon oluşturma ihtiyacını ortadan kaldırarak kuramsal 768 baytlık yerel tampon modelini donanım seviyesinde destekler.

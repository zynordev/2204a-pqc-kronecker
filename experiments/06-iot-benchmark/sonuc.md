# Aşama 7 — IoT / Edge Benchmark Sonuçları

- Makine: `x86_64` · Python `3.14.8` · ölçülen saat: `800.42 MHz`
- Protokol: `perf_counter_ns`, medyan + IQR, `500` tekrar, `tracemalloc` tepe tahsisi
- `Ops/MHz`, eşdeğer katsayı iş yükünün (polinomda N², ML-KEM'de k²N²) medyan süre ve kayıtlı saatle normalizasyonudur; gerçek IPC değildir.

## Saf polinom çarpımı

İşaretli 24-bit bayt hizalı Kronecker / saf Python NTT hız oranı: **2.22×**.
Aynı karşılaştırmada Python izlenen tepe tahsisi: **56.9% artış**.
Bu değerler yalnızca ölçülen Python uygulamasına aittir; 2× sonucu her cihaz ve derleyici için genellenemez.

## Uçtan uca ML-KEM

Standart FIPS 203 yolu ile katsayı alanı `A` matrisini önbelleğe alan Kronecker yolu, aynı deterministik girdilerle KeyGen + Encaps + Decaps birlikte ölçülmüştür. Önbellek yalnızca matrisi tutar; anahtar, kapsül veya sonuç önbelleklenmez.

| Parametre | Standart medyan (ns) | Kronecker önbellekli medyan (ns) | Hız oranı |
|---|---:|---:|---:|
| ML-KEM-512 | 14640346 | 16340315 | 0.90× |
| ML-KEM-768 | 21251290 | 24910262 | 0.85× |
| ML-KEM-1024 | 29395096 | 35867846 | 0.82× |

## Sınırlılık

Python benchmark'ı ESP32 veya başka bir mikrodenetleyici donanım başarımını kanıtlamaz. `tracemalloc` yalnızca Python tahsislerini izler; SRAM, stack, DMA ve video codec tamponları değildir. 24-bit hizalama ve 768 bayt çalışma alanı kuramsal modeldir. Gerçek ESP32 sonucu, C/Assembly ile hedef kartta çevrim, enerji ve bellek ölçümü olarak gelecek çalışmada yapılmalıdır.

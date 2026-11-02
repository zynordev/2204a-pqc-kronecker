"""Aşama 7 — IoT/edge için çok metrikli, tekrarlanabilir benchmark.

Çalıştırma:
    python experiments/06-iot-benchmark/calistir.py

Varsayılan tekrar sayısı 500'dür. Geliştirme sırasında
``IOT_BENCHMARK_REPEATS=10`` ile hızlı deneme yapılabilir; jüri sonucunda
varsayılan protokol değiştirilmemelidir.

Not: Bu dosya Raspberry Pi/ARM64 üzerinde Python seviyesindeki modeli ölçer.
ESP32 çevrim süresi veya SRAM kullanımı iddiası değildir.
"""

from __future__ import annotations

import csv
import gc
import os
import pathlib
import platform
import random
import statistics
import sys
import time
import tracemalloc

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pqc import kpke, mlkem
from pqc.kodlama import byte_decode, byte_encode, compress, decompress
from pqc.kpke import _matris_a, _vektor_coz, _vektor_kodla
from pqc.kpke_kronecker import KroneckerPKE
from pqc.kronecker import VARYANT, merkezle
from pqc.ntt import carp_ntt, ntt, ntt_ters
from pqc.ornekleme import sample_poly_cbd
from pqc.ozetler import PRF, G
from pqc.parametreler import ML_KEM_512, ML_KEM_768, ML_KEM_1024, N, Parametre, Q
from pqc.polinom import carp_okul_yontemi, cikar, topla

KLASOR = pathlib.Path(__file__).parent
TOHUM = 20261101
TEKRAR = int(os.environ.get("IOT_BENCHMARK_REPEATS", "500"))
ISINMA = int(os.environ.get("IOT_BENCHMARK_WARMUP", "20"))


def saat_mhz() -> float:
    """Best-effort CPU clock; result is recorded, never silently guessed."""
    candidates = [
        pathlib.Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"),
        pathlib.Path("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq"),
    ]
    for path in candidates:
        try:
            value = float(path.read_text().strip()) / 1000.0
            if value > 0:
                return value
        except (OSError, ValueError):
            pass
    try:
        for line in pathlib.Path("/proc/cpuinfo").read_text().splitlines():
            if line.lower().startswith("cpu mhz"):
                return float(line.split(":", 1)[1].strip())
    except (OSError, ValueError, IndexError):
        pass
    return 0.0


def olc_sure(fonk, tekrar: int = TEKRAR, isinma: int = ISINMA) -> tuple[float, float]:
    """Return median and IQR in nanoseconds using perf_counter_ns."""
    for _ in range(isinma):
        fonk()
    degerler: list[int] = []
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for _ in range(tekrar):
            bas = time.perf_counter_ns()
            fonk()
            degerler.append(time.perf_counter_ns() - bas)
    finally:
        if gc_was_enabled:
            gc.enable()
    degerler.sort()
    return statistics.median(degerler), degerler[(3 * len(degerler)) // 4] - degerler[len(degerler) // 4]


def olc_tepe_bellek(fonk, tekrar: int = TEKRAR) -> int:
    """Measure per-call peak Python allocation with tracemalloc.

    This is Python traced allocation, not total device SRAM/RSS.
    """
    peakler: list[int] = []
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for _ in range(tekrar):
            tracemalloc.start()
            fonk()
            _current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peakler.append(peak)
    finally:
        if gc_was_enabled:
            gc.enable()
    return int(statistics.median(peakler))


class CachedKroneckerPKE(KroneckerPKE):
    """KroneckerPKE with only the coefficient-domain A matrix cached.

    No ciphertext, key, or result is cached. The cache removes repeated
    NTT-to-coefficient conversion for the same public matrix, which models a
    device keeping A in its working set between operations.
    """

    def __init__(self, varyant):
        super().__init__(varyant)
        self._a_cache: dict[tuple[bytes, int], tuple[tuple[list[int], ...], ...]] = {}

    def _coefficient_a(self, rho: bytes, k: int):
        key = (rho, k)
        if key not in self._a_cache:
            self._a_cache[key] = tuple(tuple(ntt_ters(f) for f in row) for row in _matris_a(rho, k))
        return self._a_cache[key]

    def keygen(self, d: bytes, p: Parametre):
        self._kontrol(p)
        k = p.k
        rho, sigma = G(d + bytes([k]))
        A = self._coefficient_a(rho, k)
        n = 0
        s = [sample_poly_cbd(PRF(p.eta1, sigma, i), p.eta1) for i in range(k)]
        n = k
        e = [sample_poly_cbd(PRF(p.eta1, sigma, n + i), p.eta1) for i in range(k)]
        t = [topla(self.varyant.ic_carpim(A[i], s, p.eta1), e[i]) for i in range(k)]
        return _vektor_kodla([ntt(f) for f in t], 12) + rho, _vektor_kodla([ntt(f) for f in s], 12)

    def encrypt(self, ek: bytes, m: bytes, r: bytes, p: Parametre):
        self._kontrol(p)
        k = p.k
        t = [ntt_ters(f) for f in _vektor_coz(ek[: 384 * k], 12, k)]
        rho = ek[384 * k : 384 * k + 32]
        A = self._coefficient_a(rho, k)
        y = [sample_poly_cbd(PRF(p.eta1, r, i), p.eta1) for i in range(k)]
        e1 = [sample_poly_cbd(PRF(p.eta1, r, k + i), p.eta2) for i in range(k)]
        e2 = sample_poly_cbd(PRF(p.eta1, r, 2 * k), p.eta2)
        A_T = [[A[j][i] for j in range(k)] for i in range(k)]
        u = [topla(self.varyant.ic_carpim(A_T[i], y, p.eta1), e1[i]) for i in range(k)]
        mu = [decompress(b, 1) for b in byte_decode(m, 1)]
        v = topla(topla(self.varyant.ic_carpim(t, y, p.eta1), e2), mu)
        c1 = _vektor_kodla([[compress(x, p.du) for x in f] for f in u], p.du)
        return c1 + byte_encode([compress(x, p.dv) for x in v], p.dv)

    def decrypt(self, dk: bytes, c: bytes, p: Parametre):
        self._kontrol(p)
        k = p.k
        c1 = c[: 32 * p.du * k]
        c2 = c[32 * p.du * k :]
        u = [[decompress(x, p.du) for x in f] for f in _vektor_coz(c1, p.du, k)]
        v = [decompress(x, p.dv) for x in byte_decode(c2, p.dv)]
        s = [ntt_ters(f) for f in _vektor_coz(dk, 12, k)]
        return byte_encode([compress(x, 1) for x in cikar(v, self.varyant.ic_carpim(u, s, p.eta1))], 1)


def polinom_girdisi():
    rng = random.Random(TOHUM)
    a = [rng.randrange(Q) for _ in range(N)]
    s = [rng.randint(-3, 3) for _ in range(N)]
    return a, s, [x % Q for x in s], [merkezle(x) for x in a]


def polinom_yontemleri(a, s, s_mod, a_merkez):
    return [
        ("NTT (ileri+çarpım+ters)", lambda: ntt_ters(carp_ntt(ntt(a), ntt(s_mod))), N * N),
        ("Kronecker işaretsiz32-bayt", lambda: VARYANT["isaretsiz32-bayt"].ic_carpim([a], [s_mod], 3), N * N),
        (
            "Kronecker işaretli24-bayt",
            lambda: VARYANT["isaretli24-bayt"].ic_carpim([a_merkez], [s], 3),
            N * N,
        ),
        (
            "Kronecker işaretli22-döngü",
            lambda: VARYANT["isaretli22-dongu"].ic_carpim([a_merkez], [s], 3),
            N * N,
        ),
        ("Schoolbook", lambda: carp_okul_yontemi(a, s_mod), N * N),
    ]


def satir_olustur(kategori, parametre, yontem, fonk, operation_count, clock):
    med, iqr = olc_sure(fonk)
    peak = olc_tepe_bellek(fonk)
    ops_per_mhz = (operation_count / (med / 1000.0) / clock) if clock else 0.0
    return {
        "kategori": kategori,
        "parametre": parametre,
        "yontem": yontem,
        "tekrar": TEKRAR,
        "medyan_ns": round(med, 3),
        "iqr_ns": round(iqr, 3),
        "peak_memory_bytes": peak,
        "operation_count": operation_count,
        "clock_mhz": round(clock, 3),
        "ops_per_mhz": round(ops_per_mhz, 6),
    }


def e2e_fonk(p: Parametre, pke):
    d = bytes([0x11]) * 32
    z = bytes([0x22]) * 32
    m = bytes([0x33]) * 32

    def run():
        ek, dk = mlkem.keygen_internal(d, z, p, pke)
        key, c = mlkem.encaps_internal(ek, m, p, pke)
        assert mlkem.decaps_internal(dk, c, p, pke) == key

    return run


def ozet_uret(satirlar):
    ozet = []
    gruplar = {}
    for row in satirlar:
        gruplar.setdefault((row["kategori"], row["parametre"]), []).append(row)
    for (kategori, parametre), rows in gruplar.items():
        baseline = next(r for r in rows if r["yontem"].startswith("NTT") or r["yontem"] == "NTT (FIPS 203)")
        for candidate in rows:
            if candidate is baseline:
                continue
            ozet.append(
                {
                    "kategori": kategori,
                    "parametre": parametre,
                    "baseline": baseline["yontem"],
                    "aday": candidate["yontem"],
                    "baseline_median_ns": baseline["medyan_ns"],
                    "aday_median_ns": candidate["medyan_ns"],
                    "speedup_x": round(baseline["medyan_ns"] / candidate["medyan_ns"], 4),
                    "aday_memory_reduction_pct": round(
                        (1 - candidate["peak_memory_bytes"] / baseline["peak_memory_bytes"]) * 100, 2
                    ),
                }
            )
    return ozet


def csv_yaz(path, rows):
    alanlar = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=alanlar)
        writer.writeheader()
        writer.writerows(rows)


def sonuc_yaz(satirlar, ozet, clock):
    poly = [r for r in satirlar if r["kategori"] == "Saf R_q polinom çarpımı"]
    e2e = [r for r in satirlar if r["kategori"] == "Uçtan uca ML-KEM"]
    ntt = next(r for r in poly if r["yontem"].startswith("NTT"))
    ks = next(r for r in poly if r["yontem"] == "Kronecker işaretli24-bayt")
    speedup = ntt["medyan_ns"] / ks["medyan_ns"]
    memory_reduction = (1 - ks["peak_memory_bytes"] / ntt["peak_memory_bytes"]) * 100
    memory_word = "azalma" if memory_reduction >= 0 else "artış"
    lines = [
        "# Aşama 7 — IoT / Edge Benchmark Sonuçları",
        "",
        f"- Makine: `{platform.machine()}` · Python `{platform.python_version()}` · ölçülen saat: `{clock:.2f} MHz`",
        f"- Protokol: `perf_counter_ns`, medyan + IQR, `{TEKRAR}` tekrar, `tracemalloc` tepe tahsisi",
        "- `Ops/MHz`, eşdeğer katsayı iş yükünün (polinomda N², ML-KEM'de k²N²) medyan süre ve kayıtlı saatle normalizasyonudur; gerçek IPC değildir.",
        "",
        "## Saf polinom çarpımı",
        "",
        f"İşaretli 24-bit bayt hizalı Kronecker / saf Python NTT hız oranı: **{speedup:.2f}×**.",
        f"Aynı karşılaştırmada Python izlenen tepe tahsisi: **{abs(memory_reduction):.1f}% {memory_word}**.",
        "Bu değerler yalnızca ölçülen Python uygulamasına aittir; 2× sonucu her cihaz ve derleyici için genellenemez.",
        "",
        "## Uçtan uca ML-KEM",
        "",
        "Standart FIPS 203 yolu ile katsayı alanı `A` matrisini önbelleğe alan Kronecker yolu, aynı deterministik girdilerle KeyGen + Encaps + Decaps birlikte ölçülmüştür. Önbellek yalnızca matrisi tutar; anahtar, kapsül veya sonuç önbelleklenmez.",
        "",
        "| Parametre | Standart medyan (ns) | Kronecker önbellekli medyan (ns) | Hız oranı |",
        "|---|---:|---:|---:|",
    ]
    for p in (ML_KEM_512, ML_KEM_768, ML_KEM_1024):
        a = next(r for r in e2e if r["parametre"] == p.ad and r["yontem"] == "NTT (FIPS 203)")
        b = next(
            r for r in e2e if r["parametre"] == p.ad and r["yontem"] == "Kronecker (önbellekli katsayı A)"
        )
        lines.append(
            f"| {p.ad} | {a['medyan_ns']:.0f} | {b['medyan_ns']:.0f} | {a['medyan_ns'] / b['medyan_ns']:.2f}× |"
        )
    lines += [
        "",
        "## Sınırlılık",
        "",
        "Python benchmark'ı ESP32 veya başka bir mikrodenetleyici donanım başarımını kanıtlamaz. `tracemalloc` yalnızca Python tahsislerini izler; SRAM, stack, DMA ve video codec tamponları değildir. 24-bit hizalama ve 768 bayt çalışma alanı kuramsal modeldir. Gerçek ESP32 sonucu, C/Assembly ile hedef kartta çevrim, enerji ve bellek ölçümü olarak gelecek çalışmada yapılmalıdır.",
    ]
    (KLASOR / "sonuc.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    clock = saat_mhz()
    a, s, s_mod, a_merkez = polinom_girdisi()
    referans = carp_okul_yontemi(a, s_mod)
    satirlar = []
    print(f"Aşama 7 benchmark başlıyor: {TEKRAR} tekrar, saat={clock:.2f} MHz", flush=True)

    for name, fn, ops in polinom_yontemleri(a, s, s_mod, a_merkez):
        assert fn() == referans, f"Doğruluk hatası: {name}"
        print(f"  polinom: {name}", flush=True)
        satirlar.append(satir_olustur("Saf R_q polinom çarpımı", "N=256", name, fn, ops, clock))

    for p in (ML_KEM_512, ML_KEM_768, ML_KEM_1024):
        print(f"  ML-KEM: {p.ad}", flush=True)
        standard = e2e_fonk(p, kpke)
        cached_pke = CachedKroneckerPKE(VARYANT["isaretli24-bayt-negmod"])
        cached = e2e_fonk(p, cached_pke)
        # Warm the A cache before timing; warming is a separately documented cost.
        cached()
        satirlar.append(
            satir_olustur("Uçtan uca ML-KEM", p.ad, "NTT (FIPS 203)", standard, p.k * p.k * N * N, clock)
        )
        satirlar.append(
            satir_olustur(
                "Uçtan uca ML-KEM",
                p.ad,
                "Kronecker (önbellekli katsayı A)",
                cached,
                p.k * p.k * N * N,
                clock,
            )
        )

    csv_yaz(KLASOR / "veri_iot_benchmark.csv", satirlar)
    ozet = ozet_uret(satirlar)
    csv_yaz(KLASOR / "ozet.csv", ozet)
    sonuc_yaz(satirlar, ozet, clock)
    print("Üretildi: veri_iot_benchmark.csv, ozet.csv, sonuc.md", flush=True)


if __name__ == "__main__":
    main()

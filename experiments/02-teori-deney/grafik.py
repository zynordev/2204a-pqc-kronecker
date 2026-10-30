"""H2 analizi: veri.csv.gz + en_kotu.csv → ozet.csv, grafik_e23.png, grafik_e24.png, grafik_fark.png.

Kullanım (repo kökünden, deneyden sonra): python experiments/02-teori-deney/grafik.py
matplotlib gerektirir (yalnızca bu betik; kütüphane kodu bağımlılıksızdır).
"""

import csv
import gzip
import math
import pathlib
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pqc.parametreler import N
from pqc.teori import A, l_min_isaretli, model_hata, model_hata_taban

KLASOR = pathlib.Path(__file__).parent
DURUMLAR = {
    "tek-eta3": (1, 3),
    "tek-eta2": (1, 2),
    "modul-512": (2, 3),
    "modul-768": (3, 2),
    "modul-1024": (4, 2),
}
OLCULEBILIR = (1e-3, 1 - 1e-3)  # ön kayıt: model bu aralıktayken karşılaştırılır


def wilson(x: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = x / n
    merkez = (p + z * z / (2 * n)) / (1 + z * z / n)
    yari = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, merkez - yari), min(1.0, merkez + yari)


def seri_parametre(seri: str) -> tuple[int, int, bool]:
    ad, tur = seri.rsplit("-", 1)
    k, eta = DURUMLAR[ad]
    return k, eta, tur == "neg"


def oku():
    hler = defaultdict(list)
    dogru = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # seri → l → [hatalı, toplam]
    with gzip.open(KLASOR / "veri.csv.gz", "rt", newline="") as f:
        r = csv.reader(f)
        next(r)
        baslik = next(r)
        lar = [int(b.removeprefix("dogru_l")) for b in baslik[3:]]
        for satir in r:
            seri, h = satir[0], int(satir[2])
            hler[seri].append(h)
            for l, d in zip(lar, satir[3:]):
                if d != "":
                    dogru[seri][l][0] += d == "0"
                    dogru[seri][l][1] += 1
    return hler, dogru


def main() -> None:
    hler, dogru = oku()
    seriler = list(hler)

    # --- E2.3 tablosu ---
    ozet = []
    for seri in seriler:
        k, eta, neg = seri_parametre(seri)
        for l, (x, n) in sorted(dogru[seri].items()):
            bag, birlesim = model_hata(l, N, eta, k, neg)
            alt, ust = wilson(x, n)
            olculebilir = OLCULEBILIR[0] < bag < OLCULEBILIR[1]
            ozet.append(
                [seri, l, x, n, x / n, alt, ust, bag, birlesim, int(olculebilir), int(alt <= bag <= ust)]
            )
    with open(KLASOR / "ozet.csv", "w", newline="") as f:
        yaz = csv.writer(f)
        yaz.writerow(
            [
                "seri",
                "l",
                "hatali",
                "toplam",
                "oran",
                "wilson_alt",
                "wilson_ust",
                "model_bagimsiz",
                "model_birlesim",
                "olculebilir",
                "model_aralikta",
            ]
        )
        yaz.writerows(ozet)
    print("E2.3 (tam sayı ℓ; yalnızca 0 < hatalı < toplam veya ölçülebilir satırlar):")
    print(
        f"{'seri':16s} {'ℓ':>3s} {'hatalı/toplam':>14s} {'oran':>9s} {'%95 GA':>21s} {'model':>9s} {'birleşim':>9s}"
    )
    for s in ozet:
        if 0 < s[2] < s[3] or s[9]:
            print(
                f"{s[0]:16s} {s[1]:3d} {s[2]:>6d}/{s[3]:<7d} {s[4]:9.2e} [{s[5]:.2e}, {s[6]:.2e}] "
                f"{s[7]:9.2e} {s[8]:9.2e} {'✓' if s[10] else '✗'}"
            )

    # --- E2.4: sürekli taban ---
    print("\nE2.4 (sürekli log₂B ızgarası, adım 0,02; model ölçülebilir aralıktayken):")
    izgara = [15.0 + 0.02 * i for i in range(int((19.5 - 15.0) / 0.02) + 1)]
    e24 = {}
    for seri in seriler:
        k, eta, neg = seri_parametre(seri)
        h = sorted(hler[seri])
        n = len(h)
        noktalar = []
        icinde = sayilan = 0
        for x in izgara:
            yari = 2 ** (x - 1)
            hatali = sum(1 for v in h if v > yari)
            bag, birlesim = model_hata_taban(yari, N, eta, k, neg)
            alt, ust = wilson(hatali, n)
            noktalar.append((x, hatali / n, alt, ust, bag, birlesim))
            if OLCULEBILIR[0] < bag < OLCULEBILIR[1]:
                sayilan += 1
                icinde += alt <= bag <= ust
        e24[seri] = noktalar
        log_h = sorted(math.log2(2 * v) for v in h)
        print(
            f"{seri:16s} model GA içinde {icinde:3d}/{sayilan:<3d}  log₂(2h*) medyan {log_h[n // 2]:.2f}, "
            f"en büyük {log_h[-1]:.2f}, ℓ_min {l_min_isaretli(N, A, eta, k)}"
        )

    # --- grafikler ---
    renk = {"tek-eta3": "C0", "tek-eta2": "C1", "modul-512": "C2", "modul-768": "C4", "modul-1024": "C3"}
    for dosya, baslik, tur in (
        ("grafik_e24.png", "tam çarpım (2n−1 dilim)", "tam"),
        ("grafik_e24_neg.png", "negasiklik mod 2^(nℓ)+1 (n dilim)", "neg"),
    ):
        fig, ax = plt.subplots(figsize=(8, 5))
        for seri, noktalar in e24.items():
            if not seri.endswith(tur):
                continue
            ad = seri.rsplit("-", 1)[0]
            xs = [p[0] for p in noktalar]
            ax.plot(xs, [max(p[4], 1e-7) for p in noktalar], "-", color=renk[ad], lw=1.5, label=f"{ad} model")
            olc = [(p[0], p[1], p[2], p[3]) for p in noktalar[::5] if p[1] > 0]
            ax.errorbar(
                [o[0] for o in olc],
                [o[1] for o in olc],
                yerr=[[o[1] - o[2] for o in olc], [o[3] - o[1] for o in olc]],
                fmt="o",
                ms=3,
                color=renk[ad],
                label=f"{ad} ölçülen (%95 GA)",
            )
        ax.set_yscale("log")
        ax.set_ylim(1e-5, 1.5)
        ax.set_xlabel("log₂ B  (B = açma tabanı; B = 2^ℓ'de tam sayı)")
        ax.set_ylabel("açmanın bozulma olasılığı")
        ax.set_title(f"E2.4 — Model 2 ve ölçüm, {baslik}, N = {len(next(iter(hler.values())))} / seri")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=7, ncol=2)
        fig.tight_layout()
        fig.savefig(KLASOR / dosya, dpi=150)
        plt.close(fig)

    # en kötü durum ile tipik durum arasındaki fark
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, ad in enumerate(DURUMLAR):
        seri = f"{ad}-tam"
        k, eta, _ = seri_parametre(seri)
        log_h = [math.log2(2 * v) for v in hler[seri]]
        ax.hist(
            log_h, bins=60, histtype="step", color=renk[ad], label=f"{ad}: rastgele girdide gereken log₂B"
        )
        ax.axvline(l_min_isaretli(N, A, eta, k) - 0.03 * i, color=renk[ad], ls="--", lw=1)
    ax.set_xlabel("log₂ B (gereken açma tabanı); kesikli çizgi: ℓ_min (Teorem 1 / Sonuç 1, en kötü durum)")
    ax.set_ylabel("deneme sayısı")
    ax.set_title("En kötü durum (ispat) ile tipik durum (rastgele girdi) arasındaki fark")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(KLASOR / "grafik_fark.png", dpi=150)
    plt.close(fig)
    print("\ngrafikler yazıldı: grafik_e24.png, grafik_e24_neg.png, grafik_fark.png; tablo: ozet.csv")


if __name__ == "__main__":
    main()

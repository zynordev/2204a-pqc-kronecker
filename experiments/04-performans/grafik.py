"""H3 analizi ve grafikleri: E3.1, E3.2, E3.3, E3.4 -> grafikler ve sonuc.md.

Kullanım: python experiments/04-performans/grafik.py
"""

import csv
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

KLASOR = pathlib.Path(__file__).parent


def ciz_e31():
    veriler = []
    with open(KLASOR / "veri_e31.csv") as f:
        r = csv.reader(f)
        next(r)
        next(r)
        for row in r:
            veriler.append((row[0], int(row[1]), float(row[2]), float(row[3])))

    labels = [v[0] for v in veriler]
    meds = [v[2] for v in veriler]
    iqrs = [v[3] for v in veriler]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(labels, meds, yerr=iqrs, capsize=4, color=["tab:gray", "tab:blue", "tab:green", "tab:cyan"])
    ax.set_ylabel("Çarpım Süresi (µs)")
    ax.set_title("E3.1 — Saf Bigint Çarpım Süreleri (Karatsuba Hızlanması)")
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    # Değerleri ve hızlanmayı çubukların üstüne yaz
    base = meds[0]
    for bar, med in zip(bars, meds):
        hiz = base / med
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            f"{med:.2f} µs\n({hiz:.2f}x)",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(KLASOR / "grafik_e31.png", dpi=150)
    plt.close(fig)
    print("grafik_e31.png üretildi.")


def ciz_e32():
    veriler = []
    with open(KLASOR / "veri_e32.csv") as f:
        r = csv.reader(f)
        next(r)
        next(r)
        for row in r:
            veriler.append((row[0], float(row[1]), float(row[2])))

    # Schoolbook süre ölçeğini çok şişirebileceği için log scale veya kırparak gösterelim
    labels = [v[0] for v in veriler]
    meds = [v[1] for v in veriler]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(labels, meds, color="tab:blue")
    ax.set_xlabel("Süre (µs) [Logaritmik Ölçek]")
    ax.set_xscale("log")
    ax.set_title("E3.2 — Tek Polinom Çarpımı ($R_q$) Yöntem Kıyaslaması")
    ax.grid(axis="x", linestyle=":", alpha=0.6)

    for bar, med in zip(bars, meds):
        ax.text(
            bar.get_width() * 1.05,
            bar.get_y() + bar.get_height() / 2,
            f"{med:.1f} µs",
            va="center",
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(KLASOR / "grafik_e32.png", dpi=150)
    plt.close(fig)
    print("grafik_e32.png üretildi.")


def ciz_e33():
    veriler = []
    with open(KLASOR / "veri_e33.csv") as f:
        r = csv.reader(f)
        next(r)
        next(r)
        for row in r:
            veriler.append((row[0], float(row[1]), float(row[2]), float(row[3]), float(row[4])))

    labels = [v[0] for v in veriler]
    t_pack = [v[1] for v in veriler]
    t_mul = [v[2] for v in veriler]
    t_unpack = [v[3] for v in veriler]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(labels, t_pack, label="Paketleme (Pack)", color="tab:blue")
    ax.bar(labels, t_mul, bottom=t_pack, label="Tamsayı Çarpımı (Mul)", color="tab:green")
    bottom_unpack = [p + m for p, m in zip(t_pack, t_mul)]
    ax.bar(
        labels, t_unpack, bottom=bottom_unpack, label="Açma / İndirgeme (Unpack/Reduce)", color="tab:orange"
    )

    ax.set_ylabel("Süre (µs)")
    ax.set_title("E3.3 — Kronecker Varyantlarında Süre Dağılımı (Breakdown)")
    ax.legend()
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    fig.tight_layout()
    fig.savefig(KLASOR / "grafik_e33.png", dpi=150)
    plt.close(fig)
    print("grafik_e33.png üretildi.")


def ciz_e34():
    veriler = []
    with open(KLASOR / "veri_e34.csv") as f:
        r = csv.reader(f)
        next(r)
        next(r)
        for row in r:
            # parametre, motor, keygen, _, encaps, _, decaps, _
            veriler.append((row[0], row[1], float(row[2]), float(row[4]), float(row[6])))

    # 3 parametre seti için gruplu çubuk grafik
    parametreler = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
    motorlar = list(dict.fromkeys(v[1] for v in veriler))

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), sharey=True)
    islem_adlari = ["KeyGen", "Encaps", "Decaps"]

    for idx, islem in enumerate(islem_adlari):
        ax = axes[idx]
        x_offsets = [-0.25, 0, 0.25]
        for m_idx, motor in enumerate(motorlar):
            vals = [next(v[2 + idx] for v in veriler if v[0] == p and v[1] == motor) for p in parametreler]
            x_pos = [i + x_offsets[m_idx] for i in range(len(parametreler))]
            ax.bar(x_pos, vals, width=0.22, label=motor if idx == 0 else "")

        ax.set_title(islem)
        ax.set_xticks(range(len(parametreler)))
        ax.set_xticklabels(parametreler, fontsize=8)
        ax.set_ylabel("Süre (µs)" if idx == 0 else "")
        ax.grid(axis="y", linestyle=":", alpha=0.6)

    fig.suptitle("E3.4 — Tam ML-KEM Uçtan Uca Süre Karşılaştırması (NTT vs. Kronecker)")
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(KLASOR / "grafik_e34.png", dpi=150)
    plt.close(fig)
    print("grafik_e34.png üretildi.")


def main():
    ciz_e31()
    ciz_e32()
    ciz_e33()
    ciz_e34()


if __name__ == "__main__":
    main()

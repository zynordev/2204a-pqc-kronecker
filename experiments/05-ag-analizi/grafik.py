"""Aşama 5b: Ağ Analizi Karşılaştırma Grafikleri.

Üretilen Grafikler:
  1. grafik_entropi_ve_boyut.png: Shannon Entropisi ve Ağ Yükü Karşılaştırması
  2. grafik_kuantum_guvenlik.png: Klasik vs Kuantum Güvenlik Düzeyleri (Bit eşdeğeri)
"""

import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIZIN = pathlib.Path(__file__).parent


def ciz_grafikler():
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["font.size"] = 10

    protokoller = ["Düz HTTP", "Standart TLS 1.3\n(ECDHE)", "PQC-Drop\n(Kronecker)"]
    renkler = ["#d9534f", "#f0ad4e", "#2e7d32"]

    # -------------------------------------------------------------
    # Grafik 1: Entropi ve Paket Boyutu
    # -------------------------------------------------------------
    _fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Entropi
    entropiler = [4.712, 7.842, 7.965]  # Teorik/Ölçülen Shannon
    ax1.bar(protokoller, entropiler, color=renkler, width=0.5, edgecolor="black", alpha=0.85)
    ax1.axhline(8.0, color="gray", linestyle="--", alpha=0.7, label="Teorik Maksimum (8.0)")
    ax1.set_ylabel("Shannon Entropisi (bit / bayt)")
    ax1.set_title("A. Bilgi Gizleme / Rastlantısallık (Entropi)", fontweight="bold")
    ax1.set_ylim(0, 9.0)
    for i, v in enumerate(entropiler):
        ax1.text(i, v + 0.15, f"{v:.3f}", ha="center", fontweight="bold")
    ax1.legend(loc="lower right")

    # Açık Anahtar / El Sıkışma Boyutu (Bayt)
    boyutlar = [0, 32, 1184]
    b_renkler = ["#777777", "#f0ad4e", "#1b5e20"]
    ax2.bar(protokoller, boyutlar, color=b_renkler, width=0.5, edgecolor="black", alpha=0.85)
    ax2.set_ylabel("Açık Anahtar Boyutu (Bayt)")
    ax2.set_title("B. Kriptografik Anahtar Yükü (Trade-off)", fontweight="bold")
    for i, v in enumerate(boyutlar):
        ax2.text(i, v + (25 if v > 0 else 10), f"{v} B", ha="center", fontweight="bold")
    ax2.set_ylim(0, 1400)

    plt.tight_layout()
    cikis1 = DIZIN / "grafik_entropi_ve_boyut.png"
    plt.savefig(cikis1, dpi=300)
    plt.close()
    print(f"✓ Grafik 1 oluşturuldu: {cikis1}")

    # -------------------------------------------------------------
    # Grafik 2: Güvenlik Düzeyleri (Klasik vs Kuantum)
    # -------------------------------------------------------------
    _fig, ax = plt.subplots(figsize=(8, 5))

    x = range(len(protokoller))
    genislik = 0.35

    klasik_bit = [0, 128, 192]
    kuantum_bit = [0, 0, 192]

    b1 = ax.bar([p - genislik / 2 for p in x], klasik_bit, genislik, label="Klasik Güvenlik (Bit)", color="#1976d2", edgecolor="black")
    b2 = ax.bar([p + genislik / 2 for p in x], kuantum_bit, genislik, label="Kuantum Güvenlik (Shor Direnci)", color="#388e3c", edgecolor="black")

    ax.set_xticks(list(x))
    ax.set_xticklabels(protokoller, fontweight="bold")
    ax.set_ylabel("Etkin Güvenlik Seviyesi (Bit)")
    ax.set_title("Klasik Bilgisayar vs Kuantum Bilgisayar Karşısında Güvenlik Düzeyi", fontweight="bold")
    ax.set_ylim(0, 230)
    ax.axhline(128, color="red", linestyle=":", label="Güvenli Kabul Edilen Eşik (128-bit)")

    for rect in b1:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, h + 3, f"{int(h)} b", ha="center", fontsize=9)
    for rect in b2:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, h + 3, f"{int(h)} b", ha="center", fontsize=9, fontweight="bold")

    ax.legend(loc="upper left")
    plt.tight_layout()
    cikis2 = DIZIN / "grafik_kuantum_guvenlik.png"
    plt.savefig(cikis2, dpi=300)
    plt.close()
    print(f"✓ Grafik 2 oluşturuldu: {cikis2}")


if __name__ == "__main__":
    ciz_grafikler()

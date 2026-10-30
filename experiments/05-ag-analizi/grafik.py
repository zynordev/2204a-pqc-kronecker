"""Aşama 5b: Ağ Analizi Karşılaştırma Grafikleri.

Üretilen Grafikler:
  1. grafik_entropi_ve_boyut.png: Shannon Entropisi ve Ağ Yükü Karşılaştırması
  2. grafik_kuantum_guvenlik.png: Klasik vs Kuantum Güvenlik Düzeyleri (Bit eşdeğeri)
"""

import csv
import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIZIN = pathlib.Path(__file__).parent


def veri_oku() -> list[dict]:
    """calistir.py'nin yazdığı veri.csv; grafikler yalnızca buradan beslenir (05-hata-kontrol kuralı)."""
    with open(DIZIN / "veri.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ciz_grafikler():
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["font.size"] = 10

    satirlar = veri_oku()
    protokoller = ["Düz HTTP", "Yalnızca klasik ECDHE\n(TLS 1.3 benzeri)", "PQC-Drop\n(Kronecker)"]
    renkler = ["#d9534f", "#f0ad4e", "#2e7d32"]

    # -------------------------------------------------------------
    # Grafik 1: Entropi ve Paket Boyutu
    # -------------------------------------------------------------
    _fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Entropi (ölçülen) + aynı uzunlukta saf rastgele baytın ulaşabileceği üst sınır.
    # n baytlık bir örneklemin entropisi en çok log2(n) olabilir; kısa paketler bu yüzden 8'e ulaşamaz.
    # Şifreli iki yük arasındaki fark büyük ölçüde paket uzunluğundan gelir, şifreleme kalitesinden değil.
    entropiler = [float(r["Entropi"]) for r in satirlar]
    boyut_bayt = [int(r["Paket_Bayt"]) for r in satirlar]
    ust_sinir = [min(8.0, math.log2(n)) for n in boyut_bayt]
    ax1.bar(protokoller, entropiler, color=renkler, width=0.5, edgecolor="black", alpha=0.85, label="Ölçülen")
    ax1.scatter(
        range(len(protokoller)), ust_sinir, marker="_", s=600, color="black", zorder=3,
        label="Üst sınır log₂(paket boyutu)",
    )
    ax1.axhline(8.0, color="gray", linestyle="--", alpha=0.7, label="Teorik Maksimum (8.0)")
    ax1.set_ylabel("Shannon Entropisi (bit / bayt)")
    ax1.set_title("A. Entropi (örneklem boyutuna bağlıdır)", fontweight="bold")
    ax1.set_ylim(0, 9.0)
    for i, (v, n) in enumerate(zip(entropiler, boyut_bayt)):
        ax1.text(i, v + 0.15, f"{v:.3f}\n(n = {n} B)", ha="center", fontweight="bold")
    ax1.legend(loc="lower right", fontsize=8)

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

    # Klasik: X25519 ≈ 128 bit; ML-KEM-768 NIST Kategori 3 (AES-192 anahtar aramasına eşdeğer hedef).
    # Kuantum: X25519 Shor ile polinom zamanda kırılır (0); ML-KEM için bilinen kuantum saldırısı yok — NIST kategori
    # tanımı klasik ve kuantum saldırıları birlikte kapsadığı için aynı hedef çizilir. Bu "192 bit ölçüldü" demek değildir.
    klasik_bit = [0, 128, 192]
    kuantum_bit = [0, 0, 192]

    b1 = ax.bar([p - genislik / 2 for p in x], klasik_bit, genislik, label="Klasik güvenlik hedefi (bit)", color="#1976d2", edgecolor="black")
    b2 = ax.bar([p + genislik / 2 for p in x], kuantum_bit, genislik, label="Kuantum saldırgana karşı hedef (bit; 0 = Shor ile kırılır)", color="#388e3c", edgecolor="black")

    ax.set_xticks(list(x))
    ax.set_xticklabels(protokoller, fontweight="bold")
    ax.set_ylabel("Güvenlik hedefi (bit eşdeğeri, NIST tanımı)")
    ax.set_title("Klasik ve kuantum saldırgana karşı güvenlik hedefi (ölçüm değil, tasarım hedefi)", fontweight="bold")
    ax.set_ylim(0, 230)
    ax.axhline(128, color="red", linestyle=":", label="Yaygın kabul gören alt sınır (128 bit)")

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

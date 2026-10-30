"""H4 analizi: veri_e41.csv + veri_e42.csv -> grafik_e41.png, grafik_e42.png, sonuc.md

Kullanım: python experiments/03-guvenlik/grafik.py
"""

import csv
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

KLASOR = pathlib.Path(__file__).parent


def esik(l: int) -> float:
    return (1 << (l - 1)) / 1664.0


def main():
    # --- E4.1 Grafiği ---
    veriler_41 = []
    with open(KLASOR / "veri_e41.csv") as f:
        r = csv.reader(f)
        next(r)  # metadata
        next(r)  # header
        for row in r:
            norm_s = int(row[1])
            h18, _b18 = int(row[2]), int(row[3])
            h19, _b19 = int(row[4]), int(row[5])
            h20, _b20 = int(row[6]), int(row[7])
            h21, _b21 = int(row[8]), int(row[9])
            h22, _b22 = int(row[10]), int(row[11])
            veriler_41.append((norm_s, h18, h19, h20, h21, h22))

    veriler_41.sort(key=lambda x: x[0])
    norms = [v[0] for v in veriler_41]

    fig, ax = plt.subplots(figsize=(9, 5))
    renkler = {18: "tab:purple", 19: "tab:red", 20: "tab:orange", 21: "tab:blue", 22: "tab:green"}

    for idx, l in enumerate([18, 19, 20, 21, 22]):
        hatalar = [v[1 + idx] for v in veriler_41]
        ax.scatter(norms, [h + idx * 0.02 for h in hatalar], s=12, alpha=0.6,
                   color=renkler[l], label=f"ℓ = {l} (ölçülen hata)")
        e = esik(l)
        if e <= max(norms):
            ax.axvline(e, color=renkler[l], linestyle="--", alpha=0.8,
                       label=f"ℓ = {l} teorik eşik ({e:.1f})")

    ax.set_xlabel("Gizli Anahtar 1-Normu: ||s||₁")
    ax.set_ylabel("Çarpım Hatası Oluşumu (0 = Doğru, 1 = Taştı)")
    ax.set_title("E4.1 — Dar ℓ Seçiminde Gizli Anahtara Bağlı Hata Sızıntısı (H4 Doğrulaması)")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["0 (Doğru)", "1 (Bozuk / Taştı)"])
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1, 0.5))
    fig.tight_layout()
    fig.savefig(KLASOR / "grafik_e41.png", dpi=150)
    plt.close(fig)
    print("grafik_e41.png üretildi.")

    # --- E4.2 Grafiği ---
    veriler_42 = []
    with open(KLASOR / "veri_e42.csv") as f:
        r = csv.reader(f)
        next(r)
        next(r)
        for row in r:
            norm_s0 = int(row[1])
            bozuldu = int(row[2])
            veriler_42.append((norm_s0, bozuldu))

    veriler_42.sort(key=lambda x: x[0])
    norms_42 = [v[0] for v in veriler_42]
    bozulma_42 = [v[1] for v in veriler_42]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(norms_42, bozulma_42, color="tab:red", s=25, alpha=0.7, label="Ölçülen Decaps Hatası")
    e20 = esik(20)
    ax.axvline(e20, color="black", linestyle="--", lw=1.5, label=f"Teorik Eşik (ℓ=20, ||s₀||₁ ≥ {e20:.1f})")

    ax.set_xlabel("Kurbanın Gizli Anahtar Normu: ||s₀||₁")
    ax.set_ylabel("Decapsulation Sonucu")
    ax.set_title("E4.2 — ML-KEM-512 Üzerinde Seçilmiş Şifreli Metin ile Norm Sızıntısı")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Kabul (m doğru)", "Hata / İhlal (m bozuldu)"])
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend()
    fig.tight_layout()
    fig.savefig(KLASOR / "grafik_e42.png", dpi=150)
    plt.close(fig)
    print("grafik_e42.png üretildi.")


if __name__ == "__main__":
    main()

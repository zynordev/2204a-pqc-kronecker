"""Aşama 7 CSV sonuçlarından jüri sunumuna uygun süre/bellek grafikleri."""

from __future__ import annotations

import csv
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

KLASOR = pathlib.Path(__file__).parent


def oku():
    with (KLASOR / "veri_iot_benchmark.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ciz(metric, ylabel, output, title):
    rows = oku()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    groups = [
        ("Saf R_q polinom çarpımı", "N=256", "Saf polinom çarpımı"),
        ("Uçtan uca ML-KEM", "", "Uçtan uca ML-KEM"),
    ]
    colors = {"NTT": "#2563eb", "Kronecker": "#059669", "Schoolbook": "#9ca3af"}
    for ax, (category, param, subtitle) in zip(axes, groups):
        selected = [r for r in rows if r["kategori"] == category and (not param or r["parametre"] == param)]
        labels = [r["yontem"].replace("Kronecker ", "K: ").replace(" (FIPS 203)", "") for r in selected]
        values = [float(r[metric]) for r in selected]
        palette = [
            next((color for key, color in colors.items() if key in r["yontem"]), "#f59e0b") for r in selected
        ]
        bars = ax.barh(labels, values, color=palette)
        ax.set_title(subtitle)
        ax.grid(axis="x", linestyle=":", alpha=0.6)
        ax.set_xscale("log")
        for bar, value in zip(bars, values):
            ax.text(value * 1.05, bar.get_y() + bar.get_height() / 2, f"{value:.0f}", va="center", fontsize=8)
    fig.suptitle(title)
    fig.supxlabel(ylabel)
    fig.savefig(KLASOR / output, dpi=180)
    plt.close(fig)
    print(f"{output} üretildi.")


def main():
    ciz("medyan_ns", "Medyan süre (ns, log ölçek)", "grafik_sure.png", "Aşama 7 — Süre karşılaştırması")
    ciz(
        "peak_memory_bytes",
        "tracemalloc tepe tahsisi (bayt, log ölçek)",
        "grafik_bellek.png",
        "Aşama 7 — Python tepe bellek karşılaştırması",
    )


if __name__ == "__main__":
    main()

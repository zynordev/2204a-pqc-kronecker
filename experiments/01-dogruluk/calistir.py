"""E1.2 — 10.000 rastgele iç çarpım: her Kronecker varyantı okul yöntemine (altın standart) karşı.

Her örnekte ML-KEM'de gerçekten oluşan (k, η) çiftlerinden biri seçilir: (1,3), (2,3), (3,2), (4,2).
Büyük polinomlar [0, q)'da düzgün, küçükler CBD(η) ile çekilir (ML-KEM'deki dağılım).
Çıktı: veri.csv (her örnek bir satır, her varyant için 1 = doğru, 0 = hatalı).
Kullanım (repo kökünden): python experiments/01-dogruluk/calistir.py [ornek_sayisi]
"""

import csv
import pathlib
import platform
import random
import sys
import time

from pqc.kronecker import VARYANTLAR
from pqc.parametreler import N, Q
from pqc.polinom import carp_okul_yontemi, topla

TOHUM = 20261027
KOMBINASYONLAR = [(1, 3), (2, 3), (3, 2), (4, 2)]
KLASOR = pathlib.Path(__file__).parent


def cbd(rng, eta):
    """CBD(η): η yazı-tura farkı (FIPS 203 Alg. 8 ile aynı dağılım, bayt yerine doğrudan)."""
    return [sum(rng.getrandbits(1) for _ in range(eta)) - sum(rng.getrandbits(1) for _ in range(eta)) for _ in range(N)]


def main():
    adet = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000
    rng = random.Random(TOHUM)
    hata = {v.ad: 0 for v in VARYANTLAR}
    basla = time.time()
    with open(KLASOR / "veri.csv", "w", newline="") as f:
        yaz = csv.writer(f)
        yaz.writerow([f"# tohum={TOHUM} adet={adet} python={platform.python_version()} makine={platform.machine()}"])
        yaz.writerow(["ornek", "k", "eta"] + [v.ad for v in VARYANTLAR])
        for i in range(adet):
            k, eta = KOMBINASYONLAR[i % len(KOMBINASYONLAR)]
            buyuk = [[rng.randrange(Q) for _ in range(N)] for _ in range(k)]
            kucuk = [[x % Q for x in cbd(rng, eta)] for _ in range(k)]
            ref = [0] * N
            for b, s in zip(buyuk, kucuk):
                ref = topla(ref, carp_okul_yontemi(b, s))
            satir = [i, k, eta]
            for v in VARYANTLAR:
                dogru = int(v.ic_carpim(buyuk, kucuk, eta) == ref)
                hata[v.ad] += 1 - dogru
                satir.append(dogru)
            yaz.writerow(satir)
            if (i + 1) % 1000 == 0:
                print(f"{i + 1}/{adet}  {time.time() - basla:.0f} sn", flush=True)
    print("\nvaryant                          hatalı / toplam")
    for ad, h in hata.items():
        print(f"{ad:32s} {h} / {adet}")
    return 1 if any(hata.values()) else 0


if __name__ == "__main__":
    sys.exit(main())

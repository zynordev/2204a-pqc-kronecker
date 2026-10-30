"""H2 — Teori deneyle örtüşür mü? (E2.1–E2.4, docs/03-hipotez-ve-deneyler.md)

Seriler: ML-KEM'de gerçekten oluşan (k, η) çiftleri × açma türü.
  tek-eta3 / tek-eta2 : her çarpım ayrı açılır (k = 1)            → Teorem 1
  modul-512/768/1024  : iç çarpım açılmadan toplanır (k = 2, 3, 4) → Sonuç 1
  tam / neg           : 2n−1 dilim (X^n = −1 sonradan) / mod 2^(nℓ)+1 ile n dilim → Önerme 2

E2.1/E2.2: en kötü durum girdisi, ℓ = ℓ_min (doğru olmalı) ve ℓ_min − 1 (bozuk olmalı).
E2.3: rastgele girdi (büyük: [0, q) düzgün, küçük: CBD(η)), ℓ = 14 … ℓ_min, gerçek dar-ℓ Kronecker.
E2.4: her denemede tam dilim değerleri ℓ = 40 ile kesin hesaplanır (Teorem 1: 4·256·1664·3 < 2^39) ve
      h* = gereken en küçük yarım taban kaydedilir: açma B tabanında doğru ⇔ tüm dilimler [−B/2, B/2) içinde
      ⇔ h* ≤ B/2 (Lemma 1; B'nin 2'nin kuvveti olması gerekmez). Böylece hata oranı sürekli log₂B ekseninde
      ölçülüp Model 2 ile karşılaştırılır.

Çıktı: veri.csv.gz (her deneme bir satır; gzip'li CSV), en_kotu.csv (E2.1/E2.2).
Kullanım (repo kökünden): python experiments/02-teori-deney/calistir.py [deneme_sayisi] [surec_sayisi]
"""

import csv
import gzip
import multiprocessing
import pathlib
import platform
import random
import sys
import time

from pqc.kronecker import Varyant, ac_dongu_isaretli, paketle_dongu
from pqc.parametreler import N, Q
from pqc.polinom import carp_okul_yontemi, topla
from pqc.teori import A, l_min_isaretli

TOHUM = 20261030
L_EN_KUCUK = 14
L_KESIN = 40
KLASOR = pathlib.Path(__file__).parent

# (ad, k, η)
DURUMLAR = [("tek-eta3", 1, 3), ("tek-eta2", 1, 2), ("modul-512", 2, 3), ("modul-768", 3, 2), ("modul-1024", 4, 2)]
SERILER = [(ad, k, eta, neg) for ad, k, eta in DURUMLAR for neg in (False, True)]


def seri_adi(ad: str, neg: bool) -> str:
    return f"{ad}-{'neg' if neg else 'tam'}"


def l_min(k: int, eta: int) -> int:
    return l_min_isaretli(N, A, eta, k)


def varyant(l: int, k: int, neg: bool) -> Varyant:
    return Varyant(f"l{l}", l=l, isaretli=True, negasiklik_mod=neg, modul_toplami=k > 1)


def cbd(rng: random.Random, eta: int) -> list[int]:
    """CBD(η): η yazı-tura farkı (FIPS 203 Alg. 8 ile aynı dağılım)."""
    return [sum(rng.getrandbits(1) for _ in range(eta)) - sum(rng.getrandbits(1) for _ in range(eta))
            for _ in range(N)]


def merkezle(x: int) -> int:
    return x - Q if x > Q // 2 else x


def kesin_dilimler(buyuk: list[list[int]], kucuk: list[list[int]], neg: bool) -> list[int]:
    """Açılacak dilimlerin kesin değerleri: Σ_j büyük_j·küçük_j'nin tam çarpım katsayıları c_k
    (2n−1 tane) veya negasiklik d_k = c_k − c_{k+n} (n tane). Merkezlenmiş girdilerle, ℓ = 40'ta."""
    C = sum(paketle_dongu([merkezle(x) for x in b], L_KESIN) * paketle_dongu([merkezle(x) for x in s], L_KESIN)
            for b, s in zip(buyuk, kucuk))
    c = ac_dongu_isaretli(C, L_KESIN, 2 * N - 1) + [0]
    if neg:
        return [c[i] - c[i + N] for i in range(N)]
    return c[:-1]


def gereken_yari_taban(dilimler: list[int]) -> int:
    """h*: tüm dilimlerin [−h, h) içinde olduğu en küçük h."""
    return max(max(dilimler) + 1, -min(dilimler))


def referans(dilimler: list[int], neg: bool) -> list[int]:
    if neg:
        return [x % Q for x in dilimler]
    c = dilimler + [0]
    return [(c[i] - c[i + N]) % Q for i in range(N)]


# --- E2.1 / E2.2: en kötü durum ---

def en_kotu_girdiler(k: int, eta: int, neg: bool) -> list[tuple[str, list[list[int]], list[list[int]]]]:
    """Önerme 1 (a) ve Önerme 2'nin keskinlik girdileri, k terime genişletilmiş (Sonuç 1)."""
    girdiler = []
    for isaret in (1, -1):
        if neg:
            for k0 in (0, N - 1):
                a = [isaret * (A if i <= k0 else -A) for i in range(N)]
                girdiler.append((f"negasiklik k0={k0} isaret={isaret:+d}", [[x % Q for x in a]] * k,
                                 [[eta] * N] * k))
        else:
            girdiler.append((f"a=±A, s=η isaret={isaret:+d}", [[(isaret * A) % Q] * N] * k, [[eta] * N] * k))
    return girdiler


def en_kotu_deney() -> list[list]:
    satirlar = []
    for ad, k, eta, neg in SERILER:
        lm = l_min(k, eta)
        for aciklama, buyuk, kucuk in en_kotu_girdiler(k, eta, neg):
            ref = [0] * N
            for b, s in zip(buyuk, kucuk):
                ref = topla(ref, carp_okul_yontemi(b, s))
            h = gereken_yari_taban(kesin_dilimler(buyuk, kucuk, neg))
            for l in (lm, lm - 1):
                dogru = varyant(l, k, neg).ic_carpim(buyuk, kucuk, eta) == ref
                satirlar.append([seri_adi(ad, neg), aciklama, l, lm, h, int(dogru)])
    return satirlar


# --- E2.3 / E2.4: rastgele girdi ---

def seri_calistir(arg: tuple) -> tuple[str, list[list], int, int]:
    (ad, k, eta, neg), adet = arg
    ad = seri_adi(ad, neg)
    rng = random.Random(f"{TOHUM}-{ad}")
    lm = l_min(k, eta)
    lar = list(range(L_EN_KUCUK, lm + 1))
    varyantlar = {l: varyant(l, k, neg) for l in lar}
    satirlar = []
    uyumsuz = 0  # gerçek açma sonucu ile Lemma 1 ölçütünün (h* ≤ 2^(ℓ−1)) farklı olduğu durum sayısı
    okul_kontrol = 0
    for i in range(adet):
        buyuk = [[rng.randrange(Q) for _ in range(N)] for _ in range(k)]
        kucuk = [[x % Q for x in cbd(rng, eta)] for _ in range(k)]
        dilimler = kesin_dilimler(buyuk, kucuk, neg)
        ref = referans(dilimler, neg)
        if i < 20:  # ℓ = 40 referansının kendisi de okul yöntemine karşı kontrol edilir
            okul = [0] * N
            for b, s in zip(buyuk, kucuk):
                okul = topla(okul, carp_okul_yontemi(b, s))
            if okul != ref:
                raise AssertionError(f"{ad}: ℓ = 40 referansı okul yönteminden farklı (deneme {i})")
            okul_kontrol += 1
        h = gereken_yari_taban(dilimler)
        sonuc = []
        for l in lar:
            dogru = varyantlar[l].ic_carpim(buyuk, kucuk, eta) == ref
            uyumsuz += dogru != (h <= 1 << (l - 1))
            sonuc.append(int(dogru))
        satirlar.append([ad, i, h] + sonuc)
    return ad, satirlar, uyumsuz, okul_kontrol


def main() -> int:
    adet = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000
    surec = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    basla = time.time()
    baslik = f"# tohum={TOHUM} adet={adet} python={platform.python_version()} makine={platform.machine()}"

    en_kotu = en_kotu_deney()
    with open(KLASOR / "en_kotu.csv", "w", newline="") as f:
        yaz = csv.writer(f)
        yaz.writerow([baslik])
        yaz.writerow(["seri", "girdi", "l", "l_min", "h_yildiz", "dogru"])
        yaz.writerows(en_kotu)
    beklenmeyen = [s for s in en_kotu if s[5] != int(s[2] == s[3])]
    print(f"E2.1/E2.2: {len(en_kotu)} çalıştırma, beklenmeyen {len(beklenmeyen)}", flush=True)

    l_max = max(l_min(k, eta) for _, k, eta in DURUMLAR)
    with multiprocessing.Pool(surec) as havuz, gzip.open(KLASOR / "veri.csv.gz", "wt", newline="") as f:
        yaz = csv.writer(f)
        yaz.writerow([baslik])
        yaz.writerow(["seri", "deneme", "h_yildiz"] + [f"dogru_l{l}" for l in range(L_EN_KUCUK, l_max + 1)])
        toplam_uyumsuz = 0
        for ad, satirlar, uyumsuz, okul in havuz.imap(seri_calistir, [(s, adet) for s in SERILER]):
            yaz.writerows(satirlar)
            toplam_uyumsuz += uyumsuz
            print(f"{ad:20s} bitti  uyumsuz={uyumsuz}  okul_kontrol={okul}  {time.time() - basla:.0f} sn",
                  flush=True)
    print(f"\nToplam süre {time.time() - basla:.0f} sn; Lemma 1 ölçütüyle uyumsuz {toplam_uyumsuz}")
    return 1 if beklenmeyen else 0


if __name__ == "__main__":
    sys.exit(main())

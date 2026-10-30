"""H3 — Performans Deneyleri (E3.1 - E3.4, docs/03-hipotez-ve-deneyler.md).

Protokol:
  - time.perf_counter_ns ile nanosaniye hassasiyeti.
  - Ölçüm sırasında çöp toplayıcı kapalı (gc.disable()).
  - Isınma turları (warmup).
  - Medyan ve IQR (Çeyrekler arası aralık).
  - Donanım ve Python sürümü başlığa kaydedilir.

Kullanım: python experiments/04-performans/calistir.py
"""

import csv
import gc
import pathlib
import platform
import random
import statistics
import time

from pqc import kpke, mlkem
from pqc.kpke_kronecker import KroneckerPKE
from pqc.kronecker import VARYANT, VARYANTLAR, merkezle
from pqc.ntt import carp_ntt, ntt, ntt_ters
from pqc.parametreler import ML_KEM_512, ML_KEM_768, ML_KEM_1024, N, Q
from pqc.polinom import carp_okul_yontemi

KLASOR = pathlib.Path(__file__).parent
TOHUM = 20261030


def olc_medyan_iqr(fonk, tekrar: int = 1000, isinma: int = 50) -> tuple[float, float]:
    """Süreyi mikrosaniye cinsinden (medyan, iqr) döner."""
    for _ in range(isinma):
        fonk()
    ts = []
    gc.disable()
    try:
        for _ in range(tekrar):
            t0 = time.perf_counter_ns()
            fonk()
            t1 = time.perf_counter_ns()
            ts.append((t1 - t0) / 1000.0)  # mikrosaniye
    finally:
        gc.enable()
    ts.sort()
    n = len(ts)
    med = statistics.median(ts)
    q1 = ts[n // 4]
    q3 = ts[(3 * n) // 4]
    return med, q3 - q1


# --- E3.1: Saf Bigint Çarpımı ---
def e31_deneyi(tekrar: int = 10000):
    rng = random.Random(TOHUM)
    bitler = [
        ("8192b (32-bit)", 8192),
        ("6144b (24-bit)", 6144),
        ("5632b (22-bit)", 5632),
        ("5376b (21-bit)", 5376),
    ]
    sonuclar = []
    for etiket, b in bitler:
        A = rng.getrandbits(b)
        B = rng.getrandbits(b)
        med, iqr = olc_medyan_iqr(lambda A=A, B=B: A * B, tekrar=tekrar, isinma=100)
        sonuclar.append([etiket, b, med, iqr])
    return sonuclar


# --- E3.2: Tek Polinom Çarpımı ($R_q$) ---
def e32_deneyi():
    rng = random.Random(TOHUM)
    a = [rng.randrange(Q) for _ in range(N)]
    s = [rng.randint(-3, 3) for _ in range(N)]
    s_mod = [x % Q for x in s]
    a_merkez = [merkezle(x) for x in a]

    sonuclar = []

    # 1. Schoolbook
    med_sb, iqr_sb = olc_medyan_iqr(lambda: carp_okul_yontemi(a, s_mod), tekrar=200, isinma=10)
    sonuclar.append(["Schoolbook", med_sb, iqr_sb])

    # 2. Saf Python NTT
    def ntt_tam():
        a_hat = ntt(a)
        s_hat = ntt(s_mod)
        prod_hat = carp_ntt(a_hat, s_hat)
        return ntt_ters(prod_hat)

    med_ntt, iqr_ntt = olc_medyan_iqr(ntt_tam, tekrar=1000, isinma=50)
    sonuclar.append(["NTT (Forward+Mul+Inv)", med_ntt, iqr_ntt])

    # NTT sadece çarpım (Forward NTT zaten yapılmış varsayıldığında)
    a_h = ntt(a)
    s_h = ntt(s_mod)
    med_ntt_mul, iqr_ntt_mul = olc_medyan_iqr(lambda: carp_ntt(a_h, s_h), tekrar=3000, isinma=100)
    sonuclar.append(["NTT (Sadece MultiplyNTTs)", med_ntt_mul, iqr_ntt_mul])

    # 3. 8 Kronecker Varyantı
    for v in VARYANTLAR:
        girdi_a = a_merkez if v.isaretli else a
        girdi_s = s if v.isaretli else s_mod
        med_v, iqr_v = olc_medyan_iqr(
            lambda v=v, ga=girdi_a, gs=girdi_s: v.ic_carpim([ga], [gs], 3),
            tekrar=1000,
            isinma=50,
        )
        sonuclar.append([f"KS: {v.ad}", med_v, iqr_v])

    return sonuclar


# --- E3.3: Kronecker Süre Dağılımı (Breakdown) ---
def e33_deneyi():
    rng = random.Random(TOHUM)
    a_m = [merkezle(rng.randrange(Q)) for _ in range(N)]
    s_m = [rng.randint(-3, 3) for _ in range(N)]

    varyant_adlari = [
        "isaretsiz32-dongu",
        "isaretsiz32-bayt",
        "isaretli22-dongu",
        "isaretli24-bayt",
        "isaretli22-negmod",
        "isaretli24-bayt-negmod",
    ]
    sonuclar = []

    for vad in varyant_adlari:
        v = VARYANT[vad]
        girdi_a = a_m if v.isaretli else [x % Q for x in a_m]
        girdi_s = s_m if v.isaretli else [x % Q for x in s_m]

        # Paketleme
        t_pack_a, _ = olc_medyan_iqr(lambda v=v, ga=girdi_a: v._paketle(ga), tekrar=2000, isinma=50)
        t_pack_s, _ = olc_medyan_iqr(lambda v=v, gs=girdi_s: v._paketle(gs), tekrar=2000, isinma=50)
        t_pack = t_pack_a + t_pack_s

        # Tamsayı Çarpımı
        pa = v._paketle(girdi_a)
        ps = v._paketle(girdi_s)
        M = (1 << (N * v.l)) + 1 if v.negasiklik_mod else None

        def carpmul(pa=pa, ps=ps, M=M):
            u = pa * ps
            if M is not None:
                u %= M
            return u

        t_mul, _ = olc_medyan_iqr(carpmul, tekrar=5000, isinma=100)

        # Çözme / Açma ve İndirgeme
        urun = carpmul()
        t_unpack, _ = olc_medyan_iqr(lambda v=v, u=urun: v._coz(u), tekrar=2000, isinma=50)

        toplam = t_pack + t_mul + t_unpack
        sonuclar.append([vad, t_pack, t_mul, t_unpack, toplam])

    return sonuclar


# --- E3.4: Tam ML-KEM Uçtan Uca Performansı ---
def e34_deneyi(tekrar: int = 100):
    motorlar = [
        ("NTT (FIPS 203)", kpke),
        ("KS (isaretli24-bayt-negmod)", KroneckerPKE(VARYANT["isaretli24-bayt-negmod"])),
        ("KS (isaretli22-negmod)", KroneckerPKE(VARYANT["isaretli22-negmod"])),
    ]
    parametreler = [ML_KEM_512, ML_KEM_768, ML_KEM_1024]
    sonuclar = []

    for p in parametreler:
        for motor_ad, pke in motorlar:
            # Keygen
            med_kg, iqr_kg = olc_medyan_iqr(
                lambda p=p, pke=pke: mlkem.keygen(p, pke=pke), tekrar=tekrar, isinma=5
            )
            # Encaps
            ek, dk = mlkem.keygen(p, pke=pke)
            med_enc, iqr_enc = olc_medyan_iqr(
                lambda ek=ek, p=p, pke=pke: mlkem.encaps(ek, p, pke=pke),
                tekrar=tekrar,
                isinma=5,
            )
            # Decaps
            _K, c = mlkem.encaps(ek, p, pke=pke)
            med_dec, iqr_dec = olc_medyan_iqr(
                lambda dk=dk, c=c, p=p, pke=pke: mlkem.decaps(dk, c, p, pke=pke),
                tekrar=tekrar,
                isinma=5,
            )

            sonuclar.append([p.ad, motor_ad, med_kg, iqr_kg, med_enc, iqr_enc, med_dec, iqr_dec])

    return sonuclar


def main():
    basla = time.time()
    baslik = f"# tohum={TOHUM} python={platform.python_version()} makine={platform.machine()}"

    print("E3.1: Bigint çarpım süreleri ölçülüyor...", flush=True)
    res_31 = e31_deneyi(15000)
    with open(KLASOR / "veri_e31.csv", "w", newline="") as f:
        yaz = csv.writer(f)
        yaz.writerow([baslik])
        yaz.writerow(["etiket", "bit", "medyan_us", "iqr_us"])
        yaz.writerows(res_31)
    base_8192 = res_31[0][2]
    val_5632 = res_31[2][2]
    print(
        f"E3.1 tamamlandı: 8192b = {base_8192:.2f} µs, 5632b = {val_5632:.2f} µs (Hızlanma: {base_8192 / val_5632:.2f}x)",
        flush=True,
    )

    print("E3.2: Tek polinom çarpım süreleri ölçülüyor...", flush=True)
    res_32 = e32_deneyi()
    with open(KLASOR / "veri_e32.csv", "w", newline="") as f:
        yaz = csv.writer(f)
        yaz.writerow([baslik])
        yaz.writerow(["yontem", "medyan_us", "iqr_us"])
        yaz.writerows(res_32)
    print("E3.2 tamamlandı.", flush=True)

    print("E3.3: Kronecker süre dağılımı (breakdown) ölçülüyor...", flush=True)
    res_33 = e33_deneyi()
    with open(KLASOR / "veri_e33.csv", "w", newline="") as f:
        yaz = csv.writer(f)
        yaz.writerow([baslik])
        yaz.writerow(["varyant", "paketleme_us", "carpim_us", "cozme_us", "toplam_us"])
        yaz.writerows(res_33)
    print("E3.3 tamamlandı.", flush=True)

    print("E3.4: Tam ML-KEM KeyGen/Encaps/Decaps ölçülüyor...", flush=True)
    res_34 = e34_deneyi(100)
    with open(KLASOR / "veri_e34.csv", "w", newline="") as f:
        yaz = csv.writer(f)
        yaz.writerow([baslik])
        yaz.writerow(
            [
                "parametre",
                "motor",
                "keygen_med_us",
                "keygen_iqr_us",
                "encaps_med_us",
                "encaps_iqr_us",
                "decaps_med_us",
                "decaps_iqr_us",
            ]
        )
        yaz.writerows(res_34)
    print("E3.4 tamamlandı.", flush=True)

    print(f"\nTüm performans deneyleri tamamlandı. Toplam süre: {time.time() - basla:.1f} sn")


if __name__ == "__main__":
    main()

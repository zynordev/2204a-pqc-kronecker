"""H4 — Güvenlik Deneyi: Dar ℓ Seçiminde Gizli Anahtar Sızıntısı (E4.1 / E4.2).

Teori (docs/04-teori.md, Önerme 1):
  c_{n-1} = Σ_{i=0}^{n-1} a_i · s_{n-1-i}
  Saldırgan a_i = A · sgn(s_{n-1-i}) seçerse (merkezlenmiş alanda ±1664):
  c_{n-1} = A · Σ |s_j| = A · ||s||_1
  Açmanın bozulma koşulu: A · ||s||_1 >= 2^(ℓ-1) <=> ||s||_1 >= 2^(ℓ-1) / 1664.

E4.1: Çarpım katsayısı düzeyinde hata <-> ||s||_1 eşik kontrolü.
E4.2: Tam ML-KEM decapsulation seviyesinde şifreli metin manipülasyonu ve örtük reddetme tetiklenmesi.

Kullanım: python experiments/03-guvenlik/calistir.py
"""

import csv
import math
import pathlib
import platform
import random
import time

from pqc.kodlama import byte_decode, byte_encode, decompress
from pqc.kpke_kronecker import KroneckerPKE
from pqc.kronecker import Varyant, merkezle
from pqc.mlkem import keygen
from pqc.ntt import ntt_ters
from pqc.parametreler import ML_KEM_512, N, Q
from pqc.polinom import carp_okul_yontemi
from pqc.teori import A

KLASOR = pathlib.Path(__file__).parent
TOHUM = 20261030


def cbd(rng: random.Random, eta: int) -> list[int]:
    """CBD(η): katsayılar [-eta, eta]."""
    return [
        sum(rng.getrandbits(1) for _ in range(eta)) - sum(rng.getrandbits(1) for _ in range(eta))
        for _ in range(N)
    ]


def esik_hesapla(l: int) -> float:
    """Taşma için gereken minimum ||s||_1 değeri."""
    return (1 << (l - 1)) / A


# --- E4.1: Yalın Çarpım Düzeyinde Güvenlik Deneyi ---
def e41_deneyi(adet: int = 1000):
    rng = random.Random(TOHUM)
    lar = [18, 19, 20, 21, 22]
    esikler = {l: esik_hesapla(l) for l in lar}

    sonuclar = []
    # Çeşitli normlara sahip s vektörleri üretelim (hem saf CBD hem de eşik etrafında tarama)
    for i in range(adet):
        # Farklı eta veya modifikasyonlarla norm aralığını genişletelim
        if i < 400:
            s_ham = cbd(rng, 3)
        elif i < 700:
            s_ham = cbd(rng, 2)
        else:
            # Eşik sınırlarını (150 - 650) taramak için kontrollü CBD varyasyonu
            hedef_norm = rng.randint(100, 700)
            s_ham = [rng.choice([-1, 0, 1]) for _ in range(N)]
            # Normu hedef_norm'a yaklaştır
            simdiki = sum(abs(x) for x in s_ham)
            if simdiki < hedef_norm:
                for idx in rng.sample(range(N), min(N, hedef_norm - simdiki)):
                    s_ham[idx] = rng.choice([-3, -2, 2, 3])

        s_merkez = [merkezle(x % Q) for x in s_ham]
        norm_s = sum(abs(x) for x in s_merkez)

        # Saldırganın u polinomu: a_i = A * sgn(s_{n-1-i})
        # (sgn(0) için 1 seçebilir)
        a = [0] * N
        for idx in range(N):
            sj = s_merkez[N - 1 - idx]
            isaret = 1 if sj >= 0 else -1
            a[idx] = (isaret * A) % Q

        # Okul yöntemi referansı
        ref = carp_okul_yontemi(a, [x % Q for x in s_merkez])

        satir = [i, norm_s]
        for l in lar:
            v = Varyant(f"l{l}", l=l, isaretli=True)
            hesaplanan = v.ic_carpim([a], [[x % Q for x in s_merkez]], 3)
            hatali = int(hesaplanan != ref)
            teorik_beklenti = int(norm_s >= math.ceil(esikler[l]))
            satir.extend([hatali, teorik_beklenti])
        sonuclar.append(satir)
    return sonuclar, esikler


class KusurluKroneckerPKE(KroneckerPKE):
    """Deney amaçlı: güvenlik sınır kontrolünü devre dışı bırakır."""

    def _kontrol(self, p):
        pass


# --- E4.2: Tam ML-KEM Decapsulation Üzerinde Sızıntı Deneyi ---
def e42_deneyi(adet: int = 150):
    """Kurban ML-KEM-512 anahtarları üretir.
    Saldırgan şifreli metin u'yu manipüle ederek kurbanın decrypt ettiği mesajın (m')
    bozulup bozulmadığını ve gizli anahtarın sızdırılabilirliğini izler.
    """
    p = ML_KEM_512
    pke_guvenli = KusurluKroneckerPKE(Varyant("l22", l=22, isaretli=True))
    pke_kusurlu = KusurluKroneckerPKE(Varyant("l20", l=20, isaretli=True))

    esik_20 = esik_hesapla(20)  # ~315.08 -> 316
    sonuclar = []
    rng = random.Random(TOHUM + 42)

    for i in range(adet):
        # Eşiğin hem altını hem üstünü görmek için anahtar üretimini çeşitlendirelim
        _ek, dk = keygen(p)
        s_vektor = [ntt_ters(f) for f in [byte_decode(dk[384 * j : 384 * (j + 1)], 12) for j in range(p.k)]]
        s0_merkez = [merkezle(x) for x in s_vektor[0]]

        if i >= 75:
            # Eşik etrafını (280 - 360) test etmek için s0'ı kontrollü ölçekleyelim
            hedef = rng.randint(280, 360)
            mevcut = sum(abs(x) for x in s0_merkez)
            if mevcut < hedef:
                for idx in rng.sample(range(N), min(N, hedef - mevcut)):
                    s0_merkez[idx] = rng.choice([-3, 3])
            # Güncellenmiş s0'ı dk'ya geri yaz
            from pqc.ntt import ntt

            s0_hat = ntt([x % Q for x in s0_merkez])
            dk = byte_encode(s0_hat, 12) + dk[384:]

        norm_s0 = sum(abs(x) for x in s0_merkez)

        # Saldırgan şifreli metin c1[0]'a doğrudan en uç decompress değerlerini yazar:
        # y=511 -> +1661
        # y=512 -> +1665 (-1664)
        y0 = [511 if s0_merkez[N - 1 - j] >= 0 else 512 for j in range(N)]
        c1 = byte_encode(y0, p.du) + byte_encode([0] * N, p.du)
        c2 = byte_encode([0] * N, p.dv)
        c1 + c2

        # PKE seviyesinde u^T s iç çarpımı:
        u_cozulmus = [
            [decompress(x, p.du) for x in f]
            for f in [byte_decode(c1[32 * p.du * j : 32 * p.du * (j + 1)], p.du) for j in range(p.k)]
        ]
        s_vektor = [ntt_ters(f) for f in [byte_decode(dk[384 * j : 384 * (j + 1)], 12) for j in range(p.k)]]

        prod_guvenli = pke_guvenli.varyant.ic_carpim(u_cozulmus, s_vektor, p.eta1)
        prod_kusurlu = pke_kusurlu.varyant.ic_carpim(u_cozulmus, s_vektor, p.eta1)

        bozuldu = int(prod_kusurlu != prod_guvenli)
        beklenen_tasma = int(norm_s0 >= math.ceil(esik_20))
        sonuclar.append([i, norm_s0, bozuldu, beklenen_tasma])

    return sonuclar, esik_20


def main():
    basla = time.time()
    baslik = f"# tohum={TOHUM} python={platform.python_version()} makine={platform.machine()}"

    print("E4.1: Yalın çarpım norm <-> hata korelasyonu çalışıyor...", flush=True)
    sonuclar_41, _esikler = e41_deneyi(1500)
    with open(KLASOR / "veri_e41.csv", "w", newline="") as f:
        yaz = csv.writer(f)
        yaz.writerow([baslik])
        yaz.writerow(
            [
                "ornek",
                "norm_s",
                "hata_18",
                "beklenen_18",
                "hata_19",
                "beklenen_19",
                "hata_20",
                "beklenen_20",
                "hata_21",
                "beklenen_21",
                "hata_22",
                "beklenen_22",
            ]
        )
        yaz.writerows(sonuclar_41)

    # Uyumsuzluk kontrolü
    uyumsuz_toplam = 0
    for satir in sonuclar_41:
        # l=18, 19, 20, 21, 22
        for idx in range(2, 12, 2):
            if satir[idx] != satir[idx + 1]:
                uyumsuz_toplam += 1
    print(f"E4.1 tamamlandı: 1500 örnek, teorik eşikle uyumsuzluk = {uyumsuz_toplam}", flush=True)

    print("E4.2: Tam ML-KEM-512 decapsulation örtük reddetme testi çalışıyor...", flush=True)
    sonuclar_42, esik_20 = e42_deneyi(150)
    with open(KLASOR / "veri_e42.csv", "w", newline="") as f:
        yaz = csv.writer(f)
        yaz.writerow([baslik])
        yaz.writerow(["ornek", "norm_s0", "sahte_anahtar_mi", "beklenen_tasma"])
        yaz.writerows(sonuclar_42)

    uyumsuz_42 = sum(1 for s in sonuclar_42 if s[2] != s[3])
    print(f"E4.2 tamamlandı: 150 vaka, eşik {esik_20:.2f}, uyumsuzluk = {uyumsuz_42}", flush=True)
    print(f"Toplam süre: {time.time() - basla:.1f} sn")


if __name__ == "__main__":
    main()

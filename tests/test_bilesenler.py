"""ML-KEM bileşenlerinin standarttan bağımsız özellik testleri."""

import random

import pytest

from pqc import kodlama, mlkem, ntt, ornekleme
from pqc.ozetler import J
from pqc.parametreler import PARAMETRELER, N, Q
from pqc.polinom import carp_okul_yontemi

rng = random.Random(2204)


def _rastgele_polinom():
    return [rng.randrange(Q) for _ in range(N)]


# --- kodlama (Bölüm 4.2.1) ---

def test_bit_bayt_ters():
    B = bytes(rng.randrange(256) for _ in range(64))
    assert kodlama.bits_to_bytes(kodlama.bytes_to_bits(B)) == B


@pytest.mark.parametrize("d", range(1, 13))
def test_encode_decode_ters(d):
    m = 2**d if d < 12 else Q
    F = [rng.randrange(m) for _ in range(N)]
    B = kodlama.byte_encode(F, d)
    assert len(B) == 32 * d
    assert kodlama.byte_decode(B, d) == F


@pytest.mark.parametrize("d", [1, 4, 5, 10, 11])
def test_sikistirma_hata_siniri(d):
    # FIPS 203 Bölüm 4.2.1: |Decompress(Compress(x)) − x| mod± q ≤ ⌈q / 2^(d+1)⌋
    sinir = (Q + (1 << d)) >> (d + 1)
    for x in range(Q):
        fark = (kodlama.decompress(kodlama.compress(x, d), d) - x) % Q
        assert min(fark, Q - fark) <= sinir


# --- NTT (Bölüm 4.3) ---

def test_zeta_bilinen_degerler():
    assert ntt.ZETALAR[0] == 1
    assert ntt.ZETALAR[1] == 1729  # 17^64 mod 3329
    assert pow(ntt.ZETA, 256, Q) == 1 and pow(ntt.ZETA, 128, Q) == Q - 1


def test_ntt_ters_ntt():
    for _ in range(20):
        f = _rastgele_polinom()
        assert ntt.ntt_ters(ntt.ntt(f)) == f


def test_ntt_carpimi_okul_yontemiyle_ayni():
    for _ in range(20):
        f, g = _rastgele_polinom(), _rastgele_polinom()
        assert ntt.ntt_ters(ntt.carp_ntt(ntt.ntt(f), ntt.ntt(g))) == carp_okul_yontemi(f, g)


# --- örnekleme (Bölüm 4.2.2) ---

@pytest.mark.parametrize("eta", [2, 3])
def test_cbd_araligi(eta):
    f = ornekleme.sample_poly_cbd(bytes(rng.randrange(256) for _ in range(64 * eta)), eta)
    assert len(f) == N
    assert all(x <= eta or x >= Q - eta for x in f)


def test_sample_ntt():
    a = ornekleme.sample_ntt(bytes(34))
    assert len(a) == N and all(0 <= x < Q for x in a)


# --- ML-KEM uçtan uca ---

@pytest.mark.parametrize("ad", PARAMETRELER)
def test_kapsulle_ac(ad):
    p = PARAMETRELER[ad]
    ek, dk = mlkem.keygen(p)
    K, c = mlkem.encaps(ek, p)
    assert len(ek) == p.ek_uzunluk and len(dk) == p.dk_uzunluk and len(c) == p.c_uzunluk
    assert mlkem.decaps(dk, c, p) == K


@pytest.mark.parametrize("ad", PARAMETRELER)
def test_ortuk_reddetme(ad):
    p = PARAMETRELER[ad]
    ek, dk = mlkem.keygen(p)
    K, c = mlkem.encaps(ek, p)
    bozuk = bytes([c[0] ^ 1]) + c[1:]
    z = dk[-32:]
    assert mlkem.decaps(dk, bozuk, p) == J(z + bozuk) != K


def test_gecersiz_girdiler_reddedilir():
    p = PARAMETRELER["ML-KEM-512"]
    ek, dk = mlkem.keygen(p)
    with pytest.raises(ValueError):
        mlkem.encaps(ek[:-1], p)
    with pytest.raises(ValueError):
        mlkem.encaps(b"\xff" * 384 * p.k + ek[-32:], p)  # katsayılar ≥ q
    _, c = mlkem.encaps(ek, p)
    with pytest.raises(ValueError):
        mlkem.decaps(dk, c[:-1], p)

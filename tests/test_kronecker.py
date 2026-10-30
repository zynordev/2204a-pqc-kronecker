"""Kronecker varyantları: NTT'ye karşı doğruluk, kenar durumlar, Teorem 1 sınırının keskinliği."""

import random

import pytest

from pqc.kpke import _ic_carpim
from pqc.kronecker import VARYANT, VARYANTLAR, Varyant
from pqc.ntt import ntt, ntt_ters
from pqc.parametreler import ML_KEM_512, ML_KEM_768, ML_KEM_1024, PARAMETRELER, N, Q
from pqc.teori import A

rng = random.Random(2204)


def _referans(buyuk, kucuk):
    """NTT ile Σ buyuk_j·kucuk_j (NTT, test_bilesenler'de okul yöntemine karşı doğrulandı)."""
    return ntt_ters(_ic_carpim([ntt(f) for f in buyuk], [ntt(f) for f in kucuk]))


def _rastgele(k, eta):
    buyuk = [[rng.randrange(Q) for _ in range(N)] for _ in range(k)]
    kucuk = [[rng.randint(-eta, eta) % Q for _ in range(N)] for _ in range(k)]
    return buyuk, kucuk


@pytest.mark.parametrize("v", VARYANTLAR, ids=lambda v: v.ad)
@pytest.mark.parametrize("p", PARAMETRELER.values(), ids=lambda p: p.ad)
def test_rastgele_ntt_ile_ayni(v, p):
    assert v.guvenli_mi(p)
    for _ in range(5):
        buyuk, kucuk = _rastgele(p.k, p.eta1)
        assert v.ic_carpim(buyuk, kucuk, p.eta1) == _referans(buyuk, kucuk)


def _en_kotu_negasiklik(k0, eta):
    """Negasiklik k0. katsayıyı en büyük yapan girdi: s ≡ η, a_i = +A (i ≤ k0), −A (i > k0).
    i > k0 terimleri X^n = −1 ile işaret değiştirdiğinden hepsi +A·η katkı verir → n·A·η."""
    a = [A if i <= k0 else -A for i in range(N)]
    return [[x % Q for x in a]], [[eta] * N]


@pytest.mark.parametrize("v", VARYANTLAR, ids=lambda v: v.ad)
@pytest.mark.parametrize("k0", [0, 127, N - 1])
def test_en_kotu_durum(v, k0):
    buyuk, kucuk = _en_kotu_negasiklik(k0, 3)
    assert v.ic_carpim(buyuk, kucuk, 3) == _referans(buyuk, kucuk)
    # tam çarpımın en büyük katsayısı (c_{n−1} = n·A·η) ve işaretin tersi
    for isaret in (1, -1):
        buyuk = [[(isaret * A) % Q] * N]
        assert v.ic_carpim(buyuk, [[3] * N], 3) == _referans(buyuk, [[3] * N])


@pytest.mark.parametrize("v", VARYANTLAR, ids=lambda v: v.ad)
def test_sifir_polinom(v):
    sifir = [[0] * N]
    assert v.ic_carpim(sifir, [[1] * N], 3) == [0] * N
    assert v.ic_carpim([[5] * N], sifir, 3) == [0] * N


def test_sinir_keskin():
    """Önerme 1: l = l_min − 1 (21) ile en kötü girdi bozulur, l_min (22) ile bozulmaz."""
    buyuk, kucuk = [[A] * N], [[3] * N]
    ref = _referans(buyuk, kucuk)
    assert Varyant("l22", l=22, isaretli=True).ic_carpim(buyuk, kucuk, 3) == ref
    assert Varyant("l21", l=21, isaretli=True).ic_carpim(buyuk, kucuk, 3) != ref
    buyuk, kucuk = _en_kotu_negasiklik(N - 1, 3)
    ref = _referans(buyuk, kucuk)
    assert Varyant("n22", l=22, isaretli=True, negasiklik_mod=True).ic_carpim(buyuk, kucuk, 3) == ref
    assert Varyant("n21", l=21, isaretli=True, negasiklik_mod=True).ic_carpim(buyuk, kucuk, 3) != ref


def test_gerekli_l_tablosu():
    """docs/04-teori.md Teorem 1 ve Sonuç 1 tablosu."""
    tek = VARYANT["isaretli22-dongu"]
    modul = VARYANT["isaretli24-bayt-modul"]
    isaretsiz = VARYANT["isaretsiz32-dongu"]
    assert [tek.gerekli_l(p) for p in (ML_KEM_512, ML_KEM_768, ML_KEM_1024)] == [22, 21, 21]
    assert [modul.gerekli_l(p) for p in (ML_KEM_512, ML_KEM_768, ML_KEM_1024)] == [23, 23, 23]
    assert [isaretsiz.gerekli_l(p) for p in (ML_KEM_512, ML_KEM_768, ML_KEM_1024)] == [32, 32, 32]
    isaretsiz_modul = Varyant("x", l=32, isaretli=False, modul_toplami=True)
    assert not isaretsiz_modul.guvenli_mi(ML_KEM_512)  # 2·256·3328² ≥ 2^32


def test_gecersiz_varyantlar():
    with pytest.raises(ValueError):
        Varyant("x", l=22, isaretli=True, bayt=True)
    with pytest.raises(ValueError):
        Varyant("x", l=32, isaretli=False, negasiklik_mod=True)


def test_kucuk_aralik_disi_reddedilir():
    with pytest.raises(ValueError):
        VARYANT["isaretli22-dongu"].ic_carpim([[1] * N], [[4] * N], 3)

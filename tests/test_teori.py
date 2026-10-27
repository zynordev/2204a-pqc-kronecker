"""docs/04-teori.md Teorem 1 tablosunun sayısal kontrolü."""

from pqc.parametreler import N, Q
from pqc.teori import A, katsayi_siniri, l_min_isaretli, l_min_isaretsiz


def test_tablo_eta3():
    assert katsayi_siniri(N, A, 3) == 1_277_952
    assert l_min_isaretli(N, A, 3) == 22


def test_tablo_eta2():
    assert katsayi_siniri(N, A, 2) == 851_968
    assert l_min_isaretli(N, A, 2) == 21


def test_tablo_isaretsiz():
    assert katsayi_siniri(N, Q - 1, Q - 1) == 2_835_349_504
    assert l_min_isaretsiz(N, Q - 1, Q - 1) == 32


def test_l_min_gercekten_en_kucuk():
    for eta in (2, 3):
        b = katsayi_siniri(N, A, eta)
        l = l_min_isaretli(N, A, eta)
        assert b < 2 ** (l - 1)
        assert b >= 2 ** (l - 2)

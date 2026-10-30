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


def test_model2_terim_sayilari():
    """Her a_i·s_j terimi tam olarak bir dilime düşer: toplam n² (tam ve negasiklik)."""
    from pqc.teori import terim_sayilari

    assert sum(terim_sayilari(N, False)) == N * N
    assert sum(terim_sayilari(N, True)) == N * N
    assert max(terim_sayilari(N, False)) == N


def test_model2_monoton_ve_sinirli():
    from pqc.teori import model_hata

    onceki = 1.0
    for l in range(14, 23):
        bag, birlesim = model_hata(l, N, 3)
        assert 0.0 <= bag <= birlesim <= 1.0
        assert bag <= onceki
        onceki = bag
    # neg her dilimde n terim → aynı l'de daha olası; k·η aynıysa model aynı
    assert model_hata(17, N, 3, negasiklik=True)[0] > model_hata(17, N, 3)[0]
    assert model_hata(17, N, 3, terim=2) == model_hata(17, N, 2, terim=3)

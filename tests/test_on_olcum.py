"""Ön ölçüm betiğindeki çarpım yöntemlerinin schoolbook'a karşı duman testi."""

import importlib.util
import pathlib
import random

import pytest

from pqc.teori import N, Q

_YOL = pathlib.Path(__file__).parents[1] / "experiments" / "00-on-olcum" / "ks_bench.py"
_spec = importlib.util.spec_from_file_location("ks_bench", _YOL)
ks = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ks)


def _ornek(rng, eta):
    a = [rng.randrange(Q) for _ in range(N)]
    s = [rng.randint(-eta, eta) for _ in range(N)]
    return a, s, [x % Q for x in s], [ks.centered(x) for x in a]


@pytest.mark.parametrize("eta,l", [(3, 22), (2, 21)])
def test_tum_yontemler_schoolbook_ile_ayni(eta, l):
    rng = random.Random(2204)
    for _ in range(20):
        a, s, sm, ac = _ornek(rng, eta)
        ref = ks.schoolbook(a, sm)
        assert ks.ntt_mul(a, sm) == ref
        assert ks.ks_mul(a, sm, 32, False) == ref
        assert ks.ks_mul(ac, s, l, True) == ref
        assert ks.ks_negacyclic(ac, s, l) == ref


def test_en_kotu_durum_l22_dogru_l21_bozuk():
    # Önerme 1: a ve s serbestken sınıra tam ulaşılır (s tamamen +3, a tamamen +1664).
    a = [1664] * N
    s = [3] * N
    ref = ks.schoolbook([x % Q for x in a], s)
    assert ks.ks_mul(a, s, 22, True) == ref
    assert ks.ks_mul(a, s, 21, True) != ref

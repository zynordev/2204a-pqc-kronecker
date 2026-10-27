"""docs/04-teori.md'deki sınırların kod karşılığı."""

from pqc.parametreler import Q

A = (Q - 1) // 2  # merkezlenmiş katsayının en büyük mutlak değeri: 1664


def katsayi_siniri(n: int, a_max: int, b_max: int, terim: int = 1) -> int:
    """Teorem 1: tam çarpımdaki her |c_k| en fazla n * a_max * b_max.

    `terim` > 1: Σ_j a_j·b_j iç çarpımı açılmadan toplanırsa (Sonuç 1) sınır `terim` katına çıkar.
    """
    return terim * n * a_max * b_max


def l_min_isaretli(n: int, a_max: int, b_max: int, terim: int = 1) -> int:
    """Teorem 1: sınır < 2^(l-1) koşulunu sağlayan en küçük l (Lemma 1 ile dengeli açma)."""
    return katsayi_siniri(n, a_max, b_max, terim).bit_length() + 1


def l_min_isaretsiz(n: int, a_max: int, b_max: int, terim: int = 1) -> int:
    """Negatif olmayan katsayılar: sınır < 2^l koşulunu sağlayan en küçük l."""
    return katsayi_siniri(n, a_max, b_max, terim).bit_length()

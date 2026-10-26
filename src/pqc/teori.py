"""docs/04-teori.md'deki sınırların kod karşılığı."""

N = 256
Q = 3329
A = (Q - 1) // 2  # merkezlenmiş katsayının en büyük mutlak değeri: 1664


def katsayi_siniri(n: int, a_max: int, b_max: int) -> int:
    """Teorem 1: tam çarpımdaki her |c_k| en fazla n * a_max * b_max."""
    return n * a_max * b_max


def l_min_isaretli(n: int, a_max: int, b_max: int) -> int:
    """Teorem 1: n*a_max*b_max < 2^(l-1) koşulunu sağlayan en küçük l (Lemma 1 ile dengeli açma)."""
    return katsayi_siniri(n, a_max, b_max).bit_length() + 1


def l_min_isaretsiz(n: int, a_max: int, b_max: int) -> int:
    """Negatif olmayan katsayılar: n*a_max*b_max < 2^l koşulunu sağlayan en küçük l."""
    return katsayi_siniri(n, a_max, b_max).bit_length()

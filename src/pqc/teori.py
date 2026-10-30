"""docs/04-teori.md'deki sınırların ve olasılık modelinin (Model 2) kod karşılığı."""

import math

from pqc.parametreler import Q

A = (Q - 1) // 2  # merkezlenmiş katsayının en büyük mutlak değeri: 1664
VAR_A = (Q * Q - 1) / 12  # {−1664, …, 1664} üzerinde düzgün dağılımın varyansı: 923 520


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


# --- Model 2: rastgele girdide taşma olasılığı (normal yaklaşım) ---

def terim_sayilari(n: int, negasiklik: bool) -> list[int]:
    """Açılan her dilimdeki a_i·s_j terimi sayısı.

    Tam çarpım (2n − 1 dilim): T_k = min(k + 1, 2n − 1 − k) (Teorem 1 (i)).
    Negasiklik (n dilim, d_k = c_k − c_{k+n}): her dilim tam olarak n terim (Önerme 2).
    """
    if negasiklik:
        return [n] * n
    return [min(k + 1, 2 * n - 1 - k) for k in range(2 * n - 1)]


def dilim_tasma_olasiligi(yari_taban: float, sigma: float) -> float:
    """N(0, σ²) bir katsayının dengeli rakam aralığı dışına çıkma olasılığı ≈ 2·Φ(−(B/2)/σ).

    B = 2^l için aralık D_l = [−2^(l−1), 2^(l−1)), yani yari_taban = 2^(l−1).
    """
    return math.erfc(yari_taban / (sigma * math.sqrt(2)))


def model_hata_taban(yari_taban: float, n: int, eta: int, terim: int = 1,
                     negasiklik: bool = False) -> tuple[float, float]:
    """Model 2: rastgele girdide (a düzgün, s ~ CBD(η)) B tabanında açmanın bozulma olasılığı.

    Her dilim yaklaşık N(0, σ_k²), σ_k² = terim·T_k·Var(a)·Var(s), Var(s) = η/2.
    Dönüş: (bağımsızlık yaklaşımı 1 − Π(1 − p_k), birleşim üst sınırı min(1, Σ p_k)).
    Dilimler bağımsız değildir (aynı a_i birçok dilimde geçer); bu yüzden ilki yaklaşık, ikincisi
    normal yaklaşım altında bir üst sınırdır.
    """
    var_s = eta / 2
    log_dogru = 0.0
    toplam = 0.0
    for t in terim_sayilari(n, negasiklik):
        p = dilim_tasma_olasiligi(yari_taban, math.sqrt(terim * t * VAR_A * var_s))
        toplam += p
        log_dogru += math.log1p(-p) if p < 1 else -math.inf
    return -math.expm1(log_dogru), min(1.0, toplam)


def model_hata(l: int, n: int, eta: int, terim: int = 1, negasiklik: bool = False) -> tuple[float, float]:
    """model_hata_taban, B = 2^l için."""
    return model_hata_taban(float(1 << (l - 1)), n, eta, terim, negasiklik)

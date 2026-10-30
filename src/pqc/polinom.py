"""R_q = Z_q[X]/(X^256 + 1) halkasında temel işlemler.

`carp_okul_yontemi` projenin altın standardıdır (ADR 0002): yavaş ama apaçık doğru.
Diğer tüm çarpım yöntemleri buna karşı test edilir.
"""

from pqc.parametreler import N, Q


def topla(f: list[int], g: list[int]) -> list[int]:
    return [(a + b) % Q for a, b in zip(f, g)]


def cikar(f: list[int], g: list[int]) -> list[int]:
    return [(a - b) % Q for a, b in zip(f, g)]


def carp_okul_yontemi(f: list[int], g: list[int]) -> list[int]:
    """Negasiklik okul yöntemi: X^256 = −1 olduğundan i + j ≥ 256 terimleri çıkarılır."""
    c = [0] * N
    for i in range(N):
        for j in range(N):
            if i + j < N:
                c[i + j] += f[i] * g[j]
            else:
                c[i + j - N] -= f[i] * g[j]
    return [x % Q for x in c]

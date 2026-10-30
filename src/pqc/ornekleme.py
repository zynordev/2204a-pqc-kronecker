"""FIPS 203, Bölüm 4.2.2: NTT alanında düzgün örnekleme ve merkezli binom dağılımı (CBD)."""

import hashlib

from pqc.kodlama import bytes_to_bits
from pqc.parametreler import N, Q


def sample_ntt(B: bytes) -> list[int]:
    """Algoritma 7. B = ρ‖j‖i (34 bayt). XOF = SHAKE128.

    Standart XOF'tan 3'er bayt okur; hashlib'de akış olmadığından yeterince uzun bir çıktı
    alınır. SHAKE çıktısının ilk n baytı, istenen uzunluktan bağımsızdır; bu yüzden çıktı yetmezse
    daha uzununu istemek aynı akışın devamını verir.
    """
    uzunluk = 840
    while True:
        C = hashlib.shake_128(B).digest(uzunluk)
        a = []
        for p in range(0, uzunluk - 2, 3):
            d1 = C[p] + 256 * (C[p + 1] % 16)
            d2 = C[p + 1] // 16 + 16 * C[p + 2]
            if d1 < Q:
                a.append(d1)
            if d2 < Q and len(a) < N:
                a.append(d2)
            if len(a) == N:
                return a
        uzunluk *= 2


def sample_poly_cbd(B: bytes, eta: int) -> list[int]:
    """Algoritma 8. B 64·η bayttır; katsayılar [−η, η] aralığında, mod q olarak döner."""
    b = bytes_to_bits(B)
    f = []
    for i in range(N):
        x = sum(b[2 * i * eta + j] for j in range(eta))
        y = sum(b[2 * i * eta + eta + j] for j in range(eta))
        f.append((x - y) % Q)
    return f

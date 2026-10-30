"""FIPS 203, Bölüm 4.2.1: bit/bayt dönüşümleri, kodlama ve sıkıştırma."""

from pqc.parametreler import N, Q


def bits_to_bytes(b: list[int]) -> bytes:
    """Algoritma 3. Bitler küçük uçlu (her baytın en düşük biti önce) birleştirilir."""
    B = bytearray(len(b) // 8)
    for i, bit in enumerate(b):
        B[i // 8] += bit << (i % 8)
    return bytes(B)


def bytes_to_bits(B: bytes) -> list[int]:
    """Algoritma 4. bits_to_bytes'ın tersi."""
    b = []
    for bayt in B:
        for _ in range(8):
            b.append(bayt % 2)
            bayt //= 2
    return b


def byte_encode(F: list[int], d: int) -> bytes:
    """Algoritma 5. Her katsayı d bit olarak yazılır (1 ≤ d ≤ 12)."""
    b = [0] * (N * d)
    for i in range(N):
        a = F[i]
        for j in range(d):
            b[i * d + j] = a % 2
            a = (a - b[i * d + j]) // 2
    return bits_to_bytes(b)


def byte_decode(B: bytes, d: int) -> list[int]:
    """Algoritma 6. d < 12 için katsayılar mod 2^d, d = 12 için mod q okunur."""
    m = 2**d if d < 12 else Q
    b = bytes_to_bits(B)
    return [sum(b[i * d + j] << j for j in range(d)) % m for i in range(N)]


def compress(x: int, d: int) -> int:
    """Denklem 4.7: ⌈(2^d / q)·x⌋ mod 2^d. Yuvarlama: en yakın tamsayı, eşitlikte yukarı."""
    return ((2 * (x << d) + Q) // (2 * Q)) % (1 << d)


def decompress(y: int, d: int) -> int:
    """Denklem 4.8: ⌈(q / 2^d)·y⌋."""
    return (Q * y + (1 << (d - 1))) >> d

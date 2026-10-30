"""FIPS 203, Bölüm 4.3: Sayı Teorik Dönüşüm (NTT) ve NTT alanında çarpım."""

from pqc.parametreler import N, Q

ZETA = 17  # Z_q'da 256. dereceden ilkel birim kökü


def bitrev7(r: int) -> int:
    """7 bitlik r'nin bitlerini ters çevirir."""
    return int(f"{r:07b}"[::-1], 2)


# ζ^BitRev7(i) mod q, i = 0..127 (FIPS 203, Ek A)
ZETALAR = [pow(ZETA, bitrev7(i), Q) for i in range(128)]
# ζ^(2·BitRev7(i)+1) mod q, i = 0..127 — MultiplyNTTs içindeki γ değerleri
GAMMALAR = [pow(ZETA, 2 * bitrev7(i) + 1, Q) for i in range(128)]


def ntt(f: list[int]) -> list[int]:
    """Algoritma 9."""
    f = list(f)
    i = 1
    uzunluk = 128
    while uzunluk >= 2:
        for baslangic in range(0, N, 2 * uzunluk):
            zeta = ZETALAR[i]
            i += 1
            for j in range(baslangic, baslangic + uzunluk):
                t = zeta * f[j + uzunluk] % Q
                f[j + uzunluk] = (f[j] - t) % Q
                f[j] = (f[j] + t) % Q
        uzunluk //= 2
    return f


def ntt_ters(f: list[int]) -> list[int]:
    """Algoritma 10. Sondaki 3303 = 128⁻¹ mod q."""
    f = list(f)
    i = 127
    uzunluk = 2
    while uzunluk <= 128:
        for baslangic in range(0, N, 2 * uzunluk):
            zeta = ZETALAR[i]
            i -= 1
            for j in range(baslangic, baslangic + uzunluk):
                t = f[j]
                f[j] = (t + f[j + uzunluk]) % Q
                f[j + uzunluk] = zeta * (f[j + uzunluk] - t) % Q
        uzunluk *= 2
    return [x * 3303 % Q for x in f]


def base_case_multiply(a0: int, a1: int, b0: int, b1: int, gamma: int) -> tuple[int, int]:
    """Algoritma 12: (a0 + a1·X)(b0 + b1·X) mod (X² − γ)."""
    c0 = (a0 * b0 + a1 * b1 * gamma) % Q
    c1 = (a0 * b1 + a1 * b0) % Q
    return c0, c1


def carp_ntt(f_hat: list[int], g_hat: list[int]) -> list[int]:
    """Algoritma 11 (MultiplyNTTs): NTT alanında iki polinomun çarpımı."""
    h = [0] * N
    for i in range(128):
        h[2 * i], h[2 * i + 1] = base_case_multiply(
            f_hat[2 * i], f_hat[2 * i + 1], g_hat[2 * i], g_hat[2 * i + 1], GAMMALAR[i]
        )
    return h

"""FIPS 203, Bölüm 5: K-PKE, ML-KEM'in içindeki açık anahtarlı şifreleme bileşeni.

Bu dosyadaki `_ic_carpim` çağrıları, projenin incelediği polinom çarpımlarının yeridir:
  KeyGen : t̂ = Â∘ŝ + ê         (Â düzgün, ŝ küçük)
  Encrypt: u = NTT⁻¹(Âᵀ∘ŷ) + e₁, v = NTT⁻¹(t̂ᵀ∘ŷ) + e₂ + μ   (ŷ küçük)
  Decrypt: w = v' − NTT⁻¹(ŝᵀ∘NTT(u'))   (ŝ küçük, u' saldırganın seçebileceği şifreli metinden)
"""

from pqc.kodlama import byte_decode, byte_encode, compress, decompress
from pqc.ntt import carp_ntt, ntt, ntt_ters
from pqc.ornekleme import sample_ntt, sample_poly_cbd
from pqc.ozetler import PRF, G
from pqc.parametreler import N, Parametre
from pqc.polinom import cikar, topla


def _matris_a(rho: bytes, k: int) -> list[list[list[int]]]:
    """Â[i][j] = SampleNTT(ρ‖j‖i). Â doğrudan NTT alanında üretilir."""
    return [[sample_ntt(rho + bytes([j, i])) for j in range(k)] for i in range(k)]


def _ic_carpim(satir: list[list[int]], vektor: list[list[int]]) -> list[int]:
    """NTT alanında Σ_j satir[j] × vektor[j]."""
    sonuc = [0] * N
    for f_hat, g_hat in zip(satir, vektor):
        sonuc = topla(sonuc, carp_ntt(f_hat, g_hat))
    return sonuc


def _vektor_kodla(v: list[list[int]], d: int) -> bytes:
    return b"".join(byte_encode(f, d) for f in v)


def _vektor_coz(B: bytes, d: int, k: int) -> list[list[int]]:
    boy = 32 * d
    return [byte_decode(B[boy * i : boy * (i + 1)], d) for i in range(k)]


def keygen(d: bytes, p: Parametre) -> tuple[bytes, bytes]:
    """Algoritma 13: (ek_PKE, dk_PKE)."""
    k = p.k
    rho, sigma = G(d + bytes([k]))
    A = _matris_a(rho, k)
    n = 0
    s = []
    for _ in range(k):
        s.append(sample_poly_cbd(PRF(p.eta1, sigma, n), p.eta1))
        n += 1
    e = []
    for _ in range(k):
        e.append(sample_poly_cbd(PRF(p.eta1, sigma, n), p.eta1))
        n += 1
    s_hat = [ntt(f) for f in s]
    e_hat = [ntt(f) for f in e]
    t_hat = [topla(_ic_carpim(A[i], s_hat), e_hat[i]) for i in range(k)]
    ek = _vektor_kodla(t_hat, 12) + rho
    dk = _vektor_kodla(s_hat, 12)
    return ek, dk


def encrypt(ek: bytes, m: bytes, r: bytes, p: Parametre) -> bytes:
    """Algoritma 14: m (32 bayt) mesajını r rastgeleliğiyle şifreler."""
    k = p.k
    t_hat = _vektor_coz(ek[: 384 * k], 12, k)
    rho = ek[384 * k : 384 * k + 32]
    A = _matris_a(rho, k)
    n = 0
    y = []
    for _ in range(k):
        y.append(sample_poly_cbd(PRF(p.eta1, r, n), p.eta1))
        n += 1
    e1 = []
    for _ in range(k):
        e1.append(sample_poly_cbd(PRF(p.eta2, r, n), p.eta2))
        n += 1
    e2 = sample_poly_cbd(PRF(p.eta2, r, n), p.eta2)
    y_hat = [ntt(f) for f in y]
    A_T = [[A[j][i] for j in range(k)] for i in range(k)]
    u = [topla(ntt_ters(_ic_carpim(A_T[i], y_hat)), e1[i]) for i in range(k)]
    mu = [decompress(b, 1) for b in byte_decode(m, 1)]
    v = topla(topla(ntt_ters(_ic_carpim(t_hat, y_hat)), e2), mu)
    c1 = _vektor_kodla([[compress(x, p.du) for x in f] for f in u], p.du)
    c2 = byte_encode([compress(x, p.dv) for x in v], p.dv)
    return c1 + c2


def decrypt(dk: bytes, c: bytes, p: Parametre) -> bytes:
    """Algoritma 15: 32 baytlık mesajı geri döndürür."""
    k = p.k
    c1 = c[: 32 * p.du * k]
    c2 = c[32 * p.du * k :]
    u = [[decompress(x, p.du) for x in f] for f in _vektor_coz(c1, p.du, k)]
    v = [decompress(x, p.dv) for x in byte_decode(c2, p.dv)]
    s_hat = _vektor_coz(dk, 12, k)
    w = cikar(v, ntt_ters(_ic_carpim(s_hat, [ntt(f) for f in u])))
    return byte_encode([compress(x, 1) for x in w], 1)

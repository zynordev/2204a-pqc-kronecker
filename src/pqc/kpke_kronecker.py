"""K-PKE (FIPS 203 Alg. 13–15), polinom çarpımları Kronecker ikamesiyle yapılarak (ADR 0003).

`kpke.py` ile satır satır aynı akış; fark yalnızca çarpımların yapıldığı alan:
  kpke.py          : çarpımlar NTT alanında (Â∘ŝ), standardın yolu
  bu dosya         : çarpımlar katsayı alanında (A·s), Kronecker ile

Standart Â'yı, t̂'yi ve ŝ'yi NTT alanında üretip sakladığı için, çıktının standartla bayt bayt aynı
kalması adına bunlar önce NTT⁻¹ ile katsayı alanına çevrilir (işaretli satırlar). Bu dönüşümler
Kronecker yolunun "standart uyumluluk bedeli"dir ve Aşama 4'te ayrıca ölçülür.
"""

from pqc.kodlama import byte_decode, byte_encode, compress, decompress
from pqc.kpke import _matris_a, _vektor_coz, _vektor_kodla
from pqc.kronecker import Varyant
from pqc.ntt import ntt, ntt_ters
from pqc.ornekleme import sample_poly_cbd
from pqc.ozetler import PRF, G
from pqc.parametreler import Parametre
from pqc.polinom import cikar, topla


class KroneckerPKE:
    def __init__(self, varyant: Varyant):
        self.varyant = varyant

    def _kontrol(self, p: Parametre) -> None:
        if not self.varyant.guvenli_mi(p):
            raise ValueError(
                f"{self.varyant.ad}: l={self.varyant.l} yetersiz, {p.ad} için en az {self.varyant.gerekli_l(p)}"
            )

    def keygen(self, d: bytes, p: Parametre) -> tuple[bytes, bytes]:
        """Algoritma 13."""
        self._kontrol(p)
        k = p.k
        rho, sigma = G(d + bytes([k]))
        A = [[ntt_ters(f) for f in satir] for satir in _matris_a(rho, k)]  # Â → A
        n = 0
        s = []
        for _ in range(k):
            s.append(sample_poly_cbd(PRF(p.eta1, sigma, n), p.eta1))
            n += 1
        e = []
        for _ in range(k):
            e.append(sample_poly_cbd(PRF(p.eta1, sigma, n), p.eta1))
            n += 1
        t = [topla(self.varyant.ic_carpim(A[i], s, p.eta1), e[i]) for i in range(k)]
        ek = _vektor_kodla([ntt(f) for f in t], 12) + rho  # t → t̂
        dk = _vektor_kodla([ntt(f) for f in s], 12)  # s → ŝ
        return ek, dk

    def encrypt(self, ek: bytes, m: bytes, r: bytes, p: Parametre) -> bytes:
        """Algoritma 14."""
        self._kontrol(p)
        k = p.k
        t = [ntt_ters(f) for f in _vektor_coz(ek[: 384 * k], 12, k)]  # t̂ → t
        rho = ek[384 * k : 384 * k + 32]
        A = [[ntt_ters(f) for f in satir] for satir in _matris_a(rho, k)]  # Â → A
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
        A_T = [[A[j][i] for j in range(k)] for i in range(k)]
        u = [topla(self.varyant.ic_carpim(A_T[i], y, p.eta1), e1[i]) for i in range(k)]
        mu = [decompress(b, 1) for b in byte_decode(m, 1)]
        v = topla(topla(self.varyant.ic_carpim(t, y, p.eta1), e2), mu)
        c1 = _vektor_kodla([[compress(x, p.du) for x in f] for f in u], p.du)
        c2 = byte_encode([compress(x, p.dv) for x in v], p.dv)
        return c1 + c2

    def decrypt(self, dk: bytes, c: bytes, p: Parametre) -> bytes:
        """Algoritma 15. u' şifreli metinden gelir (saldırgan seçebilir); s küçük çarpandır."""
        self._kontrol(p)
        k = p.k
        c1 = c[: 32 * p.du * k]
        c2 = c[32 * p.du * k :]
        u = [[decompress(x, p.du) for x in f] for f in _vektor_coz(c1, p.du, k)]
        v = [decompress(x, p.dv) for x in byte_decode(c2, p.dv)]
        s = [ntt_ters(f) for f in _vektor_coz(dk, 12, k)]  # ŝ → s
        w = cikar(v, self.varyant.ic_carpim(u, s, p.eta1))
        return byte_encode([compress(x, 1) for x in w], 1)

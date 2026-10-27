"""FIPS 203, Bölüm 8 (Tablo 2): ML-KEM parametre setleri."""

from dataclasses import dataclass

N = 256
Q = 3329


@dataclass(frozen=True)
class Parametre:
    ad: str
    k: int
    eta1: int
    eta2: int
    du: int
    dv: int

    @property
    def ek_uzunluk(self) -> int:
        return 384 * self.k + 32

    @property
    def dk_uzunluk(self) -> int:
        return 768 * self.k + 96

    @property
    def c_uzunluk(self) -> int:
        return 32 * (self.du * self.k + self.dv)


ML_KEM_512 = Parametre("ML-KEM-512", k=2, eta1=3, eta2=2, du=10, dv=4)
ML_KEM_768 = Parametre("ML-KEM-768", k=3, eta1=2, eta2=2, du=10, dv=4)
ML_KEM_1024 = Parametre("ML-KEM-1024", k=4, eta1=2, eta2=2, du=11, dv=5)

PARAMETRELER = {p.ad: p for p in (ML_KEM_512, ML_KEM_768, ML_KEM_1024)}

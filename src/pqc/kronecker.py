"""Kronecker ikamesi ile R_q'da iç çarpım: Σ_j büyük_j · küçük_j  (docs/04-teori.md).

Fikir: polinomda X yerine 2^l koyunca polinom tek bir tamsayıya dönüşür (paketleme). İki tamsayı
çarpılır, sonuç tekrar l bitlik dilimlere bölünerek (açma) çarpım polinomunun katsayıları okunur.

Bir varyant beş seçimle tanımlanır; Aşama 4 deneyleri bu seçimlerin etkisini tek tek ölçer:
  l               dilim genişliği (bit)
  isaretli        katsayılar merkezlenmiş mi ([−1664, 1664] ve [−η, η]) yoksa [0, q) mı
  bayt            paketleme/açma bayt dönüşümüyle mi (l, 8'in katı olmalı) yoksa döngüyle mi
  negasiklik_mod  X^n + 1 indirgemesi tamsayıda mı yapılıyor: X = 2^l → mod 2^(n·l) + 1
  modul_toplami   iç çarpımın terimleri açmadan önce tamsayı olarak toplanıyor mu (Sonuç 1)
"""

from dataclasses import dataclass
from functools import cache

from pqc.parametreler import N, Parametre, Q
from pqc.teori import A, l_min_isaretli, l_min_isaretsiz


def merkezle(x: int) -> int:
    """[0, q) → [−1664, 1664]."""
    return x - Q if x > Q // 2 else x


@cache
def _birler(l: int, adet: int) -> int:
    """Σ_{k<adet} 2^(k·l): her dilimde 1 olan tamsayı (tüm katsayıları 1 olan polinomun paketi)."""
    return ((1 << (l * adet)) - 1) // ((1 << l) - 1)


# --- paketleme ---


def paketle_dongu(f: list[int], l: int) -> int:
    """Horner yöntemi: Σ f_i·2^(i·l). Negatif katsayılarla da doğru çalışır."""
    x = 0
    for c in reversed(f):
        x = (x << l) + c
    return x


def paketle_bayt(f: list[int], l: int, sapma: int) -> int:
    """Katsayılara `sapma` eklenip negatif olmayan l bitlik dilimler bayt olarak yazılır, sonra
    paket doğrusal olduğundan sapma geri çıkarılır: paket(f) = paket(f + sapma) − sapma·paket(1)."""
    genislik = l // 8
    ham = b"".join((c + sapma).to_bytes(genislik, "little") for c in f)
    return int.from_bytes(ham, "little") - sapma * _birler(l, len(f))


# --- açma ---


def ac_dongu_isaretli(C: int, l: int, adet: int) -> list[int]:
    """Lemma 1'in ispatındaki algoritma: dilim ≥ 2^(l−1) ise negatif say, çıkar, kaydır."""
    maske = (1 << l) - 1
    yarim = 1 << (l - 1)
    c = []
    for _ in range(adet):
        d = C & maske
        if d >= yarim:
            d -= 1 << l
        c.append(d)
        C = (C - d) >> l
    return c


def ac_dongu_isaretsiz(C: int, l: int, adet: int) -> list[int]:
    maske = (1 << l) - 1
    return [(C >> (l * k)) & maske for k in range(adet)]


def ac_bayt(C: int, l: int, adet: int, isaretli: bool) -> list[int]:
    """İşaretli dilimler [−2^(l−1), 2^(l−1)) aralığındaysa C'ye her dilimde 2^(l−1) eklenince tüm
    dilimler negatif olmayan olur ve dilimler arası borç oluşmaz; sonra baytlardan okunup geri çıkarılır."""
    sapma = (1 << (l - 1)) if isaretli else 0
    genislik = l // 8
    ham = (C + sapma * _birler(l, adet)).to_bytes(genislik * adet, "little")
    return [int.from_bytes(ham[i : i + genislik], "little") - sapma for i in range(0, len(ham), genislik)]


@dataclass(frozen=True)
class Varyant:
    ad: str
    l: int
    isaretli: bool
    bayt: bool = False
    negasiklik_mod: bool = False
    modul_toplami: bool = False

    def __post_init__(self):
        if self.bayt and self.l % 8:
            raise ValueError(f"{self.ad}: bayt yöntemi için l 8'in katı olmalı")
        if self.negasiklik_mod and not self.isaretli:
            # mod 2^(nl)+1 sonucu c_k − c_{k+n} farklarıdır; işaretsiz girdide bile negatif olabilir.
            raise ValueError(f"{self.ad}: negasiklik_mod işaretli katsayı gerektirir")

    def gerekli_l(self, p: Parametre) -> int:
        """Teorem 1 / Sonuç 1: bu varyantın p için doğru olması gereken en küçük l."""
        terim = p.k if self.modul_toplami else 1
        if self.isaretli:
            return l_min_isaretli(N, A, p.eta1, terim)
        return l_min_isaretsiz(N, Q - 1, Q - 1, terim)

    def guvenli_mi(self, p: Parametre) -> bool:
        return self.l >= self.gerekli_l(p)

    def _paketle(self, f: list[int]) -> int:
        if self.bayt:
            return paketle_bayt(f, self.l, (1 << (self.l - 1)) - 1 if self.isaretli else 0)
        return paketle_dongu(f, self.l)

    def _ac(self, C: int, adet: int) -> list[int]:
        if self.bayt:
            return ac_bayt(C, self.l, adet, self.isaretli)
        if self.isaretli:
            return ac_dongu_isaretli(C, self.l, adet)
        return ac_dongu_isaretsiz(C, self.l, adet)

    def _coz(self, C: int) -> list[int]:
        """Çarpım tamsayısı → R_q'daki polinom (katsayılar mod q)."""
        if self.negasiklik_mod:
            M = (1 << (N * self.l)) + 1
            C %= M
            if C > M // 2:
                C -= M
            return [x % Q for x in self._ac(C, N)]
        c = self._ac(C, 2 * N - 1)
        c.append(0)
        return [(c[i] - c[i + N]) % Q for i in range(N)]  # X^n = −1

    def ic_carpim(self, buyuk: list[list[int]], kucuk: list[list[int]], eta: int) -> list[int]:
        """Σ_j buyuk[j]·kucuk[j] ∈ R_q. Girdiler mod q; kucuk'un katsayıları [−eta, eta] aralığında olmalı.

        l'nin yeterli olup olmadığını kontrol ETMEZ (Aşama 4 deneyleri bilerek dar l kullanır);
        güvenli kullanım için `guvenli_mi` / KroneckerPKE.
        """
        if self.isaretli:
            buyuk = [[merkezle(x) for x in f] for f in buyuk]
            kucuk = [[merkezle(x) for x in f] for f in kucuk]
            if any(abs(x) > eta for f in kucuk for x in f):
                raise ValueError("küçük polinomun katsayısı [−η, η] dışında")
        M = (1 << (N * self.l)) + 1 if self.negasiklik_mod else None
        sonuc = [0] * N
        birikim = 0
        for b, s in zip(buyuk, kucuk):
            urun = self._paketle(b) * self._paketle(s)
            if M is not None:
                urun %= M
            if self.modul_toplami:
                birikim += urun
            else:
                sonuc = [(x + y) % Q for x, y in zip(sonuc, self._coz(urun))]
        if self.modul_toplami:
            sonuc = self._coz(birikim)
        return sonuc


VARYANTLAR = [
    Varyant("isaretsiz32-dongu", l=32, isaretli=False),
    Varyant("isaretsiz32-bayt", l=32, isaretli=False, bayt=True),
    Varyant("isaretli22-dongu", l=22, isaretli=True),
    Varyant("isaretli24-bayt", l=24, isaretli=True, bayt=True),
    Varyant("isaretli22-negmod", l=22, isaretli=True, negasiklik_mod=True),
    Varyant("isaretli24-bayt-negmod", l=24, isaretli=True, bayt=True, negasiklik_mod=True),
    Varyant("isaretli24-bayt-modul", l=24, isaretli=True, bayt=True, modul_toplami=True),
    Varyant(
        "isaretli24-bayt-negmod-modul",
        l=24,
        isaretli=True,
        bayt=True,
        negasiklik_mod=True,
        modul_toplami=True,
    ),
]
VARYANT = {v.ad: v for v in VARYANTLAR}

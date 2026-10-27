"""FIPS 203, Bölüm 6–7: ML-KEM anahtar üretimi, kapsülleme ve kapsül açma."""

import secrets

from pqc import kpke
from pqc.kodlama import byte_decode, byte_encode
from pqc.ozetler import G, H, J
from pqc.parametreler import Parametre


def keygen_internal(d: bytes, z: bytes, p: Parametre) -> tuple[bytes, bytes]:
    """Algoritma 16: (ek, dk). dk = dk_PKE ‖ ek ‖ H(ek) ‖ z."""
    ek, dk_pke = kpke.keygen(d, p)
    dk = dk_pke + ek + H(ek) + z
    return ek, dk


def encaps_internal(ek: bytes, m: bytes, p: Parametre) -> tuple[bytes, bytes]:
    """Algoritma 17: (K, c)."""
    K, r = G(m + H(ek))
    c = kpke.encrypt(ek, m, r, p)
    return K, c


def decaps_internal(dk: bytes, c: bytes, p: Parametre) -> bytes:
    """Algoritma 18. Şifreli metin tutarsızsa sahte anahtar K̄ = J(z‖c) döner (örtük reddetme)."""
    k = p.k
    dk_pke = dk[: 384 * k]
    ek_pke = dk[384 * k : 768 * k + 32]
    h = dk[768 * k + 32 : 768 * k + 64]
    z = dk[768 * k + 64 : 768 * k + 96]
    m_ = kpke.decrypt(dk_pke, c, p)
    K_, r_ = G(m_ + h)
    K_sahte = J(z + c)
    c_ = kpke.encrypt(ek_pke, m_, r_, p)
    if c != c_:
        K_ = K_sahte
    return K_


def ek_gecerli(ek: bytes, p: Parametre) -> bool:
    """Bölüm 7.2 girdi kontrolü: uzunluk ve modül (her katsayı < q) kontrolü."""
    if len(ek) != p.ek_uzunluk:
        return False
    for i in range(p.k):
        parca = ek[384 * i : 384 * (i + 1)]
        if byte_encode(byte_decode(parca, 12), 12) != parca:
            return False
    return True


def dk_gecerli(dk: bytes, p: Parametre) -> bool:
    """Bölüm 7.3 girdi kontrolü: uzunluk ve H(ek) özet kontrolü."""
    k = p.k
    if len(dk) != p.dk_uzunluk:
        return False
    return H(dk[384 * k : 768 * k + 32]) == dk[768 * k + 32 : 768 * k + 64]


def keygen(p: Parametre) -> tuple[bytes, bytes]:
    """Algoritma 19."""
    return keygen_internal(secrets.token_bytes(32), secrets.token_bytes(32), p)


def encaps(ek: bytes, p: Parametre) -> tuple[bytes, bytes]:
    """Algoritma 20. Geçersiz ek için ValueError."""
    if not ek_gecerli(ek, p):
        raise ValueError("geçersiz kapsülleme anahtarı")
    return encaps_internal(ek, secrets.token_bytes(32), p)


def decaps(dk: bytes, c: bytes, p: Parametre) -> bytes:
    """Algoritma 21. Geçersiz dk veya yanlış uzunlukta c için ValueError."""
    if len(c) != p.c_uzunluk or not dk_gecerli(dk, p):
        raise ValueError("geçersiz kapsül açma girdisi")
    return decaps_internal(dk, c, p)

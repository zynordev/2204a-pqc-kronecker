"""FIPS 203, Bölüm 4.1: özet (hash) ve sözde rastgele fonksiyonlar."""

import hashlib


def H(s: bytes) -> bytes:
    """H(s) = SHA3-256(s), 32 bayt."""
    return hashlib.sha3_256(s).digest()


def J(s: bytes) -> bytes:
    """J(s) = SHAKE256(s, 8·32), 32 bayt."""
    return hashlib.shake_256(s).digest(32)


def G(c: bytes) -> tuple[bytes, bytes]:
    """G(c) = SHA3-512(c), iki adet 32 baytlık parçaya bölünür."""
    h = hashlib.sha3_512(c).digest()
    return h[:32], h[32:]


def PRF(eta: int, s: bytes, b: int) -> bytes:
    """PRF_η(s, b) = SHAKE256(s‖b, 8·64·η), 64·η bayt. b tek bayttır."""
    return hashlib.shake_256(s + bytes([b])).digest(64 * eta)

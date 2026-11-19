"""Rapor §3.2 ve §3.6 örnekleri: bir okul metninin şifrelenmesi ve çözülmesi.

Bölüm 1 — Oyuncak örnek (elle izlenebilir küçük sayılar):
    ML-KEM'in fikri n = 8 katsayılı, q = 97 modlu polinomlarla tek bir harf (8 bit) üzerinde
    gösterilir. Bütün polinom çarpımları Kronecker ikamesiyle, okunması kolay olsun diye
    x = 1000 tabanında yapılır ve okul yöntemiyle karşılaştırılır.

Bölüm 2 — Gerçek akış (PQC-Drop ile aynı):
    ML-KEM-768 (projenin kendi kodu, 24 bitlik Kronecker motoru) ile 32 baytlık ortak sır kurulur,
    HKDF-SHA256 ile AES-256 anahtarı türetilir, metin AES-256-GCM ile şifrelenip çözülür.

Çalıştırma (depo kökünden):
    .venv/bin/python docs/ornekler/okul_metni_sifreleme.py
"""

import random

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from pqc import mlkem
from pqc.kpke_kronecker import KroneckerPKE
from pqc.kronecker import VARYANT
from pqc.parametreler import ML_KEM_768
from pqc.pqcdrop import anahtar_turet, nonce_uret

# ---------------------------------------------------------------- Bölüm 1: oyuncak örnek

N_OY = 8  # katsayı sayısı (ML-KEM'de 256)
Q_OY = 97  # modül (ML-KEM'de 3329)
YARIM = 49  # "1" biti için eklenen değer ≈ q/2 (ML-KEM'de 1665)
TABAN = 1000  # Kronecker tabanı; okunabilirlik için 10'un kuvveti seçildi


def merkez(x: int, q: int = Q_OY) -> int:
    """x mod q değerini −q/2 … q/2 aralığına taşır (merkezlenmiş gösterim)."""
    x %= q
    return x - q if x > q // 2 else x


def okul_carpimi(a: list[int], b: list[int]) -> list[int]:
    """Okul yöntemi: her katsayı ikilisini çarp, x^8 = −1 kuralıyla katla, mod q al."""
    d = [0] * N_OY
    for i in range(N_OY):
        for j in range(N_OY):
            k = i + j
            if k < N_OY:
                d[k] += a[i] * b[j]
            else:
                d[k - N_OY] -= a[i] * b[j]  # x^8 = −1
    return [merkez(x) for x in d]


def paketle(f: list[int]) -> int:
    """Kronecker: polinomda x yerine 1000 koy → tek bir tamsayı."""
    return sum(c * TABAN**i for i, c in enumerate(f))


def ac(C: int, adet: int) -> list[int]:
    """Dengeli açma (Lemma 1): her adımda son üç basamağı al, 500 ve üstüyse 1000 çıkar."""
    rakamlar = []
    for _ in range(adet):
        r = C % TABAN
        if r >= TABAN // 2:
            r -= TABAN
        rakamlar.append(r)
        C = (C - r) // TABAN
    assert C == 0, "taban yetersiz: katsayılar karıştı"
    return rakamlar


def kronecker_carpimi(a: list[int], b: list[int], ayrinti: bool = False) -> list[int]:
    Pa, Pb = paketle(a), paketle(b)
    C = Pa * Pb
    c = ac(C, 2 * N_OY - 1) + [0]
    d = [merkez(c[i] - c[i + N_OY]) for i in range(N_OY)]  # x^8 = −1
    if ayrinti:
        print(f"    P_a = {Pa:,}".replace(",", "."))
        print(f"    P_s = {Pb:,}".replace(",", "."))
        print(f"    P_a · P_s = {C:,}".replace(",", "."))
        print(f"    açılan 15 katsayı (c_0 … c_14) = {c[:-1]}")
        print(f"    x^8 = −1 ile katlanmış ve mod 97 = {d}")
    return d


def carp(a, b, ayrinti=False):
    d = kronecker_carpimi(a, b, ayrinti)
    assert d == okul_carpimi(a, b), "Kronecker ile okul yöntemi farklı çıktı"
    return d


def topla(*polinomlar):
    return [merkez(sum(t)) for t in zip(*polinomlar)]


def kucuk(rng) -> list[int]:
    return [rng.choice((-1, 0, 0, 1)) for _ in range(N_OY)]


def oyuncak_ornek(harf: str = "O", tohum: int = 2204) -> None:
    rng = random.Random(tohum)
    print("=" * 72)
    print(f"BÖLÜM 1 — Oyuncak örnek: '{harf}' harfi (n = {N_OY}, q = {Q_OY})")
    print("=" * 72)

    bitler = [int(b) for b in format(ord(harf), "08b")][::-1]  # en düşük bit 0. katsayı
    print(f"'{harf}' = ASCII {ord(harf)} = {format(ord(harf), '08b')} (ikilik)")
    print(f"mesaj polinomu m (katsayı = bit, düşük bitten başlayarak): {bitler}")

    # Anahtar üretimi (alıcı)
    a = [merkez(rng.randrange(Q_OY)) for _ in range(N_OY)]
    s, e = kucuk(rng), kucuk(rng)
    print("\n[1] ALICI anahtar üretir")
    print(f"    a (herkese açık, rastgele, −48…48) = {a}")
    print(f"    s (GİZLİ, küçük, −1…1)              = {s}")
    print(f"    e (gizli gürültü, −1…1)             = {e}")
    print("    a · s hesabı (Kronecker, x = 1000):")
    as_ = carp(a, s, ayrinti=True)
    b = topla(as_, e)
    print(f"    b = a·s + e (herkese açık)          = {b}")

    # Şifreleme (gönderici)
    r, e1, e2 = kucuk(rng), kucuk(rng), kucuk(rng)
    mesaj = [YARIM * x for x in bitler]
    u = topla(carp(a, r), e1)
    v = topla(carp(b, r), e2, mesaj)
    print("\n[2] GÖNDERİCİ şifreler (r, e1, e2 her seferinde yeni ve küçük)")
    print(f"    r = {r}, e1 = {e1}, e2 = {e2}")
    print(f"    mesaj · 49                           = {mesaj}")
    print(f"    u = a·r + e1                         = {u}")
    print(f"    v = b·r + e2 + 49·m                  = {v}")
    print("    gönderilen şifreli metin: (u, v)")

    # Çözme (alıcı)
    su = carp(s, u)
    w = topla(v, [-x for x in su])
    cozulen = [1 if abs(x) > Q_OY // 4 else 0 for x in w]
    harf_geri = chr(int("".join(map(str, cozulen[::-1])), 2))
    print("\n[3] ALICI çözer: w = v − s·u")
    print(f"    w                                    = {w}")
    print("    kural: |w_i| > 24 ise bit 1, değilse 0 (0 ile 49'dan hangisine yakın?)")
    print(f"    çözülen bitler = {cozulen}  →  '{harf_geri}'")
    gurultu = [merkez(wi - mi) for wi, mi in zip(w, mesaj)]
    print(f"    kalan gürültü (w − 49·m)             = {gurultu}, en büyük |.| = {max(map(abs, gurultu))}")
    assert harf_geri == harf
    # Kronecker tabanı yeterli mi? |a_i| ≤ 48, |s_j| ≤ 1, 8 terim → |c_k| ≤ 384 < 500
    print(f"    taban kontrolü: en kötü durumda |c_k| ≤ 8·48·1 = {8 * 48} < 500 → x = 1000 yeterli")


# ---------------------------------------------------------------- Bölüm 2: gerçek akış


def gercek_ornek(metin: str) -> None:
    print("\n" + "=" * 72)
    print("BÖLÜM 2 — Gerçek akış: ML-KEM-768 (24 bit Kronecker) + AES-256-GCM")
    print("=" * 72)
    pke = KroneckerPKE(VARYANT["isaretli24-bayt-negmod"])  # PQC-Drop'un varsayılan motoru
    p = ML_KEM_768
    veri = metin.encode("utf-8")

    ek, dk = mlkem.keygen(p, pke=pke)  # alıcı
    K_gonderici, c = mlkem.encaps(ek, p, pke=pke)  # gönderici
    K_alici = mlkem.decaps(dk, c, p, pke=pke)  # alıcı
    assert K_gonderici == K_alici

    anahtar = anahtar_turet(K_gonderici)
    sifreli = AESGCM(anahtar).encrypt(nonce_uret(0), veri, None)
    cozulen = AESGCM(anahtar_turet(K_alici)).decrypt(nonce_uret(0), sifreli, None).decode("utf-8")

    print(f"Metin ({len(veri)} bayt): {metin}")
    print(f"[1] Alıcının açık anahtarı ek : {len(ek)} bayt  (ilk 16: {ek[:16].hex()})")
    print(f"    Alıcının gizli anahtarı dk: {len(dk)} bayt  (gönderilmez)")
    print(f"[2] Göndericinin kapsülü c    : {len(c)} bayt  (ilk 16: {c[:16].hex()})")
    print(f"    Ortak sır K (iki tarafta aynı): {len(K_gonderici)} bayt, eşit mi: {K_gonderici == K_alici}")
    print(f"[3] Şifreli metin             : {len(sifreli)} bayt = {len(veri)} metin + 16 doğrulama etiketi")
    print(f"    ilk 32 bayt (hex)         : {sifreli[:32].hex()}")
    print(f"[4] Çözülen metin             : {cozulen}")
    print(f"    Asıl metinle aynı mı      : {cozulen == metin}")

    # Tek bayt bozulursa ne olur?
    bozuk = bytearray(sifreli)
    bozuk[0] ^= 1
    try:
        AESGCM(anahtar).decrypt(nonce_uret(0), bytes(bozuk), None)
        print("[5] Tek bit bozulmuş şifreli metin: (beklenmedik biçimde) kabul edildi")
    except InvalidTag:
        print("[5] Tek bit bozulmuş şifreli metin: reddedildi (InvalidTag)")


# ---------------------------------------------------------------- Bölüm 3: tek bir "deneme"


def tek_deneme(tohum: int = 20261030, eta: int = 3) -> None:
    """Deneylerdeki bir rastgele denemenin ne olduğunu gerçek boyutlarla gösterir."""
    print("\n" + "=" * 72)
    print(f"BÖLÜM 3 — Tek bir deneme (n = 256, q = 3329, η = {eta})")
    print("=" * 72)
    rng = random.Random(tohum)
    n, q = 256, 3329
    a = [merkez(rng.randrange(q), q) for _ in range(n)]  # düzgün dağılım, merkezlenmiş
    # Merkezli binom dağılımı: η yazı-tura "tura" sayısı − η yazı-tura "tura" sayısı
    s = [
        sum(rng.getrandbits(1) for _ in range(eta)) - sum(rng.getrandbits(1) for _ in range(eta))
        for _ in range(n)
    ]
    c = [0] * (2 * n - 1)
    carpma = 0
    for i in range(n):
        for j in range(n):
            c[i + j] += a[i] * s[j]
            carpma += 1
    en_buyuk = max(abs(x) for x in c)
    sinir = n * 1664 * eta
    print(f"a'nın ilk 8 katsayısı: {a[:8]}")
    print(
        f"s'nin ilk 8 katsayısı: {s[:8]}  (değer sayıları: "
        + ", ".join(f"{v}:{s.count(v)}" for v in range(-eta, eta + 1))
        + ")"
    )
    print(f"okul yöntemiyle yapılan çarpma sayısı: {carpma:,}".replace(",", "."))
    print(
        f"bu denemede en büyük |c_k|: {en_buyuk:,} → {en_buyuk.bit_length() + 1} bit yeterdi".replace(
            ",", "."
        )
    )
    print(f"en kötü durum sınırı n·A·η = {sinir:,} → {sinir.bit_length() + 1} bit gerekir".replace(",", "."))


if __name__ == "__main__":
    oyuncak_ornek("O")
    gercek_ornek("Okulumuzun bilim şenliği 20 Aralık'ta konferans salonunda yapılacaktır.")
    tek_deneme()

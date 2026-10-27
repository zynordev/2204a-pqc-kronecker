"""Testlerin hata yakalama gücü: koda bilerek hata koyar, testlerin bunu yakaladığını doğrular.

Her mutasyon tek tek uygulanır, ilgili testler çalıştırılır, dosya her durumda eski haline döner.
Kullanım: python araclar/mutasyon_kontrolu.py   (repo kökünden)
"""

import pathlib
import resource
import subprocess
import sys

KOK = pathlib.Path(__file__).resolve().parents[1]
ZAMAN_ASIMI = 120  # saniye; normal tam test ~5 sn
# Bir mutasyon sonsuz döngüde belleği büyütürse makineyi çökertmesin (2026-10-27'de Pi böyle çöktü).
BELLEK_SINIRI = 512 * 1024 * 1024  # bayt


def _bellegi_sinirla() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (BELLEK_SINIRI, BELLEK_SINIRI))

# (dosya, doğru kod, hatalı kod, açıklama)
MUTASYONLAR = [
    ("src/pqc/kpke.py", "G(d + bytes([k]))", "G(d)", "FIPS 203 son sürümündeki k alan ayrımı unutuldu"),
    ("src/pqc/kpke.py", "bytes([j, i])", "bytes([i, j])", "Â matrisinin indeks sırası ters"),
    ("src/pqc/kodlama.py", "(2 * (x << d) + Q)", "(2 * (x << d))", "Compress yuvarlama yerine kesiyor"),
    ("src/pqc/mlkem.py", "K_ = K_sahte", "pass", "örtük reddetme yok"),
    ("src/pqc/ntt.py", "x * 3303 % Q", "x * 3302 % Q", "NTT⁻¹ sonundaki 128⁻¹ sabiti yanlış"),
    ("src/pqc/ntt.py", "pow(ZETA, 2 * bitrev7(i) + 1, Q)", "pow(ZETA, 2 * bitrev7(i), Q)", "γ üssü yanlış"),
    ("src/pqc/ornekleme.py", "C[p] + 256 * (C[p + 1] % 16)", "C[p] + 256 * (C[p + 1] % 15)", "SampleNTT 12 bitlik sayıyı yanlış okuyor"),
    (
        "src/pqc/mlkem.py",
        "return H(dk[384 * k : 768 * k + 32]) == dk[768 * k + 32 : 768 * k + 64]",
        "return True",
        "dk özet kontrolü yok",
    ),
    ("src/pqc/kronecker.py", "(c[i] - c[i + N]) % Q", "(c[i] + c[i + N]) % Q", "Kronecker: X^n = −1 yerine +1"),
    ("src/pqc/kronecker.py", "sapma = (1 << (l - 1)) if isaretli else 0", "sapma = 0",
     "Kronecker: bayt açmada işaret sapması unutuldu"),
    ("src/pqc/teori.py", "return terim * n * a_max * b_max", "return n * a_max * b_max",
     "Teori: modül toplamında sınır k ile çarpılmıyor"),
]


def main() -> int:
    yakalanmayan = 0
    for dosya, dogru, hatali, aciklama in MUTASYONLAR:
        yol = KOK / dosya
        orijinal = yol.read_text()
        if orijinal.count(dogru) != 1:
            print(f"HATA: '{dogru}' {dosya} içinde tam bir kez geçmiyor")
            return 2
        try:
            yol.write_text(orijinal.replace(dogru, hatali))
            sonuc = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider"],
                check=False, preexec_fn=_bellegi_sinirla, cwd=KOK, capture_output=True, text=True, timeout=ZAMAN_ASIMI,
            )
            durum = "YAKALANDI " if sonuc.returncode != 0 else "KAÇTI     "
        except subprocess.TimeoutExpired:
            # Takılma bir yakalama sayılmaz: testin net bir hata vermesi gerekir.
            durum = "ZAMAN AŞIMI"
        finally:
            yol.write_text(orijinal)
        yakalanmayan += not durum.startswith("YAKALANDI")
        print(f"{durum} {dosya}: {aciklama}", flush=True)
    print(f"\n{len(MUTASYONLAR) - yakalanmayan}/{len(MUTASYONLAR)} mutasyon yakalandı")
    return 1 if yakalanmayan else 0


if __name__ == "__main__":
    sys.exit(main())

"""Çıkış gözlemimiz: sayının karesini binom katsayıları + sağdan sola elde ile hesaplamak (docs/04-teori.md §0).

23 → (2x + 3)² = 4x² + 12x + 9 → elde ile 529. Kronecker ikamesi aynı fikrin ters yönüdür:
`kronecker.paketle_dongu` = `polinom_degeri` (taban 2^l), `kronecker.ac_dongu_isaretli` = elde/ödünç olmadan
okumanın işaretli hali (Lemma 1). Fark: Kronecker'de taban, elde hiç doğmayacak kadar büyük seçilir.
"""


def rakamlar(sayi: int, taban: int = 10) -> list[int]:
    """Negatif olmayan sayının basamakları, birler basamağı önce: 23 → [3, 2]."""
    if sayi < 0:
        raise ValueError("negatif olmayan sayı bekleniyor")
    b = []
    while True:
        sayi, r = divmod(sayi, taban)
        b.append(r)
        if sayi == 0:
            return b


def polinom_degeri(katsayilar: list[int], taban: int = 10) -> int:
    """Σ c_i·taban^i (x yerine taban koymak). Katsayılar birler önce."""
    deger = 0
    for c in reversed(katsayilar):
        deger = deger * taban + c
    return deger


def kare_katsayilari(sayi: int, taban: int = 10) -> list[int]:
    """Sayının basamak polinomunun karesi (elde uygulanmadan): 23 → [9, 12, 4] yani 4x² + 12x + 9."""
    r = rakamlar(sayi, taban)
    c = [0] * (2 * len(r) - 1)
    for i, ri in enumerate(r):
        for j, rj in enumerate(r):
            c[i + j] += ri * rj
    return c


def elde_ile_normalize(katsayilar: list[int], taban: int = 10) -> tuple[list[int], list[int]]:
    """Sağdan sola elde: her adımda basamak = (katsayı + elde) mod taban, yeni elde = bölüm.

    Negatif katsayıda bölüm negatif olur: bu ödünçtür (19² örneği). Dönen değerler:
    (basamaklar, her adımdan sonraki elde), ikisi de birler önce.
    """
    if polinom_degeri(katsayilar, taban) < 0:
        raise ValueError("toplam değer negatif; basamaklara ayrılamaz")
    basamaklar, eldeler = [], []
    elde = 0
    for c in katsayilar:
        elde, basamak = divmod(c + elde, taban)
        basamaklar.append(basamak)
        eldeler.append(elde)
    while elde:
        elde, basamak = divmod(elde, taban)
        basamaklar.append(basamak)
        eldeler.append(elde)
    return basamaklar, eldeler


def eldesiz_mi(katsayilar: list[int], taban: int) -> bool:
    """Katsayılar doğrudan basamak olarak okunabiliyor mu (hiç elde doğmuyor mu)?"""
    return all(0 <= c < taban for c in katsayilar)


def eldesiz_taban_siniri(basamak: int, taban: int = 10) -> int:
    """`basamak` basamaklı sayıların karesinde en büyük katsayı: basamak·(taban−1)².

    Teorem 1'in taban-10 karşılığı (n·A·η ↔ d·9·9). Değerlendirme tabanı bundan büyükse elde hiç doğmaz.
    """
    return basamak * (taban - 1) ** 2

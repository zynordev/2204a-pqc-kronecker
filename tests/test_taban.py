"""Çıkış gözlemi (docs/04-teori.md §0): kare = binom katsayıları + elde."""

import pytest

from pqc.kronecker import ac_dongu_isaretli, paketle_dongu
from pqc.taban import (
    elde_ile_normalize,
    eldesiz_mi,
    eldesiz_taban_siniri,
    kare_katsayilari,
    polinom_degeri,
    rakamlar,
)


def test_23_kare_adim_adim():
    c = kare_katsayilari(23)
    assert c == [9, 12, 4]  # 4x² + 12x + 9
    basamaklar, eldeler = elde_ile_normalize(c)
    assert eldeler == [0, 1, 0]  # 9 → elde yok; 12 → 2, elde 1; 4 + 1 = 5
    assert basamaklar == [9, 2, 5]
    assert polinom_degeri(basamaklar) == 529


def test_34_kare_adim_adim():
    c = kare_katsayilari(34)
    assert c == [16, 24, 9]  # 9x² + 24x + 16
    basamaklar, eldeler = elde_ile_normalize(c)
    assert eldeler == [1, 2, 1, 0]  # 16 → 6, elde 1; 25 → 5, elde 2; 11 → 1, elde 1; 1
    assert basamaklar == [6, 5, 1, 1]
    assert polinom_degeri(basamaklar) == 1156


@pytest.mark.parametrize("sayi", range(10, 100))
def test_iki_basamakli_tum_sayilar(sayi):
    basamaklar, _ = elde_ile_normalize(kare_katsayilari(sayi))
    assert basamaklar == rakamlar(sayi**2)


def test_taban_100_de_elde_yok_ama_her_sayiya_yetmez():
    c = kare_katsayilari(23)
    assert eldesiz_mi(c, 100)
    assert polinom_degeri(c, 100) == 41209
    assert rakamlar(41209, 100) == c  # 04 | 12 | 09 doğrudan okunur
    assert not eldesiz_mi(kare_katsayilari(99), 100)  # orta katsayı 162 > 99


def test_eldesiz_taban_siniri_keskin():
    """Teorem 1 + Önerme 1'in taban-10 hali: 2 basamakta en büyük katsayı tam 162 (99²'de)."""
    assert eldesiz_taban_siniri(2) == 162
    en_buyuk = max(max(kare_katsayilari(s)) for s in range(10, 100))
    assert en_buyuk == 162
    assert kare_katsayilari(99)[1] == 162
    en_kucuk_taban = en_buyuk + 1
    assert all(eldesiz_mi(kare_katsayilari(s), en_kucuk_taban) for s in range(10, 100))
    assert not all(eldesiz_mi(kare_katsayilari(s), en_kucuk_taban - 1) for s in range(10, 100))


def test_negatif_katsayi_odunc():
    """19 = 2·10 − 1 → (2x − 1)² = 4x² − 4x + 1; −4'te ödünç (elde −1) → 361."""
    c = [1, -4, 4]
    basamaklar, eldeler = elde_ile_normalize(c)
    assert eldeler == [0, -1, 0]
    assert basamaklar == [1, 6, 3]
    assert polinom_degeri(basamaklar) == 19**2


def test_negatif_toplam_reddedilir():
    with pytest.raises(ValueError):
        elde_ile_normalize([-5])


def test_kronecker_ile_baglanti():
    """Taban 2^l'de paketle = polinom_degeri; elde doğmayacak l'de Lemma 1 açması katsayıları geri verir."""
    c = [1, -4, 4]
    assert paketle_dongu(c, 8) == polinom_degeri(c, 2**8)
    assert ac_dongu_isaretli(paketle_dongu(c, 8), 8, 3) == c

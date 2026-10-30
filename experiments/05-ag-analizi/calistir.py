"""Aşama 5b: Ağ Seviyesinde Paket ve Güvenlik Karşılaştırma Deneyi (Açık HTTP vs Klasik HTTPS/TLS vs PQC-Drop).

Bu deney, ağ kablosundan (fiziksel hattan) geçen ham baytları Wireshark paket dökümü
seviyesinde objektif olarak karşılaştırır.

Karşılaştırılan Protokoller:
  1. Düz HTTP (Şifresiz Klasik Protokol)
  2. TLS 1.3 / HTTPS (Klasik Asimetrik ECDHE-X25519 + AES-256-GCM)
  3. PQC-Drop (NIST FIPS 203 ML-KEM-768 Kronecker İkamesi + AES-256-GCM)

Değerlendirme Kriterleri:
  - Shannon Entropisi (Rastlantısallık / Bilgi Gizleme Ölçütü: 0 = düz metin, ~8.0 = saf gürültü)
  - Açık Metin Sızıntısı (Wireshark String Arama: "Hello" / dosya adı tespiti)
  - El Sıkışma / Açık Anahtar Boyutları
  - Kuantum Bilgisayar Tehdidi (Shor Algoritması ve 'Şimdi Kaydet, Sonra Çöz' Riski)
"""

import csv
import math
import os
import pathlib
import time
from collections import Counter

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from pqc import mlkem
from pqc.kpke_kronecker import KroneckerPKE
from pqc.kronecker import VARYANT
from pqc.parametreler import PARAMETRELER


def shannon_entropisi(veri: bytes) -> float:
    """Verinin Shannon entropisini hesaplar (bit / bayt, maks: 8.0)."""
    if not veri:
        return 0.0
    uzunluk = len(veri)
    sayimlar = Counter(veri)
    entropi = 0.0
    for sayi in sayimlar.values():
        p = sayi / uzunluk
        entropi -= p * math.log2(p)
    return entropi


def hexdump_metni(veri: bytes, maks_satir: int = 6) -> str:
    """Wireshark / tcpdump benzeri hexdump ve ASCII çıktısı üretir."""
    satirlar = []
    toplam = len(veri)
    satir_sayisi = min(maks_satir, (toplam + 15) // 16)

    for i in range(satir_sayisi):
        offset = i * 16
        parca = veri[offset : offset + 16]
        hex_str = " ".join(f"{b:02x}" for b in parca)
        hex_str = f"{hex_str:<48}"
        ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in parca)
        satirlar.append(f"{offset:04x}   {hex_str}   |{ascii_str}|")

    if toplam > satir_sayisi * 16:
        kalan = toplam - satir_sayisi * 16
        satirlar.append(f"... ({kalan} bayt daha gizlendi)")
    return "\n".join(satirlar)


def calistir_deney():
    print("=" * 70)
    print("🌐 AĞ PAKET ANALİZİ VE KUANTUM GÜVENLİK KARŞILAŞTIRMASI")
    print("   HTTP (Açık) vs HTTPS (TLS 1.3 Klasik) vs PQC-Drop (Kronecker)")
    print("=" * 70)

    test_icerik = (
        b"Hello World! Bu metin TUBITAK 2204-A Projesi kapsaminda test edilmektedir. "
        b"Kuantum sonrasi kriptografi ile gizlenmektedir."
    )
    aranacak_kelime = b"Hello World"

    sonuclar = []

    # -------------------------------------------------------------
    # 1. Senaryo: Düz HTTP (Şifresiz)
    # -------------------------------------------------------------
    http_istek = (
        f"POST /yukle HTTP/1.1\r\n"
        f"Host: 10.70.175.238:80\r\n"
        f"Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(test_icerik)}\r\n"
        f"\r\n"
    ).encode() + test_icerik

    http_entropi = shannon_entropisi(http_istek)
    http_sizinti = aranacak_kelime in http_istek

    print("\n[1] DÜZ HTTP (Şifresiz):")
    print(f"  Toplam Ağ Yükü: {len(http_istek)} bayt")
    print(f"  Shannon Entropisi: {http_entropi:.3f} / 8.000 bit/bayt")
    print(f"  Wireshark 'Hello World' Araması: {'⚠️ AÇIKÇA BULUNDU!' if http_sizinti else 'Gizli'}")
    print("  --- Kablodan Geçen Paket Dökümü (Hexdump) ---")
    print(hexdump_metni(http_istek, maks_satir=4))

    sonuclar.append({
        "Protokol": "Düz HTTP",
        "Kategori": "Şifresiz Klasik",
        "Paket_Bayt": len(http_istek),
        "Entropi": round(http_entropi, 3),
        "Metin_Sizintisi": "EVET (Açık)",
        "Klasik_Guvenlik": "YOK (Dinlenebilir)",
        "Kuantum_Guvenlik": "YOK (Dinlenebilir)",
        "Shor_Tehdidi": "Uygulanamaz (Şifresiz)",
        "Store_Now_Decrypt_Later": "Anında İfşa",
    })

    # -------------------------------------------------------------
    # 2. Senaryo: Klasik HTTPS / TLS 1.3 (ECDHE-X25519 + AES-256-GCM)
    # -------------------------------------------------------------
    # İstemci & Sunucu X25519 anahtar çifti
    istemci_sk = x25519.X25519PrivateKey.generate()
    raw_enc = serialization.Encoding.Raw
    raw_fmt = serialization.PublicFormat.Raw
    istemci_pk = istemci_sk.public_key().public_bytes(raw_enc, raw_fmt)  # 32 bayt

    sunucu_sk = x25519.X25519PrivateKey.generate()
    sunucu_pk = sunucu_sk.public_key().public_bytes(raw_enc, raw_fmt)  # 32 bayt

    # Ortak sır (ECDH)
    paylasilan_ecdh = istemci_sk.exchange(sunucu_sk.public_key())  # 32 bayt
    aes_tls = AESGCM(paylasilan_ecdh)
    tls_nonce = os.urandom(12)
    tls_sifreli_icerik = aes_tls.encrypt(tls_nonce, test_icerik, None)

    # Ağda akan toplam veri (Açık anahtarlar + TLS başlıkları + şifreli veri)
    tls_ag_verisi = istemci_pk + sunucu_pk + tls_nonce + tls_sifreli_icerik
    tls_entropi = shannon_entropisi(tls_ag_verisi)
    tls_sizinti = aranacak_kelime in tls_ag_verisi

    print("\n[2] YALNIZCA KLASİK ECDHE (X25519 + AES-256-GCM; TLS 1.3 benzeri, TLS kaydı değil):")
    print("  Açık Anahtar Değişimi: 32 bayt (X25519)")
    print(f"  Toplam Ağ Yükü: {len(tls_ag_verisi)} bayt")
    print(f"  Shannon Entropisi: {tls_entropi:.3f} / 8.000 bit/bayt")
    print(f"  Wireshark 'Hello World' Araması: {'Bulundu' if tls_sizinti else '✓ GİZLİ (0 Eşleşme)'}")
    print("  --- Kablodan Geçen Paket Dökümü (Hexdump) ---")
    print(hexdump_metni(tls_ag_verisi, maks_satir=4))
    print("  ⚠️ KUANTUM TEHDİDİ: Aktarılan 32 baytlık X25519 açık anahtarları ağda yakalandığında,")
    print("     yeterli kübite sahip bir kuantum bilgisayar Shor algoritmasıyla ayrık logaritmayı çözer!")

    sonuclar.append({
        "Protokol": "Yalnızca klasik ECDHE (TLS 1.3 benzeri)",
        "Kategori": "Klasik şifreli",
        "Paket_Bayt": len(tls_ag_verisi),
        "Entropi": round(tls_entropi, 3),
        "Metin_Sizintisi": "Hayır",
        "Klasik_Guvenlik": "~128 bit (X25519)",
        "Kuantum_Guvenlik": "Shor ile kırılabilir",
        "Shor_Tehdidi": "Ayrık logaritma polinom zamanda",
        "Store_Now_Decrypt_Later": "Kayıt ileride çözülebilir",
    })

    # -------------------------------------------------------------
    # 3. Senaryo: PQC-Drop (NIST FIPS 203 ML-KEM-768 Kronecker + AES-256-GCM)
    # -------------------------------------------------------------
    p = PARAMETRELER["ML-KEM-768"]
    pke = KroneckerPKE(VARYANT["isaretli24-bayt-negmod"])

    t0 = time.perf_counter()
    ek, _dk = mlkem.keygen(p, pke=pke)
    K, c = mlkem.encaps(ek, p, pke=pke)
    t_pqc_ms = (time.perf_counter() - t0) * 1000

    aes_pqc = AESGCM(K)
    pqc_nonce = os.urandom(12)
    pqc_sifreli_icerik = aes_pqc.encrypt(pqc_nonce, test_icerik, None)

    # Ağda akan toplam veri (1184 bayt ek + 1088 bayt c + 12 bayt nonce + şifreli veri)
    pqc_ag_verisi = ek + c + pqc_nonce + pqc_sifreli_icerik
    pqc_entropi = shannon_entropisi(pqc_ag_verisi)
    pqc_sizinti = aranacak_kelime in pqc_ag_verisi

    print("\n[3] PQC-DROP (NIST FIPS 203 ML-KEM-768 Kronecker + AES-256-GCM):")
    print(f"  Açık Anahtar (ek): {len(ek)} bayt")
    print(f"  Kapsüllenmiş Şifreli Metin (c): {len(c)} bayt")
    print(f"  Toplam Ağ Yükü: {len(pqc_ag_verisi)} bayt")
    print(f"  Shannon Entropisi: {pqc_entropi:.3f} / 8.000 bit/bayt (üst sınır log₂n = {math.log2(len(pqc_ag_verisi)):.2f})")
    print(f"  Wireshark 'Hello World' Araması: {'Bulundu' if pqc_sizinti else '✓ GİZLİ (0 Eşleşme)'}")
    print(f"  Kronecker KEM İşlem Süresi: {t_pqc_ms:.2f} ms")
    print("  --- Kablodan Geçen Paket Dökümü (Hexdump) ---")
    print(hexdump_metni(pqc_ag_verisi, maks_satir=4))
    print("  Kuantum: ML-KEM'in dayandığı M-LWE problemi için bilinen bir kuantum saldırısı yoktur (NIST Kategori 3 hedefi).")

    sonuclar.append({
        "Protokol": "PQC-Drop (Kronecker)",
        "Kategori": "Kuantum sonrası",
        "Paket_Bayt": len(pqc_ag_verisi),
        "Entropi": round(pqc_entropi, 3),
        "Metin_Sizintisi": "Hayır",
        "Klasik_Guvenlik": "NIST Kategori 3 hedefi",
        "Kuantum_Guvenlik": "Bilinen kuantum saldırısı yok (M-LWE)",
        "Shor_Tehdidi": "Uygulanmaz",
        "Store_Now_Decrypt_Later": "Bilinen yöntemle çözülemez",
    })

    # -------------------------------------------------------------
    # Verileri CSV ve Markdown Olarak Kaydetme
    # -------------------------------------------------------------
    dizin = pathlib.Path(__file__).parent
    csv_yolu = dizin / "veri.csv"
    with open(csv_yolu, "w", newline="", encoding="utf-8") as f:
        yazici = csv.DictWriter(f, fieldnames=list(sonuclar[0].keys()))
        yazici.writeheader()
        yazici.writerows(sonuclar)

    md_yolu = dizin / "sonuc.md"
    with open(md_yolu, "w", encoding="utf-8") as f:
        ust = [min(8.0, math.log2(len(v))) for v in (http_istek, tls_ag_verisi, pqc_ag_verisi)]
        f.write("# Deney 05: Ağ Yükü Karşılaştırması (betik içi simülasyon)\n\n")
        f.write("## 1. Deney Amacı ve Yöntem\n")
        f.write(
            "Bu betik **soket açmaz ve paket yakalamaz**; aynı içerik için üç yükü bellekte kurar ve karşılaştırır: "
            "şifresiz HTTP isteği, yalnızca klasik X25519 + AES-256-GCM ile kurulmuş yük (TLS kaydı değil, TLS 1.3 benzeri) "
            "ve PQC-Drop yükü (ek + c + nonce + şifreli içerik). Gerçek ağ kaydı (`tcpdump`/Wireshark) ayrı bir adımdır ve "
            "rapora o girer. Ölçütler: yük boyutu, açık metin araması, Shannon entropisi (yalnızca şifresiz/şifreli ayrımı "
            "için; bkz. §4).\n\n"
        )
        f.write("## 2. Karşılaştırma Tablosu\n\n")
        f.write("| Ölçüt | Düz HTTP | Yalnızca klasik ECDHE (TLS 1.3 benzeri) | PQC-Drop (ML-KEM-768 Kronecker) |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        f.write("| **Anahtar değişimi** | yok | X25519 | FIPS 203 ML-KEM-768 |\n")
        f.write("| **Açık anahtar** | — | 32 bayt | 1184 bayt (+ 1088 bayt kapsül) |\n")
        f.write(f"| **Toplam yük** | {len(http_istek)} bayt | {len(tls_ag_verisi)} bayt | {len(pqc_ag_verisi)} bayt |\n")
        f.write(
            f"| **Shannon entropisi (üst sınır log₂n)** | {http_entropi:.3f} ({ust[0]:.2f}) | "
            f"{tls_entropi:.3f} ({ust[1]:.2f}) | {pqc_entropi:.3f} ({ust[2]:.2f}) |\n"
        )
        f.write("| **Açık metin araması** | bulundu | bulunamadı | bulunamadı |\n")
        f.write("| **Shor algoritmasına karşı** | — | kırılabilir | bilinen kuantum saldırısı yok (NIST Kategori 3 hedefi) |\n\n")

        f.write("## 3. Yük Dökümleri (hexdump)\n\n")
        f.write("### A. Düz HTTP (açık metin)\n```text\n")
        f.write(hexdump_metni(http_istek, maks_satir=6))
        f.write("\n```\n\n")
        f.write("### B. Yalnızca klasik ECDHE + AES-GCM\n```text\n")
        f.write(hexdump_metni(tls_ag_verisi, maks_satir=6))
        f.write("\n```\n\n")
        f.write("### C. PQC-Drop (ek + c + şifreli içerik)\n```text\n")
        f.write(hexdump_metni(pqc_ag_verisi, maks_satir=6))
        f.write("\n```\n\n")

        f.write("## 4. Yorum ve Bilinen Kusurlar\n")
        f.write(
            "- **Boyut bedeli:** Kuantum sonrası anahtar değişiminin maliyeti açık anahtar ve kapsül boyutundadır "
            "(32 bayt yerine 1184 + 1088 bayt).\n"
            "- **Entropi yalnızca şifresiz/şifreli ayrımı için anlamlıdır.** n baytlık örneklemin entropisi en çok log₂n "
            "olabilir; aynı uzunlukta saf rastgele bayt dizisi de aynı değeri verir (214 bayt → ≈ 7,03; 2422 bayt → ≈ 7,92). "
            "İki şifreli yük arasındaki fark paket uzunluğundan gelir, şifreleme kalitesinden değil (ikisi de AES-GCM).\n"
            "- **'TLS 1.3' burada klasik ECDHE'yi temsil eder.** Güncel TLS 1.3 dağıtımları (2024'ten beri büyük tarayıcılar ve "
            "CDN'ler) X25519MLKEM768 hibrit anahtar değişimi kullanır; 'TLS kuantuma açık' genellemesi yapılmamalıdır.\n"
            "- Yalnızca klasik anahtar değişimiyle kaydedilen trafik ileride yeterince büyük bir kuantum bilgisayarla "
            "(Shor) çözülebilir; ML-KEM için bilinen böyle bir saldırı yoktur. 'Sıfır risk' veya 'tam direnç' iddia edilmez.\n"
            "- Bu betik gerçek ağ trafiği içermez; TLS kayıt başlıkları, sertifikalar ve TCP/IP ek yükü hesaba katılmamıştır.\n"
        )

    print(f"\n✓ Veriler kaydedildi: {csv_yolu}")
    print(f"✓ Rapor oluşturuldu: {md_yolu}")


if __name__ == "__main__":
    calistir_deney()

"""PQC-Drop: ML-KEM (Kronecker İkamesi) + AES-256-GCM Kuantum Korumalı Dosya Aktarım Aracı.

Mimari:
  1. KEM (Key Encapsulation): NIST FIPS 203 ML-KEM-768, merkezlenmiş Kronecker motoruyla çalıştırılır.
  2. KDF: 32 baytlık paylaşılan sırdan (K) HKDF-SHA256 ile 256-bit AES anahtarı türetilir.
  3. DEM (Data Encapsulation): Dosya 64 KB'lık parçalar halinde AES-256-GCM ile şifrelenir.
  4. Bütünlük: Her parça GCM etiketiyle anlık doğrulanır, transfer bitiminde tüm dosyanın SHA-256 özeti onaylanır.

Kullanım:
  Alıcı:   python3 -m pqc.pqcdrop alici [--port 8765] [--hedef-dizin .]
  Gönderici: python3 -m pqc.pqcdrop gonder <dosya> <alici_ip> [--port 8765]
"""

import argparse
import hashlib
import json
import pathlib
import socket
import struct
import sys
import time

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from pqc import mlkem
from pqc.kpke_kronecker import KroneckerPKE
from pqc.kronecker import VARYANT
from pqc.parametreler import PARAMETRELER, Parametre

CHUNK_BOYUTU = 64 * 1024  # 64 KB
VARSAYILAN_PORT = 8765
VARSAYILAN_MOTOR = "isaretli24-bayt-negmod"
VARSAYILAN_PARAM = "ML-KEM-768"


def send_bytes(sock: socket.socket, veri: bytes) -> None:
    """4 baytlık uzunluk öneki ile güvenli veri gönderimi."""
    sock.sendall(struct.pack(">I", len(veri)) + veri)


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """Belirtilen bayt miktarı tamamlanana kadar güvenli okuma yapar."""
    parcalar = []
    kalan = n
    while kalan > 0:
        veri = sock.recv(kalan)
        if not veri:
            raise ConnectionError("Bağlantı beklenmedik şekilde kapandı.")
        parcalar.append(veri)
        kalan -= len(veri)
    return b"".join(parcalar)


def recv_bytes(sock: socket.socket) -> bytes:
    """4 baytlık uzunluk önekini okuyup tam veriyi çeker."""
    ham_uzunluk = recv_exact(sock, 4)
    uzunluk = struct.unpack(">I", ham_uzunluk)[0]
    return recv_exact(sock, uzunluk)


def anahtar_turet(paylasilan_sir: bytes) -> bytes:
    """HKDF-SHA256 ile AES-256 anahtarı türetir."""
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"pqc-drop-v1-salt",
        info=b"pqc-drop-aes-256-gcm-key",
    )
    return hkdf.derive(paylasilan_sir)


def nonce_uret(chunk_idx: int) -> bytes:
    """Her chunk için tekil 12 baytlık AES-GCM nonce üretir (8 bayt sayaç + 4 bayt sabit)."""
    return struct.pack(">Q", chunk_idx) + b"PQCD"


# --- El Sıkışma (PQC Handshake) ---


def el_sikis_alici(sock: socket.socket, p: Parametre, motor_adi: str) -> tuple[bytes, float]:
    """Alıcı tarafı: ek üretir -> gönderir -> c alır -> decaps ile K türetir."""
    pke = KroneckerPKE(VARYANT[motor_adi])
    t0 = time.perf_counter()
    ek, dk = mlkem.keygen(p, pke=pke)
    t_keygen = (time.perf_counter() - t0) * 1000

    # 1. ek gönder
    send_bytes(sock, ek)

    # 2. c al
    c = recv_bytes(sock)

    # 3. K decaps
    t0 = time.perf_counter()
    K = mlkem.decaps(dk, c, p, pke=pke)
    t_decaps = (time.perf_counter() - t0) * 1000

    aes_anahtar = anahtar_turet(K)
    return aes_anahtar, t_keygen + t_decaps


def el_sikis_gonderici(sock: socket.socket, p: Parametre, motor_adi: str) -> tuple[bytes, float]:
    """Gönderici tarafı: ek alır -> encaps ile (K, c) üretir -> c gönderir."""
    pke = KroneckerPKE(VARYANT[motor_adi])

    # 1. ek al
    ek = recv_bytes(sock)

    # 2. encaps
    t0 = time.perf_counter()
    K, c = mlkem.encaps(ek, p, pke=pke)
    t_encaps = (time.perf_counter() - t0) * 1000

    # 3. c gönder
    send_bytes(sock, c)

    aes_anahtar = anahtar_turet(K)
    return aes_anahtar, t_encaps


# --- Dosya Gönderici / Alıcı Fonksiyonları ---


def dosya_gonder(
    dosya_yolu: str,
    alici_ip: str,
    port: int = VARSAYILAN_PORT,
    param_adi: str = VARSAYILAN_PARAM,
    motor_adi: str = VARSAYILAN_MOTOR,
) -> None:
    yol = pathlib.Path(dosya_yolu)
    if not yol.is_file():
        print(f"HATA: '{dosya_yolu}' geçerli bir dosya değil.")
        sys.exit(1)

    toplam_bayt = yol.stat().st_size
    p = PARAMETRELER[param_adi]

    print("=" * 60)
    print("🔒 PQC-Drop — Kuantum Korumalı Dosya Gönderici")
    print(f"Dosya: {yol.name} ({toplam_bayt / (1024 * 1024):.2f} MB)")
    print(f"Hedef: {alici_ip}:{port}")
    print(f"Protokol: NIST FIPS 203 ({p.ad}) + Merkezlenmiş Kronecker ({motor_adi})")
    print("=" * 60)

    # Orijinal SHA-256 hesapla
    print("⏳ Dosya SHA-256 bütünlük özeti hesaplanıyor...")
    hasher = hashlib.sha256()
    with open(yol, "rb") as f:
        while blok := f.read(1024 * 1024):
            hasher.update(blok)
    orijinal_ozet = hasher.hexdigest()
    print(f"✓ SHA-256: {orijinal_ozet}")

    # Bağlan
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"🔌 {alici_ip}:{port} adresine bağlanılıyor...")
        sock.connect((alici_ip, port))
        print("✓ TCP bağlantısı kuruldu.")

        # Kuantum El Sıkışma
        print("🤝 Kuantum el sıkışma başlatılıyor (ML-KEM Kronecker)...")
        t0_hs = time.perf_counter()
        aes_anahtar, t_islem = el_sikis_gonderici(sock, p, motor_adi)
        t_toplam_hs = (time.perf_counter() - t0_hs) * 1000
        print(f"✓ Oturum anahtarı kuruldu (KEM işlem: {t_islem:.2f} ms, Ağ dahil: {t_toplam_hs:.2f} ms)")

        aes = AESGCM(aes_anahtar)

        # Metadata gönderimi
        metadata = json.dumps(
            {
                "ad": yol.name,
                "boyut": toplam_bayt,
                "sha256": orijinal_ozet,
                "param": param_adi,
            }
        ).encode("utf-8")

        meta_ct = aes.encrypt(b"METADATA_NC0", metadata, None)
        send_bytes(sock, meta_ct)

        # Şifreli dosya akışı
        print("🚀 Dosya AES-256-GCM ile şifrelenerek aktarılıyor...")
        aktarilan = 0
        chunk_idx = 0
        t0_aktar = time.perf_counter()

        with open(yol, "rb") as f:
            while parca := f.read(CHUNK_BOYUTU):
                nonce = nonce_uret(chunk_idx)
                sifreli_parca = aes.encrypt(nonce, parca, None)
                send_bytes(sock, sifreli_parca)
                aktarilan += len(parca)
                chunk_idx += 1

                # Canlı ilerleme çubuğu
                gecen = time.perf_counter() - t0_aktar
                hiz_mb = (aktarilan / (1024 * 1024)) / (gecen if gecen > 0 else 0.001)
                yuzde = (aktarilan / toplam_bayt) * 100 if toplam_bayt > 0 else 100
                cubuk = "█" * int(yuzde // 5) + "░" * (20 - int(yuzde // 5))
                print(
                    f"\r  [{cubuk}] %{yuzde:.1f} ({aktarilan / (1024 * 1024):.2f}/{toplam_bayt / (1024 * 1024):.2f} MB) {hiz_mb:.2f} MB/s",
                    end="",
                    flush=True,
                )

        print("\n✓ Aktarım tamamlandı! Alıcının bütünlük onayı bekleniyor...")
        onay = recv_bytes(sock).decode("utf-8")
        if onay == "OK":
            print("🎉 BAŞARILI: Alıcı dosyanın SHA-256 özetini ve kimliğini doğruladı!")
        else:
            print(f"❌ HATA: Alıcı aktarımı reddetti: {onay}")

    finally:
        sock.close()


def dosya_al(
    port: int = VARSAYILAN_PORT,
    kayit_dizini: str = ".",
    param_adi: str = VARSAYILAN_PARAM,
    motor_adi: str = VARSAYILAN_MOTOR,
) -> None:
    hedef_klasor = pathlib.Path(kayit_dizini)
    hedef_klasor.mkdir(parents=True, exist_ok=True)
    p = PARAMETRELER[param_adi]

    sunucu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sunucu.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sunucu.bind(("0.0.0.0", port))
    sunucu.listen(1)

    print("=" * 60)
    print("📥 PQC-Drop — Kuantum Korumalı Dosya Alıcı")
    print(f"Dinleniyor: Port {port}")
    print(f"Protokol: NIST FIPS 203 ({p.ad}) + Merkezlenmiş Kronecker ({motor_adi})")
    print(f"Kayıt Dizini: {hedef_klasor.resolve()}")
    print("=" * 60)
    print("⏳ Gönderici bekleniyor... (Çıkış için Ctrl+C)")

    try:
        sock, istemci_addr = sunucu.accept()
        print(f"\n🔌 Bağlantı kabul edildi: {istemci_addr[0]}:{istemci_addr[1]}")

        # Kuantum El Sıkışma
        print("🤝 Kuantum el sıkışma başlatılıyor...")
        t0_hs = time.perf_counter()
        aes_anahtar, t_islem = el_sikis_alici(sock, p, motor_adi)
        t_toplam_hs = (time.perf_counter() - t0_hs) * 1000
        print(f"✓ Oturum anahtarı kuruldu (KEM işlem: {t_islem:.2f} ms, Ağ dahil: {t_toplam_hs:.2f} ms)")

        aes = AESGCM(aes_anahtar)

        # Metadata alımı
        meta_ct = recv_bytes(sock)
        try:
            metadata = json.loads(aes.decrypt(b"METADATA_NC0", meta_ct, None).decode("utf-8"))
        except InvalidTag:
            print("❌ GÜVENLİK İHLALİ: Metadata kimlik doğrulama etiketi geçersiz! Saldırı tespit edildi.")
            sock.close()
            return

        dosya_adi = pathlib.Path(metadata["ad"]).name
        if not dosya_adi or dosya_adi in (".", ".."):
            print("❌ GÜVENLİK İHLALİ: Geçersiz dosya adı tespit edildi.")
            sock.close()
            return
        toplam_bayt = metadata["boyut"]
        beklenen_sha256 = metadata["sha256"]
        cikti_yolu = hedef_klasor / dosya_adi

        print(f"📄 Gelen Dosya: {dosya_adi} ({toplam_bayt / (1024 * 1024):.2f} MB)")
        print(f"📋 Beklenen SHA-256: {beklenen_sha256}")

        # Dosya akışını al ve şifreyi çöz
        print("📥 Veri parçaları alınıyor ve AES-GCM ile çözülüyor...")
        alinan = 0
        chunk_idx = 0
        hasher = hashlib.sha256()
        t0_aktar = time.perf_counter()

        with open(cikti_yolu, "wb") as f_out:
            while alinan < toplam_bayt:
                sifreli_parca = recv_bytes(sock)
                nonce = nonce_uret(chunk_idx)
                try:
                    parca = aes.decrypt(nonce, sifreli_parca, None)
                except InvalidTag:
                    print(f"\n❌ GÜVENLİK İHLALİ: Parça #{chunk_idx} manipüle edilmiş! Paket kurcalandı.")
                    cikti_yolu.unlink(missing_ok=True)
                    send_bytes(sock, b"ERR_TAG_INVALID")
                    sock.close()
                    return

                f_out.write(parca)
                hasher.update(parca)
                alinan += len(parca)
                chunk_idx += 1

                # Canlı ilerleme
                gecen = time.perf_counter() - t0_aktar
                hiz_mb = (alinan / (1024 * 1024)) / (gecen if gecen > 0 else 0.001)
                yuzde = (alinan / toplam_bayt) * 100 if toplam_bayt > 0 else 100
                cubuk = "█" * int(yuzde // 5) + "░" * (20 - int(yuzde // 5))
                print(
                    f"\r  [{cubuk}] %{yuzde:.1f} ({alinan / (1024 * 1024):.2f}/{toplam_bayt / (1024 * 1024):.2f} MB) {hiz_mb:.2f} MB/s",
                    end="",
                    flush=True,
                )

        print("\n🔍 Bütünlük kontrolü yapılıyor...")
        hesaplanan_sha256 = hasher.hexdigest()
        if hesaplanan_sha256 == beklenen_sha256:
            print(f"✓ SHA-256 Doğrulandı: {hesaplanan_sha256}")
            print(f"🎉 Dosya başarıyla kaydedildi: {cikti_yolu.resolve()}")
            send_bytes(sock, b"OK")
        else:
            print("❌ HATA: SHA-256 uyuşmazlığı!")
            cikti_yolu.unlink(missing_ok=True)
            send_bytes(sock, b"ERR_HASH_MISMATCH")

    finally:
        sunucu.close()


def main():
    parser = argparse.ArgumentParser(description="PQC-Drop: Kuantum Korumalı Güvenli Dosya Aktarımı")
    alt = parser.add_subparsers(dest="mod", required=True)

    # Alıcı
    p_alici = alt.add_parser("alici", help="Dosya almak için dinlemeye başla")
    p_alici.add_argument(
        "--port", type=int, default=VARSAYILAN_PORT, help="Dinlenecek port (varsayılan: 8765)"
    )
    p_alici.add_argument("--hedef-dizin", default=".", help="Kaydedilecek dizin (varsayılan: aktif dizin)")
    p_alici.add_argument("--param", default=VARSAYILAN_PARAM, choices=list(PARAMETRELER.keys()))
    p_alici.add_argument("--motor", default=VARSAYILAN_MOTOR, choices=list(VARYANT.keys()))

    # Gönderici
    p_gonder = alt.add_parser("gonder", help="Dosya göndermek için bağlan")
    p_gonder.add_argument("dosya", help="Gönderilecek dosyanın yolu")
    p_gonder.add_argument("ip", help="Alıcının IP adresi")
    p_gonder.add_argument("--port", type=int, default=VARSAYILAN_PORT, help="Alıcı portu (varsayılan: 8765)")
    p_gonder.add_argument("--param", default=VARSAYILAN_PARAM, choices=list(PARAMETRELER.keys()))
    p_gonder.add_argument("--motor", default=VARSAYILAN_MOTOR, choices=list(VARYANT.keys()))

    args = parser.parse_args()

    if args.mod == "alici":
        dosya_al(args.port, args.hedef_dizin, args.param, args.motor)
    elif args.mod == "gonder":
        dosya_gonder(args.dosya, args.ip, args.port, args.param, args.motor)


if __name__ == "__main__":
    main()

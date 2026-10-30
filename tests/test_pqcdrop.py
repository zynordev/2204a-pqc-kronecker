"""PQC-Drop uçtan uca entegrasyon ve güvenlik testleri."""

import os
import socket
import threading

from pqc.parametreler import ML_KEM_768
from pqc.pqcdrop import (
    dosya_al,
    dosya_gonder,
    el_sikis_alici,
    el_sikis_gonderici,
)


def test_pqcdrop_handshake():
    """Alıcı ve gönderici arasında ML-KEM Kronecker el sıkışması ve anahtar eşleşmesi."""
    s_alici = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_alici.bind(("127.0.0.1", 0))
    port = s_alici.getsockname()[1]
    s_alici.listen(1)

    anahtarlar = {}

    def alici_thread():
        conn, _ = s_alici.accept()
        k, _ = el_sikis_alici(conn, ML_KEM_768, "isaretli24-bayt-negmod")
        anahtarlar["alici"] = k
        conn.close()
        s_alici.close()

    t = threading.Thread(target=alici_thread)
    t.start()

    s_gonderici = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_gonderici.connect(("127.0.0.1", port))
    k_gond, _ = el_sikis_gonderici(s_gonderici, ML_KEM_768, "isaretli24-bayt-negmod")
    anahtarlar["gonderici"] = k_gond
    s_gonderici.close()

    t.join()

    assert anahtarlar["alici"] == anahtarlar["gonderici"]
    assert len(anahtarlar["alici"]) == 32


def test_pqcdrop_dosya_aktarimi(tmp_path):
    """Tam dosya aktarımı ve SHA-256 doğrulama testi."""
    gonderilen_dosya = tmp_path / "deneme_veri.bin"
    icerik = os.urandom(256 * 1024)  # 256 KB
    gonderilen_dosya.write_bytes(icerik)

    alici_dizin = tmp_path / "alici_gelen"
    alici_dizin.mkdir()

    port = 9876

    t = threading.Thread(
        target=lambda: dosya_al(port=port, kayit_dizini=str(alici_dizin), param_adi="ML-KEM-512")
    )
    t.daemon = True
    t.start()

    # Sunucunun dinlemeye geçmesini bekle
    import time

    time.sleep(0.2)

    dosya_gonder(str(gonderilen_dosya), "127.0.0.1", port=port, param_adi="ML-KEM-512")
    t.join(timeout=5)

    alınan_dosya = alici_dizin / "deneme_veri.bin"
    assert alınan_dosya.is_file()
    assert alınan_dosya.read_bytes() == icerik

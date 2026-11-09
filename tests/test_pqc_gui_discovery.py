"""PQC-Drop GUI & Keşif Servisi Testleri."""

import os
import socket
import time
from pqc.discovery import DiscoveryService, PeerInfo
from pqc.pqcdrop_engine import hesapla_shannon_entropisi, formatla_hex_dokum


def test_shannon_entropisi():
    # Rastgele şifreli veri (AES-GCM benzeri)
    rastgele_veri = os.urandom(64 * 1024)
    ent_rastgele = hesapla_shannon_entropisi(rastgele_veri)
    assert ent_rastgele >= 7.95, f"Rastgele verinin entropisi yüksek olmalı: {ent_rastgele}"

    # Düz metin veri
    duz_metin = b"Bu cok gizli bir sinav sorusudur. Halil Erdem Yanik TUBITAK 2204-A Projesi." * 100
    ent_duz = hesapla_shannon_entropisi(duz_metin)
    assert ent_duz < 5.5, f"Düz metnin entropisi düşük olmalı: {ent_duz}"


def test_formatla_hex_dokum():
    veri = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
    dokum = formatla_hex_dokum(veri)
    assert "0000" in dokum
    assert "00 01 02 03 04 05 06 07" in dokum
    assert "|.........." in dokum


def test_discovery_service():
    peers_bulundu = []

    def on_update(peers):
        peers_bulundu.append(len(peers))

    d1 = DiscoveryService("Cihaz-A", transfer_port=8765, discovery_port=8799)
    d2 = DiscoveryService("Cihaz-B", transfer_port=8766, discovery_port=8799, on_peers_updated=on_update)

    try:
        d1.start()
        d2.start()

        # Yayın yap
        d1.broadcast_beacon()
        time.sleep(0.3)

        # Görünürlük kapatma testi
        d1.set_visible(False)
        assert d1.visible is False
    finally:
        d1.stop()
        d2.stop()


def test_gui_window_headless():
    from PyQt6.QtWidgets import QApplication
    from pqc.gui import VoiceBoxPQCDropWindow

    # Headless / offscreen test
    app = QApplication.instance()
    if not app:
        app = QApplication(["-platform", "offscreen"])

    win = VoiceBoxPQCDropWindow()
    assert win.windowTitle() != ""
    assert win.tabs.count() == 3

    # Binom simülatörü testi
    win.txt_calc_input.setText("23")
    win._simulate_binom_carry()
    assert "529" in win.lbl_binom_result.text()

    # H4 saldırı simülatörü testi
    win._simulate_h4_attack()
    assert "GÜVENLİK ALARMI" in win.lbl_h4_result.text()

    win.close()


def test_pqcdrop_engine_e2e(tmp_path):
    """SendTask ve ReceiveListener ile uçtan uca dosya aktarımı ve paket yakalama testi."""
    from pqc.pqcdrop_engine import SendTask, ReceiveListener

    gonderilen_dosya = tmp_path / "gizli_metin.txt"
    test_veri = "TUBITAK 2204-A Projesi Kuantum Korumali Dosya Aktarim Testi.".encode("utf-8") * 2000  # ~120 KB
    gonderilen_dosya.write_bytes(test_veri)

    alici_dizin = tmp_path / "alici_klasor"
    alici_dizin.mkdir()

    test_port = 9888
    yakalanan_paketler = []
    aktarim_sonuc = {}

    listener = ReceiveListener(
        port=test_port,
        save_dir=str(alici_dizin),
        on_packet=lambda p: yakalanan_paketler.append(p),
        on_file_received=lambda f, b, h: aktarim_sonuc.update({"dosya": f, "boyut": b, "sha256": h}),
    )
    listener.start()
    time.sleep(0.2)

    gonderildi_flag = []
    sender = SendTask(
        file_path=str(gonderilen_dosya),
        target_ip="127.0.0.1",
        target_port=test_port,
        on_packet=lambda p: yakalanan_paketler.append(p),
        on_finished=lambda s, m, h: gonderildi_flag.append((s, m, h)),
    )
    sender.start()
    sender.join(timeout=8.0)
    time.sleep(0.3)
    listener.stop()

    assert len(gonderildi_flag) == 1
    assert gonderildi_flag[0][0] is True  # Success
    assert len(yakalanan_paketler) >= 4  # PUBKEY, CIPHERTEXT, METADATA, CHUNKS, VERIFY

    # Dosya doğrulaması
    alinan_dosya = alici_dizin / "gizli_metin.txt"
    assert alinan_dosya.is_file()
    assert alinan_dosya.read_bytes() == test_veri
    assert aktarim_sonuc["sha256"] == gonderildi_flag[0][2]


"""PQC-Drop Asenkron Arayüz Motoru & Canlı Şifreleme/Paket Denetleyicisi.

Özellikler:
- Shannon Entropi hesaplayıcı (Şifreli verinin rastgelelik derecesini kanıtlar).
- 16-baytlık Hex/ASCII formatlayıcı (Wireshark benzeri döküm).
- Asenkron alıcı ve gönderici iş parçacıkları (Worker threads).
- Canlı paket dinleme kancası (Packet inspector hooks).
"""

import hashlib
import json
import math
import os
import pathlib
import socket
import struct
import sys
import threading
import time
from typing import Callable, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from pqc.parametreler import PARAMETRELER, Parametre
from pqc.pqcdrop import (
    CHUNK_BOYUTU,
    VARSAYILAN_MOTOR,
    VARSAYILAN_PARAM,
    VARSAYILAN_PORT,
    el_sikis_alici,
    el_sikis_gonderici,
    nonce_uret,
    recv_bytes,
    send_bytes,
)


def hesapla_shannon_entropisi(veri: bytes) -> float:
    """Verilen bayt dizisinin Shannon Entropisini hesaplar (0.000 ile 8.000 arası).
    Şifrelenmiş veri 7.95+ çıkar; düz metin 4.0 - 5.5 civarıdır.
    """
    if not veri:
        return 0.0
    uzunluk = len(veri)
    frekanslar = {}
    for b in veri:
        frekanslar[b] = frekanslar.get(b, 0) + 1

    entropi = 0.0
    for sayi in frekanslar.values():
        p = sayi / uzunluk
        entropi -= p * math.log2(p)
    return round(entropi, 3)


def formatla_hex_dokum(veri: bytes, max_bayt: int = 256) -> str:
    """Veriyi Wireshark tarzı 16 sütunlu Hex + ASCII biçiminde döker."""
    kirpilmis = veri[:max_bayt]
    satirlar = []
    for ofset in range(0, len(kirpilmis), 16):
        blok = kirpilmis[ofset : ofset + 16]
        hex_parcalar = [f"{b:02x}" for b in blok]
        # 8. bayttan sonra çift boşluk
        if len(hex_parcalar) > 8:
            hex_str = " ".join(hex_parcalar[:8]) + "  " + " ".join(hex_parcalar[8:])
        else:
            hex_str = " ".join(hex_parcalar)
        hex_pad = hex_str.ljust(49)

        ascii_parcalar = [chr(b) if 32 <= b <= 126 else "." for b in blok]
        ascii_str = "".join(ascii_parcalar)

        satirlar.append(f"{ofset:04x}  {hex_pad}  |{ascii_str}|")

    if len(veri) > max_bayt:
        satirlar.append(f"... (+{len(veri) - max_bayt} bayt daha)")
    return "\n".join(satirlar)


class PacketEvent:
    def __init__(
        self,
        packet_type: str,
        direction: str,  # "GÖNDERİLDİ" veya "ALINDI"
        size: int,
        raw_bytes: bytes,
        details: str,
    ):
        self.timestamp = time.strftime("%H:%M:%S")
        self.packet_type = packet_type
        self.direction = direction
        self.size = size
        self.raw_bytes = raw_bytes
        self.details = details
        self.entropy = hesapla_shannon_entropisi(raw_bytes)
        self.hex_dump = formatla_hex_dokum(raw_bytes)


class SendTask(threading.Thread):
    def __init__(
        self,
        file_path: str,
        target_ip: str,
        target_port: int = VARSAYILAN_PORT,
        param_name: str = VARSAYILAN_PARAM,
        engine_name: str = VARSAYILAN_MOTOR,
        on_packet: Optional[Callable[[PacketEvent], None]] = None,
        on_progress: Optional[Callable[[int, int, float], None]] = None,
        on_status: Optional[Callable[[str, str], None]] = None,
        on_finished: Optional[Callable[[bool, str, str], None]] = None,
    ):
        super().__init__(daemon=True, name="PQC-SendTask")
        self.file_path = file_path
        self.target_ip = target_ip
        self.target_port = target_port
        self.param_name = param_name
        self.engine_name = engine_name
        self.on_packet = on_packet
        self.on_progress = on_progress
        self.on_status = on_status
        self.on_finished = on_finished
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def run(self):
        yol = pathlib.Path(self.file_path)
        if not yol.is_file():
            if self.on_finished:
                self.on_finished(False, f"Hata: '{self.file_path}' bulunamadı.", "")
            return

        toplam_bayt = yol.stat().st_size
        p = PARAMETRELER[self.param_name]

        if self.on_status:
            self.on_status(f"SHA-256 bütünlük özeti hesaplanıyor...", "INFO")

        hasher = hashlib.sha256()
        with open(yol, "rb") as f:
            while blok := f.read(1024 * 1024):
                hasher.update(blok)
        orijinal_ozet = hasher.hexdigest()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)

        try:
            if self.on_status:
                self.on_status(f"{self.target_ip}:{self.target_port} adresine bağlanılıyor...", "INFO")
            sock.connect((self.target_ip, self.target_port))

            # Kuantum El Sıkışma
            if self.on_status:
                self.on_status("ML-KEM Kuantum El Sıkışması başlatıldı...", "INFO")

            # 1. Alıcıdan ek (Açık Anahtar) al
            ek = recv_bytes(sock)
            if self.on_packet:
                self.on_packet(
                    PacketEvent("PQC_PUBKEY (ek)", "ALINDI", len(ek), ek, f"ML-KEM-768 Açık Anahtarı ({len(ek)} B)")
                )

            # 2. Gönderici encaps yapar (K, c üretir)
            from pqc import mlkem
            from pqc.kpke_kronecker import KroneckerPKE
            from pqc.kronecker import VARYANT
            from pqc.pqcdrop import anahtar_turet

            pke = KroneckerPKE(VARYANT[self.engine_name])
            t0 = time.perf_counter()
            K, c = mlkem.encaps(ek, p, pke=pke)
            t_encaps = (time.perf_counter() - t0) * 1000

            # c gönder
            send_bytes(sock, c)
            if self.on_packet:
                self.on_packet(
                    PacketEvent(
                        "PQC_CIPHERTEXT (c)",
                        "GÖNDERİLDİ",
                        len(c),
                        c,
                        f"Kronecker ile Kapsüllenen Sır ({len(c)} B, {t_encaps:.1f}ms)",
                    )
                )

            aes_anahtar = anahtar_turet(K)
            aes = AESGCM(aes_anahtar)

            # Metadata gönder
            metadata_raw = json.dumps(
                {
                    "ad": yol.name,
                    "boyut": toplam_bayt,
                    "sha256": orijinal_ozet,
                    "param": self.param_name,
                }
            ).encode("utf-8")
            meta_ct = aes.encrypt(b"METADATA_NC0", metadata_raw, None)
            send_bytes(sock, meta_ct)
            if self.on_packet:
                self.on_packet(
                    PacketEvent(
                        "METADATA_ENC",
                        "GÖNDERİLDİ",
                        len(meta_ct),
                        meta_ct,
                        f"Şifreli Dosya Başlığı ({yol.name})",
                    )
                )

            # Dosya akışı
            if self.on_status:
                self.on_status("Dosya AES-256-GCM ile şifrelenerek aktarılıyor...", "SUCCESS")

            aktarilan = 0
            chunk_idx = 0
            t0_aktar = time.perf_counter()

            with open(yol, "rb") as f:
                while not self.is_cancelled and (parca := f.read(CHUNK_BOYUTU)):
                    nonce = nonce_uret(chunk_idx)
                    sifreli_parca = aes.encrypt(nonce, parca, None)
                    send_bytes(sock, sifreli_parca)

                    aktarilan += len(parca)
                    chunk_idx += 1

                    # Paket olayı (Her 4 chunkta bir veya ilk 2 chunkta tetikle)
                    if self.on_packet and (chunk_idx <= 2 or chunk_idx % 4 == 0 or aktarilan >= toplam_bayt):
                        self.on_packet(
                            PacketEvent(
                                f"AES_GCM_CHUNK #{chunk_idx}",
                                "GÖNDERİLDİ",
                                len(sifreli_parca),
                                sifreli_parca[:256],
                                f"Blok #{chunk_idx} ({len(parca)} bayt veri + 16B GCM Tag)",
                            )
                        )

                    gecen = time.perf_counter() - t0_aktar
                    hiz_mb = (aktarilan / (1024 * 1024)) / (gecen if gecen > 0 else 0.001)

                    if self.on_progress:
                        self.on_progress(aktarilan, toplam_bayt, hiz_mb)

            if self.is_cancelled:
                if self.on_finished:
                    self.on_finished(False, "Aktarım kullanıcı tarafından iptal edildi.", "")
                return

            onay = recv_bytes(sock).decode("utf-8")
            if onay == "OK":
                if self.on_packet:
                    self.on_packet(
                        PacketEvent(
                            "SHA256_VERIFY",
                            "ALINDI",
                            2,
                            b"OK",
                            f"Alıcı Doğrulama İmzası (Özet: {orijinal_ozet[:8]}...)",
                        )
                    )
                if self.on_finished:
                    self.on_finished(True, f"'{yol.name}' başarıyla teslim edildi ve doğrulandı!", orijinal_ozet)
            else:
                if self.on_finished:
                    self.on_finished(False, f"Alıcı aktarımı reddetti: {onay}", "")

        except Exception as e:
            if self.on_finished:
                self.on_finished(False, f"Aktarım hatası: {e}", "")
        finally:
            try:
                sock.close()
            except Exception:
                pass


class ReceiveListener(threading.Thread):
    def __init__(
        self,
        port: int = VARSAYILAN_PORT,
        save_dir: str = "/home/halil/Downloads",
        param_name: str = VARSAYILAN_PARAM,
        engine_name: str = VARSAYILAN_MOTOR,
        on_packet: Optional[Callable[[PacketEvent], None]] = None,
        on_progress: Optional[Callable[[int, int, float], None]] = None,
        on_status: Optional[Callable[[str, str], None]] = None,
        on_file_received: Optional[Callable[[str, int, str], None]] = None,
        on_port_bound: Optional[Callable[[int], None]] = None,
    ):
        super().__init__(daemon=True, name="PQC-ReceiveListener")
        self.port = port
        self.save_dir = save_dir
        self.param_name = param_name
        self.engine_name = engine_name
        self.on_packet = on_packet
        self.on_progress = on_progress
        self.on_status = on_status
        self.on_file_received = on_file_received
        self.on_port_bound = on_port_bound
        self.running = False
        self._server_sock: Optional[socket.socket] = None

    def stop(self):
        self.running = False
        if self._server_sock:
            try:
                self._server_sock.close()
            except Exception:
                pass
            self._server_sock = None

    def run(self):
        self.running = True
        p = PARAMETRELER[self.param_name]
        os.makedirs(self.save_dir, exist_ok=True)

        # Port meşgulse otomatik olarak sonraki boş portu dene (+1, +2, ...)
        bound = False
        start_port = self.port
        max_attempts = 15

        for offset in range(max_attempts):
            curr_port = start_port + offset
            try:
                self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._server_sock.bind(("0.0.0.0", curr_port))
                self._server_sock.listen(2)
                self._server_sock.settimeout(1.5)
                self.port = curr_port
                bound = True
                if self.on_port_bound:
                    self.on_port_bound(self.port)
                break
            except OSError:
                if self._server_sock:
                    try:
                        self._server_sock.close()
                    except Exception:
                        pass
                    self._server_sock = None

        if not bound:
            if self.on_status:
                self.on_status(f"Alıcı dinleme hatası: {start_port}-{start_port+max_attempts-1} portları meşgul!", "ERROR")
            return

        if self.on_status:
            self.on_status(f"Port {self.port} dinleniyor (Kuantum Korumalı Alıcı Hazır)...", "INFO")

        while self.running:
            try:
                conn, addr = self._server_sock.accept()
            except socket.timeout:
                continue
            except Exception:
                break

            conn.settimeout(15.0)
            threading.Thread(
                target=self._handle_incoming, args=(conn, addr, p), daemon=True, name=f"PQC-Recv-{addr[0]}"
            ).start()

    def _handle_incoming(self, conn: socket.socket, addr, p: Parametre):
        try:
            if self.on_status:
                self.on_status(f"Bağlantı kabul edildi: {addr[0]} (El sıkışma başlıyor...)", "INFO")

            # 1. Alıcı Keygen (ek, dk)
            from pqc import mlkem
            from pqc.kpke_kronecker import KroneckerPKE
            from pqc.kronecker import VARYANT
            from pqc.pqcdrop import anahtar_turet

            pke = KroneckerPKE(VARYANT[self.engine_name])
            t0 = time.perf_counter()
            ek, dk = mlkem.keygen(p, pke=pke)
            t_keygen = (time.perf_counter() - t0) * 1000

            # 2. ek gönder
            send_bytes(conn, ek)
            if self.on_packet:
                self.on_packet(
                    PacketEvent("PQC_PUBKEY (ek)", "GÖNDERİLDİ", len(ek), ek, f"Açık Anahtar ({len(ek)} B)")
                )

            # 3. c al
            c = recv_bytes(conn)
            if self.on_packet:
                self.on_packet(
                    PacketEvent("PQC_CIPHERTEXT (c)", "ALINDI", len(c), c, f"Şifreli Kapsül ({len(c)} B)")
                )

            # 4. K decaps
            t0 = time.perf_counter()
            K = mlkem.decaps(dk, c, p, pke=pke)
            t_decaps = (time.perf_counter() - t0) * 1000

            aes_anahtar = anahtar_turet(K)
            aes = AESGCM(aes_anahtar)

            # 5. Metadata al
            meta_ct = recv_bytes(conn)
            if self.on_packet:
                self.on_packet(
                    PacketEvent("METADATA_ENC", "ALINDI", len(meta_ct), meta_ct, "Şifreli Dosya Başlığı")
                )

            metadata_raw = aes.decrypt(b"METADATA_NC0", meta_ct, None)
            metadata = json.loads(metadata_raw.decode("utf-8"))
            dosya_adi = metadata["ad"]
            toplam_bayt = metadata["boyut"]
            beklenen_sha256 = metadata["sha256"]

            hedef_dosya = pathlib.Path(self.save_dir) / dosya_adi
            hasher = hashlib.sha256()

            if self.on_status:
                self.on_status(f"'{dosya_adi}' ({toplam_bayt / (1024 * 1024):.2f} MB) alınıyor...", "INFO")

            alinan = 0
            chunk_idx = 0
            t0_aktar = time.perf_counter()

            with open(hedef_dosya, "wb") as f:
                while alinan < toplam_bayt:
                    sifreli_parca = recv_bytes(conn)
                    nonce = nonce_uret(chunk_idx)
                    parca = aes.decrypt(nonce, sifreli_parca, None)

                    f.write(parca)
                    hasher.update(parca)

                    alinan += len(parca)
                    chunk_idx += 1

                    if self.on_packet and (chunk_idx <= 2 or chunk_idx % 4 == 0 or alinan >= toplam_bayt):
                        self.on_packet(
                            PacketEvent(
                                f"AES_GCM_CHUNK #{chunk_idx}",
                                "ALINDI",
                                len(sifreli_parca),
                                sifreli_parca[:256],
                                f"Blok #{chunk_idx} Çözüldü ({len(parca)} bayt)",
                            )
                        )

                    gecen = time.perf_counter() - t0_aktar
                    hiz_mb = (alinan / (1024 * 1024)) / (gecen if gecen > 0 else 0.001)

                    if self.on_progress:
                        self.on_progress(alinan, toplam_bayt, hiz_mb)

            hesaplanan_sha256 = hasher.hexdigest()
            if hesaplanan_sha256 == beklenen_sha256:
                send_bytes(conn, b"OK")
                if self.on_status:
                    self.on_status(f"'{dosya_adi}' SHA-256 doğrulandı ve kaydedildi!", "SUCCESS")
                if self.on_file_received:
                    self.on_file_received(str(hedef_dosya), toplam_bayt, hesaplanan_sha256)
            else:
                send_bytes(conn, b"ERR_HASH_MISMATCH")
                if self.on_status:
                    self.on_status("HATA: Dosya SHA-256 özeti uyuşmadı!", "ERROR")

        except Exception as e:
            if self.on_status:
                self.on_status(f"Alma işleminde hata: {e}", "ERROR")
        finally:
            try:
                conn.close()
            except Exception:
                pass

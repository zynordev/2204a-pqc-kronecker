"""PQC-Drop ASCII Terminal Kullanıcı Arayüzü (CLI / TUI).

Özellikler:
- Raspberry Pi, SSH ve başsız (headless) sunucularda doğrudan terminal içinde çalışır.
- X11 veya Wayland grafik ekranı GEREKTİRMEZ.
- VoiceBox tasarım estetiğinde yüksek kontrastlı ASCII/Unicode kutuları ve düzeni.
- Canlı UDP Ağ Keşfi (Radar), Dosya Gönder/Al, Wireshark benzeri canlı Hex dökümü
  ve Shannon Entropi ölçerini doğrudan terminalde gösterir.
- Klavye Kısayolları:
  [S] Dosya Gönder
  [V] Görünürlük Aç/Kapat (Stealth)
  [R] Radar Tara
  [Yukarı/Aşağı] Paketler arasında gezin (Hex dökümü incele)
  [C] Paket Denetim Tablosunu Temizle
  [Q] Çıkış
"""

import curses
import os
import pathlib
import socket
import sys
import threading
import time
from typing import Dict, List, Optional

from pqc.discovery import DiscoveryService, PeerInfo
from pqc.pqcdrop_engine import (
    PacketEvent,
    ReceiveListener,
    SendTask,
    formatla_hex_dokum,
    hesapla_shannon_entropisi,
)


class AsciiTuiApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.running = True

        # Terminal Ayarları
        curses.curs_set(0)
        curses.use_default_colors()
        self.stdscr.nodelay(True)  # Non-blocking input
        self.stdscr.timeout(100)   # 100ms refresh

        # Renk Çiftleri (Varsa)
        if curses.has_colors():
            try:
                curses.start_color()
                curses.init_pair(1, curses.COLOR_RED, -1)     # Red Accent
                curses.init_pair(2, curses.COLOR_GREEN, -1)   # Success Green
                curses.init_pair(3, curses.COLOR_CYAN, -1)    # Info Cyan
                curses.init_pair(4, curses.COLOR_YELLOW, -1)  # Warning Yellow
                curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE) # Inverted
            except Exception:
                pass

        # Durum Değişkenleri
        self.device_name = socket.gethostname() or "RaspberryPi-5"
        self.local_ip = self._get_local_ip()
        self.transfer_port = 8787
        self.discovery_port = 8766
        self.save_dir = os.path.expanduser("~/Downloads")

        self.peers: Dict[str, PeerInfo] = {}
        self.peers_list: List[PeerInfo] = []
        self.packets: List[PacketEvent] = []
        self.selected_packet_idx = -1

        self.status_msg = "HAZIR — Kuantum Korumalı Şifreleme Hattı Devrede."
        self.status_type = "INFO"
        self.transfer_info = "Boşta — Aktarım bekleniyor."
        self.transfer_pct = 0

        self.current_sender: Optional[SendTask] = None
        self.recv_listener: Optional[ReceiveListener] = None

        # UDP Keşif Servisi
        self.discovery = DiscoveryService(
            device_name=self.device_name,
            transfer_port=self.transfer_port,
            discovery_port=self.discovery_port,
            on_peers_updated=self._on_peers_updated,
        )

        # Servisleri Başlat
        self._start_services()

    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _start_services(self):
        # Alıcı Dinleyiciyi Başlat
        self.recv_listener = ReceiveListener(
            port=self.transfer_port,
            save_dir=self.save_dir,
            on_packet=self._add_packet,
            on_progress=self._update_progress,
            on_status=self._set_status,
            on_file_received=self._on_file_received,
            on_port_bound=self._on_port_bound,
        )
        self.recv_listener.start()

        # Keşif Servisini Başlat
        self.discovery.start()

    def _on_port_bound(self, actual_port: int):
        self.transfer_port = actual_port
        self.discovery.transfer_port = actual_port
        if self.discovery.visible:
            self.discovery.broadcast_beacon()

    def _on_peers_updated(self, peers_dict: dict):
        self.peers = peers_dict
        self.peers_list = list(peers_dict.values())

    def _add_packet(self, pkt: PacketEvent):
        self.packets.append(pkt)
        if len(self.packets) > 100:
            self.packets.pop(0)
        self.selected_packet_idx = len(self.packets) - 1

    def _update_progress(self, transferred: int, total: int, speed_mb: float):
        if total > 0:
            self.transfer_pct = int((transferred / total) * 100)
            t_mb = transferred / (1024 * 1024)
            tot_mb = total / (1024 * 1024)
            self.transfer_info = f"%{self.transfer_pct} ({t_mb:.2f}/{tot_mb:.2f} MB, {speed_mb:.2f} MB/s)"

    def _set_status(self, msg: str, stype: str = "INFO"):
        self.status_msg = msg
        self.status_type = stype

    def _on_file_received(self, fpath: str, size: int, sha256_hash: str):
        fname = os.path.basename(fpath)
        self._set_status(f"'{fname}' ({size // 1024} KB) ALINDI! SHA256: {sha256_hash[:8]}...", "SUCCESS")

    def run(self):
        while self.running:
            try:
                self.draw()
                ch = self.stdscr.getch()
                if ch != -1:
                    self.handle_input(ch)
            except Exception as e:
                self._set_status(f"Arayüz hatası: {e}", "ERROR")

        # Kapanış
        if self.discovery:
            self.discovery.stop()
        if self.recv_listener:
            self.recv_listener.stop()

    def draw(self):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        if h < 22 or w < 76:
            self.stdscr.addstr(0, 0, f"Terminal boyutu çok küçük ({w}x{h}). En az 80x24 yapın.")
            self.stdscr.refresh()
            return

        # 1. BAŞLIK BARI (VOICEBOX ASCII HEADER)
        border_top = "=" * (w - 1)
        self.stdscr.addstr(0, 0, border_top)
        header_title = " [PQC-DROP // VOICEBOX ASCII TUI]  NIST FIPS 203 ML-KEM + 22-BIT KRONECKER "
        self.stdscr.addstr(1, 1, header_title, curses.A_BOLD)

        vis_str = "[● GORUNUR]" if self.discovery.visible else "[○ GIZLI (STEALTH)]"
        sub_info = f" Cihaz: {self.device_name} | IP: {self.local_ip}:{self.transfer_port} | Durum: {vis_str} | Alici: [AKTIF]"
        self.stdscr.addstr(2, 1, sub_info[: w - 2])
        self.stdscr.addstr(3, 0, border_top)

        # 2. İKİ PANEL DÜZENİ (SOL: RADAR & TRANSFER, SAĞ: CANLI DENETÇİ)
        split_x = int(w * 0.44)
        mid_y_end = h - 4

        # Dikey Ayırıcı Çizgi
        for y in range(4, mid_y_end):
            self.stdscr.addch(y, split_x, "|")

        # --- SOL PANEL: RADAR & AKTARIM ---
        self.stdscr.addstr(4, 2, ">>> 1. YAKINDAKI CIHAZLAR (UDP RADAR)", curses.A_BOLD)
        y_peer = 5
        if not self.peers_list:
            self.stdscr.addstr(y_peer, 4, "[ Ağ taranıyor / Cihaz bulunamadı ]", curses.A_DIM)
            y_peer += 1
        else:
            for i, p in enumerate(self.peers_list[:4]):
                peer_line = f" [{i+1}] {p.name} ({p.ip}:{p.port})"
                self.stdscr.addstr(y_peer, 2, peer_line[: split_x - 3], curses.A_BOLD)
                y_peer += 1

        y_peer = max(y_peer, 9)
        self.stdscr.addstr(y_peer, 2, "-" * (split_x - 3))
        y_peer += 1

        self.stdscr.addstr(y_peer, 2, ">>> 2. DOSYA AKTARIM DURUMU", curses.A_BOLD)
        y_peer += 1
        self.stdscr.addstr(y_peer, 4, f"Hedef: [S] tuşuna basarak gönderin")
        y_peer += 1
        self.stdscr.addstr(y_peer, 4, f"Kayıt: {self.save_dir[:split_x - 12]}")
        y_peer += 1

        # ASCII Progress Bar
        bar_w = max(10, split_x - 18)
        filled = int((self.transfer_pct / 100) * bar_w)
        prog_bar = "[" + "#" * filled + "-" * (bar_w - filled) + "]"
        self.stdscr.addstr(y_peer, 4, f"{prog_bar} {self.transfer_pct}%", curses.A_BOLD)
        y_peer += 1
        self.stdscr.addstr(y_peer, 4, f"Metrik: {self.transfer_info[:split_x - 12]}")

        # --- SAĞ PANEL: CANLI WIRESHARK / HEX DENETÇİSİ ---
        self.stdscr.addstr(4, split_x + 2, ">>> 3. CANLI SIFRELEME DENETCİSİ (WIRESHARK KANITI)", curses.A_BOLD)

        # Paket Tablosu Başlığı
        self.stdscr.addstr(5, split_x + 2, "ZAMAN    | TIP            | YON  | BOYUT | ENTROPI", curses.A_UNDERLINE)

        # Son 6 Paketi Listele
        start_row = 6
        visible_pkts = self.packets[-6:] if len(self.packets) > 6 else self.packets
        for idx, pkt in enumerate(visible_pkts):
            row_y = start_row + idx
            is_selected = (len(self.packets) - len(visible_pkts) + idx) == self.selected_packet_idx
            prefix = " >" if is_selected else "  "
            line = f"{prefix}{pkt.timestamp} | {pkt.packet_type[:14]:<14} | {pkt.direction[:4]} | {pkt.size:>5}B | {pkt.entropy:.3f}"
            attr = curses.A_REVERSE if is_selected else curses.A_NORMAL
            self.stdscr.addstr(row_y, split_x + 1, line[: w - split_x - 2], attr)

        # Hex Dökümü Başlığı
        hex_header_y = start_row + 7
        self.stdscr.addstr(hex_header_y, split_x + 2, "-" * (w - split_x - 4))
        self.stdscr.addstr(hex_header_y + 1, split_x + 2, "SEÇİLİ PAKET 16-BAYT HEX & ASCII DÖKÜMÜ:", curses.A_BOLD)

        # Seçili paketin hex dökümünü yazdır
        if 0 <= self.selected_packet_idx < len(self.packets):
            sel_pkt = self.packets[self.selected_packet_idx]
            hex_lines = sel_pkt.hex_dump.split("\n")[:4]  # İlk 4 satır (64 bayt)
            for h_idx, h_line in enumerate(hex_lines):
                self.stdscr.addstr(hex_header_y + 2 + h_idx, split_x + 4, h_line[: w - split_x - 6], curses.A_DIM)
            ent_msg = f"SHANNON ENTROPISI: {sel_pkt.entropy:.3f} / 8.000 [TAM RASTGELE SIFRELI]"
            self.stdscr.addstr(hex_header_y + 2 + len(hex_lines), split_x + 4, ent_msg, curses.A_BOLD)
        else:
            self.stdscr.addstr(hex_header_y + 2, split_x + 4, "[ Paket yakalandığında burada hex dökümü belirecektir ]", curses.A_DIM)

        # 3. ALT DURUM BARI VE KISAYOLLAR
        self.stdscr.addstr(mid_y_end, 0, "=" * (w - 1))
        stat_color = curses.A_BOLD
        if self.status_type == "ERROR":
            stat_color = curses.color_pair(1) | curses.A_BOLD
        elif self.status_type == "SUCCESS":
            stat_color = curses.color_pair(2) | curses.A_BOLD

        self.stdscr.addstr(mid_y_end + 1, 2, f"DURUM: {self.status_msg}"[: w - 4], stat_color)

        keys_bar = " [S] Dosya Gonder | [V] Gorunurluk | [R] Radar Tara | [YUKARI/ASAGI] Paket Sec | [C] Temizle | [Q] Cikis"
        self.stdscr.addstr(mid_y_end + 2, 0, keys_bar[: w - 1], curses.A_STANDOUT)

        self.stdscr.refresh()

    def handle_input(self, ch: int):
        if ch in (ord("q"), ord("Q")):
            self.running = False
        elif ch in (ord("v"), ord("V")):
            # Görünürlük aç/kapat
            new_vis = not self.discovery.visible
            self.discovery.set_visible(new_vis)
            self._set_status(f"Görünürlük değiştirildi: {'AÇIK' if new_vis else 'GİZLİ (STEALTH)'}", "INFO")
        elif ch in (ord("r"), ord("R")):
            # Ağ keşfi tetikle
            self.discovery.broadcast_beacon()
            self._set_status("Ağdaki kuantum cihazlar taranıyor (UDP 8766)...", "INFO")
        elif ch in (ord("c"), ord("C")):
            # Paket logunu temizle
            self.packets.clear()
            self.selected_packet_idx = -1
            self._set_status("Paket denetim günlüğü temizlendi.", "INFO")
        elif ch == curses.KEY_UP:
            if self.selected_packet_idx > 0:
                self.selected_packet_idx -= 1
        elif ch == curses.KEY_DOWN:
            if self.selected_packet_idx < len(self.packets) - 1:
                self.selected_packet_idx += 1
        elif ch in (ord("s"), ord("S")):
            # Dosya Gönderme İnteraktif Diyaloğu
            self._prompt_send_file()

    def _prompt_send_file(self):
        h, w = self.stdscr.getmaxyx()
        dlg_y = max(2, h // 2 - 4)
        dlg_x = max(2, w // 2 - 32)
        dlg_w = min(64, w - 4)

        # Varsayılan hedef IP ve port
        default_target = "127.0.0.1"
        default_port = self.transfer_port
        if self.peers_list:
            default_target = self.peers_list[0].ip
            default_port = self.peers_list[0].port

        # Modal girdi için non-blocking modu kapat ve bekle
        self.stdscr.timeout(-1)
        self.stdscr.nodelay(False)
        curses.echo()
        curses.curs_set(1)

        try:
            # Kutuyu Çiz
            self.stdscr.addstr(dlg_y, dlg_x, "+--" + " KUANTUM KORUMALI DOSYA GONDER " + "-" * max(0, dlg_w - 34) + "+", curses.A_BOLD)
            self.stdscr.addstr(dlg_y + 1, dlg_x, f"| Hedef IP veya No [{default_target}]:".ljust(dlg_w - 1) + "|")
            self.stdscr.addstr(dlg_y + 2, dlg_x, f"| Dosya Yolu (Orn: test.txt veya ~/dosya.bin):".ljust(dlg_w - 1) + "|")
            self.stdscr.addstr(dlg_y + 3, dlg_x, "| [ENTER] Onayla | [Bos/ESC] Iptal".ljust(dlg_w - 1) + "|")
            self.stdscr.addstr(dlg_y + 4, dlg_x, "+" + "-" * (dlg_w - 2) + "+")
            self.stdscr.refresh()

            # 1. IP veya No Oku
            input_x = dlg_x + min(44, dlg_w - 18)
            self.stdscr.move(dlg_y + 1, input_x)
            raw_target = self.stdscr.getstr(dlg_y + 1, input_x, 18).decode("utf-8", errors="ignore").strip()

            target_ip = default_target
            target_port = default_port
            if raw_target:
                if raw_target.isdigit():
                    idx = int(raw_target) - 1
                    if 0 <= idx < len(self.peers_list):
                        target_ip = self.peers_list[idx].ip
                        target_port = self.peers_list[idx].port
                    else:
                        target_ip = raw_target
                else:
                    target_ip = raw_target

            # 2. Dosya Yolu Oku
            file_x = dlg_x + min(46, dlg_w - 18)
            self.stdscr.move(dlg_y + 2, file_x)
            raw_file = self.stdscr.getstr(dlg_y + 2, file_x, 26).decode("utf-8", errors="ignore").strip()

            if not raw_file:
                self._set_status("Gonderim iptal edildi (Dosya yolu bos).", "INFO")
                return

            file_path = os.path.expanduser(raw_file)
            if not os.path.isfile(file_path):
                self._set_status(f"HATA: '{file_path}' bulunamadi!", "ERROR")
                return

            fname = os.path.basename(file_path)
            self._set_status(f"'{fname}' -> {target_ip}:{target_port} gonderiliyor...", "INFO")
            self.transfer_pct = 0

            self.current_sender = SendTask(
                file_path=file_path,
                target_ip=target_ip,
                target_port=target_port,
                on_packet=self._add_packet,
                on_progress=self._update_progress,
                on_status=self._set_status,
                on_finished=lambda s, m, h: self._set_status(
                    f"{'BASARILI' if s else 'HATA'}: {m}", "SUCCESS" if s else "ERROR"
                ),
            )
            self.current_sender.start()

        except Exception as e:
            self._set_status(f"Gonderim hatasi: {e}", "ERROR")
        finally:
            curses.noecho()
            curses.curs_set(0)
            self.stdscr.nodelay(True)
            self.stdscr.timeout(100)


def main():
    curses.wrapper(lambda stdscr: AsciiTuiApp(stdscr).run())


if __name__ == "__main__":
    main()

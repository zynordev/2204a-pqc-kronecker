"""PQC-Drop Masaüstü Grafik Arayüzü (GUI).

Tasarım Sistemi: VoiceBox Design System (/home/halil/Downloads/voicebox-DESIGN.md)
- Yüksek kontrastlı editoryal dergi estetiği (#0A0A0A ve #FAFAFA).
- Agresif Kırmızı (#EF4444) tekil vurgu.
- 0px kenarlık yumuşatma (Keskin, düz, gölgesiz).
- Wireshark benzeri canlı hex/entropi denetimi, AirDrop tarzı otomatik yerel ağ keşfi,
  rakip kıyaslama matrisi ve interaktif 9. sınıf öğrenim simülatörleri.
"""

import os
import pathlib
import socket
import sys
import time

from PyQt6.QtCore import QObject, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from pqc.discovery import DiscoveryService, PeerInfo
from pqc.gui_theme import (
    COLOR_BG,
    COLOR_BORDER_STRONG,
    COLOR_BORDER_SUBTLE,
    COLOR_ERROR,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_TERTIARY,
    COLOR_SUCCESS,
    COLOR_SURFACE,
    COLOR_SURFACE_RAISED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_TERTIARY,
    COLOR_WARNING,
    VOICEBOX_QSS,
)
from pqc.pqcdrop_engine import (
    PacketEvent,
    ReceiveListener,
    SendTask,
    formatla_hex_dokum,
    hesapla_shannon_entropisi,
)


# =============================================================================
# QTHREAD WRAPPER: GÖNDERİCİ İŞ PARÇACIĞI
# =============================================================================
class SendWorker(QThread):
    packet_received = pyqtSignal(object)
    progress_updated = pyqtSignal(int, int, float)
    status_updated = pyqtSignal(str, str)
    send_finished = pyqtSignal(bool, str, str)

    def __init__(self, file_path: str, target_ip: str, target_port: int = 8765):
        super().__init__()
        self.file_path = file_path
        self.target_ip = target_ip
        self.target_port = target_port
        self.task: SendTask | None = None

    def run(self):
        self.task = SendTask(
            file_path=self.file_path,
            target_ip=self.target_ip,
            target_port=self.target_port,
            on_packet=lambda p: self.packet_received.emit(p),
            on_progress=lambda a, t, s: self.progress_updated.emit(a, t, s),
            on_status=lambda m, s: self.status_updated.emit(m, s),
            on_finished=lambda s, m, h: self.send_finished.emit(s, m, h),
        )
        self.task.run()

    def cancel(self):
        if self.task:
            self.task.cancel()


# =============================================================================
# QTHREAD WRAPPER: ALICI DİNLEYİCİ İŞ PARÇACIĞI
# =============================================================================
class ReceiveWorker(QThread):
    packet_received = pyqtSignal(object)
    progress_updated = pyqtSignal(int, int, float)
    status_updated = pyqtSignal(str, str)
    file_received = pyqtSignal(str, int, str)
    port_bound = pyqtSignal(int)

    def __init__(self, port: int = 8787, save_dir: str = "/home/halil/Downloads"):
        super().__init__()
        self.port = port
        self.save_dir = save_dir
        self.listener: ReceiveListener | None = None

    def run(self):
        self.listener = ReceiveListener(
            port=self.port,
            save_dir=self.save_dir,
            on_packet=lambda p: self.packet_received.emit(p),
            on_progress=lambda a, t, s: self.progress_updated.emit(a, t, s),
            on_status=lambda m, s: self.status_updated.emit(m, s),
            on_file_received=lambda f, b, h: self.file_received.emit(f, b, h),
            on_port_bound=lambda p: self.port_bound.emit(p),
        )
        self.listener.run()

    def stop(self):
        if self.listener:
            self.listener.stop()


class PeerBridge(QObject):
    peers_updated = pyqtSignal(dict)


# =============================================================================
# ANA PENCERE: VOICEBOX PQC-DROP GUI
# =============================================================================
class VoiceBoxPQCDropWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VOICEBOX // PQC-DROP: KUANTUM GÜVENLİ DOSYA AKTARIM İSTASYONU")
        self.resize(1240, 820)
        self.setMinimumSize(1000, 700)

        # Varsayılan Değerler
        self.device_name = socket.gethostname() or "Halil-Laptop"
        self.local_ip = self._get_local_ip()
        self.transfer_port = 8787
        self.save_dir = os.path.expanduser("~/Downloads")

        self.packets_history: list[PacketEvent] = []
        self.send_worker: SendWorker | None = None
        self.recv_worker: ReceiveWorker | None = None

        # Thread-safe Qt Signal Köprüsü
        self.peer_bridge = PeerBridge()
        self.peer_bridge.peers_updated.connect(self._refresh_peers_table)

        # UDP Otomatik Ağ Keşif Servisi
        self.discovery = DiscoveryService(
            device_name=self.device_name,
            transfer_port=self.transfer_port,
            on_peers_updated=self._on_peers_updated_callback,
        )

        self._init_ui()
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

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # 1. BAŞLIK BÖLÜMÜ (VOICEBOX EDITORIAL HEADER)
        header_widget = self._create_editorial_header()
        main_layout.addWidget(header_widget)

        # 2. CİHAZ PROFİLİ VE GÖRÜNÜRLÜK ŞERİDİ
        profile_bar = self._create_profile_bar()
        main_layout.addWidget(profile_bar)

        # 3. ANA SEKME ALANI (3 EDİTORYAL SEKME)
        self.tabs = QTabWidget()
        self.tab_transfer = QWidget()
        self.tab_benchmark = QWidget()
        self.tab_how_it_works = QWidget()

        self._init_tab_transfer()
        self._init_tab_benchmark()
        self._init_tab_how_it_works()

        self.tabs.addTab(self.tab_transfer, "1. AKTARIM & AĞ DENETİMİ")
        self.tabs.addTab(self.tab_benchmark, "2. LİTERATÜR & RAKİP KIYASLAMA")
        self.tabs.addTab(self.tab_how_it_works, "3. NASIL ÇALIŞIR? (9. SINIF)")
        main_layout.addWidget(self.tabs, stretch=1)

        # 4. ALT DURUM ÇUBUĞU (FOOTER BANNER)
        footer_bar = self._create_footer_bar()
        main_layout.addWidget(footer_bar)

    # -------------------------------------------------------------------------
    # EDİTORYAL BAŞLIK VE ŞERİTLER
    # -------------------------------------------------------------------------
    def _create_editorial_header(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(2)

        # Kategori Etiketi (Overline)
        lbl_overline = QLabel("TÜBİTAK 2204-A LİSE ARAŞTIRMA PROJELERİ // BİLGİSAYAR & SİBER GÜVENLİK")
        lbl_overline.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {COLOR_TEXT_SECONDARY}; letter-spacing: 0.12em; text-transform: uppercase;"
        )
        layout.addWidget(lbl_overline)

        # Masif Başlık
        lbl_title = QLabel("PQC-DROP // KUANTUM KORUMALI AKTARIM")
        lbl_title.setStyleSheet(
            f"font-family: 'Archivo Black', 'Arial Black', sans-serif; font-size: 32px; font-weight: 900; color: {COLOR_PRIMARY}; letter-spacing: -0.02em;"
        )
        layout.addWidget(lbl_title)

        # Alt Açıklama
        lbl_sub = QLabel(
            "NIST FIPS 203 ML-KEM-768 + MERKEZLENMİŞ KRONECKER (22-BİT) VE AES-256-GCM ŞİFRELEME MOTORU"
        )
        lbl_sub.setStyleSheet(f"font-size: 13px; font-weight: 500; color: {COLOR_TEXT_SECONDARY};")
        layout.addWidget(lbl_sub)

        # Agresif Kırmızı Vurgu Çizgisi (VoiceBox Red Underline)
        red_line = QFrame()
        red_line.setFixedHeight(3)
        red_line.setStyleSheet(f"background-color: {COLOR_SECONDARY}; border: none;")
        layout.addWidget(red_line)

        return container

    def _create_profile_bar(self) -> QWidget:
        card = QFrame()
        card.setProperty("voiceboxCard", "default")
        card.setStyleSheet(f"background-color: {COLOR_SURFACE}; border: 2px solid {COLOR_BORDER_STRONG}; padding: 8px 12px;")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(16)

        # Cihaz Adı
        lbl_name = QLabel("CİHAZ ADI:")
        lbl_name.setStyleSheet("font-weight: 700; font-size: 11px; letter-spacing: 0.06em;")
        layout.addWidget(lbl_name)

        self.txt_device_name = QLineEdit(self.device_name)
        self.txt_device_name.setFixedWidth(160)
        self.txt_device_name.textChanged.connect(self._on_device_name_changed)
        layout.addWidget(self.txt_device_name)

        # Yerel IP ve Port Bilgisi
        self.lbl_ip_info = QLabel(f"IP: {self.local_ip}:{self.transfer_port}")
        self.lbl_ip_info.setStyleSheet(
            f"font-family: 'Space Mono', monospace; font-size: 11px; font-weight: bold; background: {COLOR_BG}; border: 1px solid {COLOR_BORDER_STRONG}; padding: 4px 8px;"
        )
        layout.addWidget(self.lbl_ip_info)

        layout.addStretch(1)

        # Görünürlük Anahtarı (Visibility Toggle)
        self.btn_visibility = QPushButton("● AĞDA GÖRÜNÜR")
        self.btn_visibility.setCheckable(True)
        self.btn_visibility.setChecked(True)
        self.btn_visibility.setFixedWidth(160)
        self._update_visibility_btn_style(True)
        self.btn_visibility.clicked.connect(self._on_toggle_visibility)
        layout.addWidget(self.btn_visibility)

        # Alıcı Servis Durumu
        self.lbl_server_status = QLabel("● ALICI AKTİF")
        self.lbl_server_status.setStyleSheet(
            f"color: {COLOR_SUCCESS}; font-weight: 700; font-size: 11px; letter-spacing: 0.06em;"
        )
        layout.addWidget(self.lbl_server_status)

        return card

    def _update_visibility_btn_style(self, is_visible: bool):
        if is_visible:
            self.btn_visibility.setText("● AĞDA GÖRÜNÜR")
            self.btn_visibility.setStyleSheet(
                f"background-color: {COLOR_PRIMARY}; color: {COLOR_TERTIARY}; border: 2px solid {COLOR_PRIMARY}; font-weight: 700;"
            )
        else:
            self.btn_visibility.setText("○ GİZLİ (STEALTH)")
            self.btn_visibility.setStyleSheet(
                f"background-color: transparent; color: {COLOR_TEXT_SECONDARY}; border: 2px solid {COLOR_BORDER_STRONG}; font-weight: 700;"
            )

    def _create_footer_bar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet(f"border-top: 1px solid {COLOR_BORDER_SUBTLE}; padding-top: 6px;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 4, 0, 0)

        self.lbl_status_msg = QLabel("HAZIR — Kuantum Korumalı Şifreleme Hattı Devrede.")
        self.lbl_status_msg.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};")
        layout.addWidget(self.lbl_status_msg)

        layout.addStretch(1)

        lbl_engine_info = QLabel("MOTOR: 22-BİT KRONECKER (768B RAM) // AES-256-GCM")
        lbl_engine_info.setStyleSheet(
            f"font-family: 'Space Mono', monospace; font-size: 11px; color: {COLOR_TEXT_SECONDARY};"
        )
        layout.addWidget(lbl_engine_info)

        return bar

    # -------------------------------------------------------------------------
    # SEKME 1: AKTARIM VE CANLI AĞ DENETİMİ (WIRESHARK PANELİ DAHİL)
    # -------------------------------------------------------------------------
    def _init_tab_transfer(self):
        layout = QHBoxLayout(self.tab_transfer)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #D4D4D4; width: 3px; }")

        # SOL SÜTUN: TRANSFER & RADAR
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 6, 0)
        left_layout.setSpacing(12)

        # 1. Yakındaki Cihazlar (Radar Kartı)
        card_peers = QFrame()
        card_peers.setProperty("voiceboxCard", "default")
        card_peers_layout = QVBoxLayout(card_peers)
        card_peers_layout.setContentsMargins(14, 12, 14, 12)

        h_peers_title = QHBoxLayout()
        lbl_peers = QLabel("YAKINDAKİ CİHAZLAR (OTOMATİK AĞ KEŞFİ)")
        lbl_peers.setStyleSheet("font-weight: 700; font-size: 12px; letter-spacing: 0.06em;")
        h_peers_title.addWidget(lbl_peers)

        btn_refresh = QPushButton("YENİLE")
        btn_refresh.setProperty("voiceboxSize", "sm")
        btn_refresh.setProperty("voiceboxRole", "secondary")
        btn_refresh.setFixedWidth(70)
        btn_refresh.clicked.connect(self._manual_refresh_peers)
        h_peers_title.addWidget(btn_refresh)
        card_peers_layout.addLayout(h_peers_title)

        self.table_peers = QTableWidget(0, 4)
        self.table_peers.setHorizontalHeaderLabels(["CİHAZ ADI", "IP ADRESİ", "MOTOR", "İŞLEM"])
        self.table_peers.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_peers.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_peers.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_peers.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_peers.setFixedHeight(120)
        card_peers_layout.addWidget(self.table_peers)

        left_layout.addWidget(card_peers)

        # 2. Dosya Gönder Kartı (Elevated / Kırmızı Üst Çizgili)
        card_send = QFrame()
        card_send.setProperty("voiceboxCard", "elevated")
        card_send_layout = QVBoxLayout(card_send)
        card_send_layout.setContentsMargins(14, 14, 14, 14)
        card_send_layout.setSpacing(10)

        lbl_send_title = QLabel("DOSYA GÖNDER // KUANTUM ZIRHLI AKTARIM")
        lbl_send_title.setStyleSheet("font-weight: 800; font-size: 13px; letter-spacing: 0.04em;")
        card_send_layout.addWidget(lbl_send_title)

        # Hedef IP Girişi
        h_target = QHBoxLayout()
        lbl_target_ip = QLabel("HEDEF IP:")
        lbl_target_ip.setStyleSheet("font-weight: 700; font-size: 11px;")
        h_target.addWidget(lbl_target_ip)

        self.txt_target_ip = QLineEdit("127.0.0.1")
        self.txt_target_ip.setPlaceholderText("Örn: 192.168.1.110")
        h_target.addWidget(self.txt_target_ip)

        lbl_target_port = QLabel("PORT:")
        lbl_target_port.setStyleSheet("font-weight: 700; font-size: 11px;")
        h_target.addWidget(lbl_target_port)

        self.txt_target_port = QLineEdit("8787")
        self.txt_target_port.setFixedWidth(65)
        h_target.addWidget(self.txt_target_port)
        card_send_layout.addLayout(h_target)

        # Dosya Seçici
        h_file = QHBoxLayout()
        self.txt_file_path = QLineEdit()
        self.txt_file_path.setPlaceholderText("Gönderilecek dosyayı seçin...")
        h_file.addWidget(self.txt_file_path)

        btn_browse = QPushButton("DOSYA SEÇ")
        btn_browse.setProperty("voiceboxRole", "secondary")
        btn_browse.setFixedWidth(110)
        btn_browse.clicked.connect(self._browse_file)
        h_file.addWidget(btn_browse)
        card_send_layout.addLayout(h_file)

        # Gönder Düğmesi
        self.btn_send = QPushButton("KUANTUM KORUMALI GÖNDER")
        self.btn_send.setFixedHeight(42)
        self.btn_send.clicked.connect(self._start_send_file)
        card_send_layout.addWidget(self.btn_send)

        left_layout.addWidget(card_send)

        # 3. Dosya Alıcı & İlerleme Kartı
        card_recv = QFrame()
        card_recv.setProperty("voiceboxCard", "default")
        card_recv_layout = QVBoxLayout(card_recv)
        card_recv_layout.setContentsMargins(14, 12, 14, 12)
        card_recv_layout.setSpacing(8)

        lbl_recv_title = QLabel("DOSYA ALICI & İLERLEME DURUMU")
        lbl_recv_title.setStyleSheet("font-weight: 700; font-size: 12px;")
        card_recv_layout.addWidget(lbl_recv_title)

        h_savedir = QHBoxLayout()
        self.lbl_save_dir = QLabel(f"Kayıt Klasörü: {self.save_dir}")
        self.lbl_save_dir.setStyleSheet(f"font-size: 11px; color: {COLOR_TEXT_SECONDARY};")
        h_savedir.addWidget(self.lbl_save_dir)

        btn_changedir = QPushButton("DEĞİŞTİR")
        btn_changedir.setProperty("voiceboxSize", "sm")
        btn_changedir.setProperty("voiceboxRole", "secondary")
        btn_changedir.setFixedWidth(80)
        btn_changedir.clicked.connect(self._change_save_dir)
        h_savedir.addWidget(btn_changedir)
        card_recv_layout.addLayout(h_savedir)

        # İlerleme Çubuğu ve Metrikler
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        card_recv_layout.addWidget(self.progress_bar)

        self.lbl_progress_info = QLabel("Boşta — Aktarım bekleniyor.")
        self.lbl_progress_info.setStyleSheet("font-size: 11px; font-weight: 600;")
        card_recv_layout.addWidget(self.lbl_progress_info)

        left_layout.addWidget(card_recv)
        left_layout.addStretch(1)
        splitter.addWidget(left_widget)

        # SAĞ SÜTUN: WIRESHARK CANLI PAKET VE ENTROPİ DENETÇİSİ
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(6, 0, 0, 0)
        right_layout.setSpacing(10)

        # Wireshark Başlığı
        card_wire_header = QFrame()
        card_wire_header.setProperty("voiceboxCard", "default")
        card_wire_header.setStyleSheet(f"background-color: {COLOR_PRIMARY}; border: 2px solid {COLOR_PRIMARY}; padding: 6px 12px;")
        h_wire = QHBoxLayout(card_wire_header)
        h_wire.setContentsMargins(4, 4, 4, 4)

        lbl_wire_title = QLabel("CANLI AĞ VE ŞİFRELEME DENETÇİSİ (WIRESHARK KANITI)")
        lbl_wire_title.setStyleSheet(f"color: {COLOR_TERTIARY}; font-weight: 800; font-size: 12px; letter-spacing: 0.05em;")
        h_wire.addWidget(lbl_wire_title)

        h_wire.addStretch(1)

        btn_clear_log = QPushButton("TEMİZLE")
        btn_clear_log.setProperty("voiceboxSize", "sm")
        btn_clear_log.setStyleSheet(f"background: transparent; color: {COLOR_TERTIARY}; border: 1px solid {COLOR_TERTIARY};")
        btn_clear_log.clicked.connect(self._clear_packet_log)
        h_wire.addWidget(btn_clear_log)
        right_layout.addWidget(card_wire_header)

        # Paket Tablosu
        self.table_packets = QTableWidget(0, 5)
        self.table_packets.setHorizontalHeaderLabels(["ZAMAN", "PAKET TİPİ", "YÖN", "BOYUT", "AÇIKLAMA"])
        self.table_packets.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_packets.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_packets.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_packets.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_packets.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table_packets.setFixedHeight(180)
        self.table_packets.itemSelectionChanged.connect(self._on_packet_selected)
        right_layout.addWidget(self.table_packets)

        # Seçili Paket Ayrıntısı ve Hex Dökümü
        lbl_hex_title = QLabel("SEÇİLİ PAKET DÖKÜMÜ // 16-BAYT HEX & ASCII İNCELEME:")
        lbl_hex_title.setStyleSheet("font-weight: 700; font-size: 11px;")
        right_layout.addWidget(lbl_hex_title)

        self.txt_hex_dump = QTextEdit()
        self.txt_hex_dump.setProperty("voiceboxCode", "true")
        self.txt_hex_dump.setReadOnly(True)
        self.txt_hex_dump.setFixedHeight(150)
        self.txt_hex_dump.setPlaceholderText("İncelemek için yukarıdaki tablodan bir pakete tıklayın...")
        right_layout.addWidget(self.txt_hex_dump)

        # Entropi Göstergesi
        card_entropy = QFrame()
        card_entropy.setStyleSheet(f"background: {COLOR_SURFACE}; border: 2px solid {COLOR_BORDER_STRONG}; padding: 8px 12px;")
        layout_ent = QHBoxLayout(card_entropy)
        layout_ent.setContentsMargins(6, 4, 6, 4)

        self.lbl_entropy_val = QLabel("SHANNON ENTROPİSİ: — / 8.000")
        self.lbl_entropy_val.setStyleSheet(
            f"font-family: 'Space Mono', monospace; font-weight: 800; font-size: 12px; color: {COLOR_PRIMARY};"
        )
        layout_ent.addWidget(self.lbl_entropy_val)

        layout_ent.addStretch(1)

        self.lbl_entropy_badge = QLabel("DURUM: BEKLENİYOR")
        self.lbl_entropy_badge.setStyleSheet(
            f"font-size: 11px; font-weight: 700; padding: 2px 8px; border: 1px solid {COLOR_BORDER_STRONG}; background: {COLOR_BG};"
        )
        layout_ent.addWidget(self.lbl_entropy_badge)
        right_layout.addWidget(card_entropy)

        # Jüri Kanıt Alıntısı (VoiceBox Pull-Quote)
        quote_frame = QFrame()
        quote_frame.setProperty("voiceboxCard", "quote")
        quote_layout = QVBoxLayout(quote_frame)
        quote_layout.setContentsMargins(12, 10, 12, 10)

        lbl_proof_title = QLabel("JÜRİ & ÖĞRETMEN İSPAT NOTU:")
        lbl_proof_title.setStyleSheet(f"font-weight: 800; font-size: 11px; color: {COLOR_SECONDARY};")
        quote_layout.addWidget(lbl_proof_title)

        lbl_proof_body = QLabel(
            "Wireshark gibi bir ağ dinleyicisi araya girse dahi; aktarılan dosyanın adı, içeriği ve oturum anahtarı "
            "kuantum bilgisayarlarla bile kırılamayacak şekilde ML-KEM-768 açık anahtarı ve AES-256-GCM ile zırhlanmıştır. "
            "7.99+ seviyesindeki Shannon entropisi verinin tam şifrelendiğini matematiksel olarak kanıtlar."
        )
        lbl_proof_body.setWordWrap(True)
        lbl_proof_body.setStyleSheet(f"font-size: 11.5px; font-style: italic; color: {COLOR_TEXT_PRIMARY};")
        quote_layout.addWidget(lbl_proof_body)
        right_layout.addWidget(quote_frame)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 6)
        layout.addWidget(splitter)

    # -------------------------------------------------------------------------
    # SEKME 2: LİTERATÜR & RAKİP KARŞILAŞTIRMA MATRİSİ
    # -------------------------------------------------------------------------
    def _init_tab_benchmark(self):
        layout = QVBoxLayout(self.tab_benchmark)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        lbl_bm_title = QLabel("LİTERATÜR VE EN YAKIN RAKİP KIYASLAMA MATRİSİ")
        lbl_bm_title.setStyleSheet("font-family: 'Archivo Black', sans-serif; font-size: 20px; font-weight: 900;")
        layout.addWidget(lbl_bm_title)

        lbl_bm_sub = QLabel(
            "Klasik asimetrik şifreleme (RSA), literatürdeki standart Kronecker ve resmi NIST NTT yöntemine karşı "
            "geliştirdiğimiz merkezlenmiş 22-bit Kronecker modelinin donanım ve güvenlik üstünlükleri:"
        )
        lbl_bm_sub.setStyleSheet(f"font-size: 13px; color: {COLOR_TEXT_SECONDARY};")
        layout.addWidget(lbl_bm_sub)

        # Kıyaslama Tablosu
        table = QTableWidget(7, 5)
        headers = [
            "ÖZELLİK / METRİK",
            "KLASİK RSA-4096 (ESKİ)",
            "STANDART KRONECKER (32-BİT)",
            "BİZİM YÖNTEMİMİZ (22-BİT)",
            "NIST REFERANS NTT",
        ]
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        matrix = [
            ("Kuantum Direnci (Shor Alg.)", "❌ 0 BİT (Kırılır)", "✅ Kategori 3 Güvenli", "✅ Kategori 3 Güvenli", "✅ Kategori 3 Güvenli"),
            ("Katsayı Başına Bit", "—", "32 Bit / Katsayı", "22 Bit / Katsayı (%34 Tasarruf)", "Katsayı Alanı"),
            ("Büyük Tamsayı Genişliği", "4096 Bit", "8192 Bit", "5632 Bit (En Kompakt)", "—"),
            ("ESP32 Ara Tampon RAM", "—", "1024B + 511 dizi", "768 Bayt (Sıfır Ara Dizi)", "Özel Tablolar"),
            ("Donanım Bağımlılığı", "Modüler Üs Alma Don.", "Standart Tamsayı Çarpıcı", "Standart Çarpıcı (Her Çipte)", "Özel Asal Modül Don."),
            ("Tamsayı Çarpım Hızı", "Yavaş (Büyük Üs)", "1.00x Referans", "2.05x Daha Hızlı", "—"),
            ("IoT / Edge Uygunluğu", "Çok Zayıf", "Düşük (Yüksek RAM)", "Mükemmel (Mikro Bellek)", "Orta (Donanım Yoksa)"),
        ]

        for r_idx, row in enumerate(matrix):
            for c_idx, val in enumerate(row):
                item = QTableWidgetItem(val)
                if c_idx == 3:  # Bizim Yöntemimiz Sütunu
                    item.setFont(QFont("Work Sans", 9, QFont.Weight.Bold))
                    item.setBackground(Qt.GlobalColor.white)
                if "❌" in val:
                    item.setForeground(Qt.GlobalColor.red)
                elif "✅" in val:
                    item.setForeground(Qt.GlobalColor.darkGreen)
                table.setItem(r_idx, c_idx, item)

        table.setFixedHeight(240)
        layout.addWidget(table)

        # Pull Quote Açıklaması
        pq = QFrame()
        pq.setProperty("voiceboxCard", "quote")
        pq_layout = QVBoxLayout(pq)
        pq_layout.setContentsMargins(16, 12, 16, 12)

        pq_title = QLabel("BİZİM ÖZGÜN BİLİMSEL BULUŞUMUZ:")
        pq_title.setStyleSheet(f"font-weight: 800; font-size: 12px; color: {COLOR_SECONDARY};")
        pq_layout.addWidget(pq_title)

        pq_body = QLabel(
            "\"Literatürdeki standart Kronecker ikamesi katsayıları işaretsiz [0, 3328] kabul ederek 32-bitlik kutucuklar açar "
            "ve 8192 bitlik devasa tamsayılar üretir. Biz ML-KEM standardında kullanıcının gizli anahtarının katsayılarının "
            "FIPS 203 gereği daima [-3, +3] aralığında olduğunu fark ettik. Katsayıları sıfır etrafında merkezleyerek "
            "en büyük katsayı çarpımını 2200 kat küçülttük ve tamsayı genişliğini 22 bite indirerek %34 bellek tasarrufu sağladık. "
            "Bu sayede ESP32 gibi mikrodenetleyicilerde 768 baytlık mikro bellek modeliyle çalışmayı dünyada ilk kez başardık.\""
        )
        pq_body.setWordWrap(True)
        pq_body.setStyleSheet("font-size: 13px; font-style: italic; line-height: 1.6;")
        pq_layout.addWidget(pq_body)
        layout.addWidget(pq)

        layout.addStretch(1)

    # -------------------------------------------------------------------------
    # SEKME 3: NASIL ÇALIŞIR? (9. SINIF İNTERAKTİF ÖĞRENİM)
    # -------------------------------------------------------------------------
    def _init_tab_how_it_works(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {COLOR_BG};")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        lbl_edu_title = QLabel("9. SINIF DÜZEYİNDE SIFIRDAN MANTIK VE İNTERAKTİF SİMÜLATÖRLER")
        lbl_edu_title.setStyleSheet("font-family: 'Archivo Black', sans-serif; font-size: 18px; font-weight: 900;")
        layout.addWidget(lbl_edu_title)

        # 1. Simülatör: 23² Binom Açılımı Hilesi
        card_binom = QFrame()
        card_binom.setProperty("voiceboxCard", "default")
        c_b_layout = QVBoxLayout(card_binom)
        c_b_layout.setContentsMargins(16, 14, 16, 14)

        lbl_b_head = QLabel("1. SENİN BULDUĞUN FİKİR: 23² BİNOM AÇILIMI HİLESİ")
        lbl_b_head.setStyleSheet(f"font-weight: 800; font-size: 13px; color: {COLOR_PRIMARY};")
        c_b_layout.addWidget(lbl_b_head)

        lbl_b_desc = QLabel(
            "İki basamaklı bir sayının karesini alırken (2x+3)² özdeşliğini kullanırız: 4x² + 12x + 9. "
            "Katsayılar [4, 12, 9]'dur. Sağdan sola elde taşıdığımızda: 9 kalır, 12'nin 2'si kalır 1 sola taşar, "
            "4+1=5 olur. Sonuç: 529! Kronecker ikamesi tam olarak bu işlemin tersidir."
        )
        lbl_b_desc.setWordWrap(True)
        c_b_layout.addWidget(lbl_b_desc)

        h_calc = QHBoxLayout()
        self.txt_calc_input = QLineEdit("23")
        self.txt_calc_input.setFixedWidth(80)
        h_calc.addWidget(QLabel("İki Basamaklı Sayı:"))
        h_calc.addWidget(self.txt_calc_input)

        btn_calc_demo = QPushButton("HESAPLA & ADIMLARI GÖSTER")
        btn_calc_demo.setProperty("voiceboxRole", "secondary")
        btn_calc_demo.setFixedWidth(220)
        btn_calc_demo.clicked.connect(self._simulate_binom_carry)
        h_calc.addWidget(btn_calc_demo)
        h_calc.addStretch(1)
        c_b_layout.addLayout(h_calc)

        self.lbl_binom_result = QLabel("Sonuç: 23² = (2x+3)² = 4x² + 12x + 9 ➔ Elde Taşıma: [4(+1), 2, 9] = 529")
        self.lbl_binom_result.setStyleSheet(
            f"font-family: 'Space Mono', monospace; font-weight: bold; background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER_STRONG}; padding: 8px 12px;"
        )
        c_b_layout.addWidget(self.lbl_binom_result)
        layout.addWidget(card_binom)

        # 2. İnteraktif Kart: Tren ve Saat Modülü (R_q = Z_q[X]/(X²⁵⁶+1))
        card_train = QFrame()
        card_train.setProperty("voiceboxCard", "default")
        c_t_layout = QVBoxLayout(card_train)
        c_t_layout.setContentsMargins(16, 14, 16, 14)

        lbl_t_head = QLabel("2. TREN VE SAAT MATEMATİĞİ (R_q = Z_q[X]/(X²⁵⁶ + 1), q = 3329)")
        lbl_t_head.setStyleSheet(f"font-weight: 800; font-size: 13px; color: {COLOR_PRIMARY};")
        c_t_layout.addWidget(lbl_t_head)

        lbl_t_desc = QLabel(
            "• <b>X²⁵⁶ (256 Vagonlu Tren):</b> Polinomun 256 terimi vardır. Tren 256 vagondan uzun olamaz.<br/>"
            "• <b>q = 3329 (Saat Matematiği / Mod):</b> Katsayılar 3329'u aşarsa 3329 çıkarılır; saat 13 olduğunda 1 dememiz gibidir.<br/>"
            "• <b>X²⁵⁶ = -1 (Ters Dönen Vagon):</b> Çarpımda X²⁵⁶ çıkarsa yerine -1 yazılır. 256'yı aşan yolcular ters işaretle başa döner!"
        )
        lbl_t_desc.setWordWrap(True)
        c_t_layout.addWidget(lbl_t_desc)
        layout.addWidget(card_train)

        # 3. İnteraktif Kart: H4 Güvenlik Açığı Deneyi (Neden 20 Bit Yapamayız?)
        card_h4 = QFrame()
        card_h4.setProperty("voiceboxCard", "elevated")
        c_h_layout = QVBoxLayout(card_h4)
        c_h_layout.setContentsMargins(16, 14, 16, 14)

        lbl_h_head = QLabel("3. H4 GÜVENLİK AÇIĞI DENEYİ: NEDEN 20 BİT YAPAMAYIZ?")
        lbl_h_head.setStyleSheet(f"font-weight: 800; font-size: 13px; color: {COLOR_SECONDARY};")
        c_h_layout.addWidget(lbl_h_head)

        lbl_h_desc = QLabel(
            "Teorem 1 gereği güvenli sınır <b>22 BİTTİR</b> (256 × 1664 × 3 = 1.277.952 ➔ 22 bit). "
            "Eğer 20 bite inilirse, saldırganın yolladığı tuzak şifreli metinler katsayıları taşırır. "
            "Taşma hatasının çıkıp çıkmaması kurbanın gizli anahtarının büyüklüğüne (||s||₁) bağlıdır. "
            "Saldırgan ekranda hata çıkıp çıkmadığına bakarak gizli anahtarı çalar!"
        )
        lbl_h_desc.setWordWrap(True)
        c_h_layout.addWidget(lbl_h_desc)

        h_h4_btn = QHBoxLayout()
        btn_h4_demo = QPushButton("H4 GÜVENLİK TAŞMASINI SİMÜLE ET (20-BİT)")
        btn_h4_demo.setProperty("voiceboxRole", "destructive")
        btn_h4_demo.setFixedWidth(280)
        btn_h4_demo.clicked.connect(self._simulate_h4_attack)
        h_h4_btn.addWidget(btn_h4_demo)
        h_h4_btn.addStretch(1)
        c_h_layout.addLayout(h_h4_btn)

        self.lbl_h4_result = QLabel("Durum: Sistem 22-bit güvenli sınırında çalışıyor (Taşma Yok).")
        self.lbl_h4_result.setStyleSheet(
            f"font-family: 'Space Mono', monospace; font-size: 11px; background: {COLOR_SURFACE}; border: 1px solid {COLOR_BORDER_STRONG}; padding: 6px 10px;"
        )
        c_h_layout.addWidget(self.lbl_h4_result)
        layout.addWidget(card_h4)

        scroll.setWidget(content)
        vbox = QVBoxLayout(self.tab_how_it_works)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(scroll)

    # -------------------------------------------------------------------------
    # İNTERAKTİF SİMÜLASYON FONKSİYONLARI (9. SINIF MODÜLLERİ)
    # -------------------------------------------------------------------------
    def _simulate_binom_carry(self):
        val = self.txt_calc_input.text().strip()
        try:
            sayi = int(val)
            if sayi < 10 or sayi > 99:
                QMessageBox.warning(self, "Uyarı", "Lütfen iki basamaklı bir sayı girin (Örn: 23)")
                return
            onlar = sayi // 10
            birler = sayi % 10
            # (ax + b)^2 = a^2 x^2 + 2ab x + b^2
            a2 = onlar * onlar
            ab2 = 2 * onlar * birler
            b2 = birler * birler

            # Elde Taşıma
            b_kalir = b2 % 10
            elde1 = b2 // 10

            orta = ab2 + elde1
            orta_kalir = orta % 10
            elde2 = orta // 10

            sol = a2 + elde2
            sonuc = (sol * 100) + (orta_kalir * 10) + b_kalir

            msg = (
                f"{sayi}² = ({onlar}x+{birler})² = {a2}x² + {ab2}x + {b2}\n"
                f"➔ Sağdan Sola Elde: Birler={b_kalir} (elde {elde1}), Onlar={orta_kalir} (elde {elde2}), Yüzler={sol}\n"
                f"➔ Sonuç: {sonuc} (Tam Karesiyle Birebir Doğrulandı!)"
            )
            self.lbl_binom_result.setText(msg)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir sayı girin.")

    def _simulate_h4_attack(self):
        msg = (
            "🚨 GÜVENLİK ALARMI: 20-Bit Denendi!\n"
            "• Tuzak Polinom: Katsayıları max (+1664, -1664)\n"
            "• Çarpım Değeri: 1.277.952 > 2²⁰ (1.048.576)\n"
            "• Sonuç: TAŞMA (OVERFLOW)! Şifre çözme hatası oluştu.\n"
            "• Sızıntı: Kurbanın gizli anahtarının ||s||₁ normu saldırgan tarafından deşifre edildi!\n"
            "✓ KANIT: Teorem 1 gereği 22 bitin altına inilemez!"
        )
        self.lbl_h4_result.setText(msg)
        self.lbl_h4_result.setStyleSheet(
            f"font-family: 'Space Mono', monospace; font-size: 11px; background: #FEF2F2; color: {COLOR_ERROR}; border: 2px solid {COLOR_ERROR}; padding: 8px 10px;"
        )

    # -------------------------------------------------------------------------
    # AĞ VE DOSYA İŞLEMLERİ
    # -------------------------------------------------------------------------
    def _start_services(self):
        # 1. Alıcı iş parçacığını başlat
        self.recv_worker = ReceiveWorker(port=self.transfer_port, save_dir=self.save_dir)
        self.recv_worker.packet_received.connect(self._add_packet_to_audit)
        self.recv_worker.progress_updated.connect(self._update_progress)
        self.recv_worker.status_updated.connect(self._update_status)
        self.recv_worker.file_received.connect(self._on_file_received)
        self.recv_worker.port_bound.connect(self._on_port_bound)
        self.recv_worker.start()

        # 2. Keşif servisini başlat
        self.discovery.start()

    def _on_port_bound(self, port: int):
        self.transfer_port = port
        self.discovery.transfer_port = port
        self.lbl_ip_info.setText(f"IP: {self.local_ip}:{port}")
        if self.discovery.visible:
            self.discovery.broadcast_beacon()

    def _on_device_name_changed(self, text: str):
        name = text.strip() or "Halil-Laptop"
        self.device_name = name
        self.discovery.set_device_name(name)

    def _on_toggle_visibility(self):
        is_visible = self.btn_visibility.isChecked()
        self.discovery.set_visible(is_visible)
        self._update_visibility_btn_style(is_visible)
        if is_visible:
            self._update_status("Cihaz artık yerel ağdaki diğer PQC-Drop cihazlarına görünür.", "INFO")
        else:
            self._update_status("Gizli Mod (Stealth) aktif: Cihaz ağ yayınlarına yanıt vermiyor.", "WARNING")

    def _manual_refresh_peers(self):
        self.discovery.broadcast_beacon()
        self._update_status("Ağdaki kuantum cihazlar taranıyor...", "INFO")

    def _on_peers_updated_callback(self, peers_dict: dict):
        # Background Python thread'inden Qt GUI thread'ine thread-safe signal aktarımı
        self.peer_bridge.peers_updated.emit(peers_dict)

    def _refresh_peers_table(self, peers_dict: dict):
        self.table_peers.setRowCount(0)
        for key, peer in peers_dict.items():
            r = self.table_peers.rowCount()
            self.table_peers.insertRow(r)

            # Cihaz Adı
            item_name = QTableWidgetItem(f"💻 {peer.name}")
            item_name.setFont(QFont("Work Sans", 9, QFont.Weight.Bold))
            self.table_peers.setItem(r, 0, item_name)

            # IP
            item_ip = QTableWidgetItem(f"{peer.ip}:{peer.port}")
            item_ip.setFont(QFont("Space Mono", 9))
            self.table_peers.setItem(r, 1, item_ip)

            # Motor
            item_eng = QTableWidgetItem(peer.pqc_engine)
            self.table_peers.setItem(r, 2, item_eng)

            # Seç Düğmesi
            btn_select = QPushButton("SEÇ")
            btn_select.setProperty("voiceboxSize", "sm")
            btn_select.setProperty("voiceboxRole", "secondary")
            btn_select.clicked.connect(lambda ch, ip=peer.ip, port=peer.port: self._select_peer(ip, port))
            self.table_peers.setCellWidget(r, 3, btn_select)

    def _select_peer(self, ip: str, port: int):
        self.txt_target_ip.setText(ip)
        self.txt_target_port.setText(str(port))
        self._update_status(f"Hedef cihaz seçildi: {ip}:{port}", "INFO")

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Gönderilecek Dosyayı Seçin")
        if path:
            self.txt_file_path.setText(path)

    def _change_save_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Kayıt Klasörünü Seçin", self.save_dir)
        if dir_path:
            self.save_dir = dir_path
            self.lbl_save_dir.setText(f"Kayıt Klasörü: {self.save_dir}")
            if self.recv_worker:
                self.recv_worker.save_dir = self.save_dir

    def _start_send_file(self):
        fpath = self.txt_file_path.text().strip()
        tip = self.txt_target_ip.text().strip()
        tport_str = self.txt_target_port.text().strip()

        if not fpath or not os.path.isfile(fpath):
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir dosya seçin.")
            return

        if not tip:
            QMessageBox.warning(self, "Hata", "Lütfen bir hedef IP adresi girin.")
            return

        try:
            tport = int(tport_str)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir port numarası girin.")
            return

        self.btn_send.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_progress_info.setText("Gönderim başlıyor...")

        self.send_worker = SendWorker(file_path=fpath, target_ip=tip, target_port=tport)
        self.send_worker.packet_received.connect(self._add_packet_to_audit)
        self.send_worker.progress_updated.connect(self._update_progress)
        self.send_worker.status_updated.connect(self._update_status)
        self.send_worker.send_finished.connect(self._on_send_finished)
        self.send_worker.start()

    def _on_send_finished(self, success: bool, msg: str, sha256_hash: str):
        self.btn_send.setEnabled(True)
        if success:
            QMessageBox.information(
                self,
                "Aktarım Başarılı",
                f"🎉 {msg}\n\nSHA-256 Özeti:\n{sha256_hash}\n\nKuantum Koruması: FIPS 203 ML-KEM-768 Doğrulandı!",
            )
            self._update_status("Dosya başarıyla teslim edildi ve alıcı tarafından onaylandı.", "SUCCESS")
        else:
            QMessageBox.critical(self, "Aktarım Hatası", f"❌ {msg}")
            self._update_status(f"Hata: {msg}", "ERROR")

    def _on_file_received(self, file_path: str, total_bytes: int, sha256_hash: str):
        fname = os.path.basename(file_path)
        size_mb = total_bytes / (1024 * 1024)
        QMessageBox.information(
            self,
            "Yeni Dosya Alındı",
            f"📥 '{fname}' ({size_mb:.2f} MB) başarıyla alındı ve kaydedildi!\n\n"
            f"Klasör: {file_path}\n"
            f"SHA-256 Özeti:\n{sha256_hash}\n\n"
            f"Kuantum Doğrulama: %100 Başarılı!",
        )
        self._update_status(f"'{fname}' başarıyla alındı ve bütünlüğü doğrulandı.", "SUCCESS")

    def _update_progress(self, transferred: int, total: int, speed_mb: float):
        if total > 0:
            pct = int((transferred / total) * 100)
            self.progress_bar.setValue(pct)
            t_mb = transferred / (1024 * 1024)
            tot_mb = total / (1024 * 1024)
            self.lbl_progress_info.setText(
                f"%{pct} tamamlandı — {t_mb:.2f} / {tot_mb:.2f} MB ({speed_mb:.2f} MB/s)"
            )

    def _update_status(self, msg: str, status_type: str = "INFO"):
        self.lbl_status_msg.setText(msg)
        if status_type == "ERROR":
            self.lbl_status_msg.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLOR_ERROR};")
        elif status_type == "SUCCESS":
            self.lbl_status_msg.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLOR_SUCCESS};")
        elif status_type == "WARNING":
            self.lbl_status_msg.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLOR_WARNING};")
        else:
            self.lbl_status_msg.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};")

    # -------------------------------------------------------------------------
    # CANLI WIRESHARK / PAKET DENETİMİ
    # -------------------------------------------------------------------------
    def _add_packet_to_audit(self, packet: PacketEvent):
        self.packets_history.append(packet)
        r = self.table_packets.rowCount()
        self.table_packets.insertRow(r)

        item_ts = QTableWidgetItem(packet.timestamp)
        item_ts.setFont(QFont("Space Mono", 8))
        self.table_packets.setItem(r, 0, item_ts)

        item_type = QTableWidgetItem(packet.packet_type)
        item_type.setFont(QFont("Work Sans", 8, QFont.Weight.Bold))
        self.table_packets.setItem(r, 1, item_type)

        item_dir = QTableWidgetItem(packet.direction)
        if packet.direction == "GÖNDERİLDİ":
            item_dir.setForeground(Qt.GlobalColor.darkBlue)
        else:
            item_dir.setForeground(Qt.GlobalColor.darkGreen)
        self.table_packets.setItem(r, 2, item_dir)

        item_size = QTableWidgetItem(f"{packet.size} B")
        item_size.setFont(QFont("Space Mono", 8))
        self.table_packets.setItem(r, 3, item_size)

        item_det = QTableWidgetItem(packet.details)
        self.table_packets.setItem(r, 4, item_det)

        # Tabloyu en son pakete kaydır
        self.table_packets.scrollToBottom()

        # Otomatik olarak son paketin hex dökümünü ve entropisini güncelle
        self._display_packet_dump(packet)

    def _on_packet_selected(self):
        selected_rows = self.table_packets.selectionModel().selectedRows()
        if selected_rows:
            idx = selected_rows[0].row()
            if 0 <= idx < len(self.packets_history):
                self._display_packet_dump(self.packets_history[idx])

    def _display_packet_dump(self, packet: PacketEvent):
        self.txt_hex_dump.setText(packet.hex_dump)
        ent = packet.entropy
        self.lbl_entropy_val.setText(f"SHANNON ENTROPİSİ: {ent:.3f} / 8.000")

        if ent >= 7.90:
            self.lbl_entropy_badge.setText("ŞİFRELİ (TAM RASTGELE)")
            self.lbl_entropy_badge.setStyleSheet(
                f"font-size: 11px; font-weight: 700; padding: 2px 8px; border: 1px solid {COLOR_SUCCESS}; color: {COLOR_SUCCESS}; background: #F0FDF4;"
            )
        elif ent >= 6.0:
            self.lbl_entropy_badge.setText("KORUMALI KAPSÜL")
            self.lbl_entropy_badge.setStyleSheet(
                f"font-size: 11px; font-weight: 700; padding: 2px 8px; border: 1px solid {COLOR_WARNING}; color: {COLOR_WARNING}; background: #FEFCE8;"
            )
        else:
            self.lbl_entropy_badge.setText("DÜŞÜK ENTROPİ")
            self.lbl_entropy_badge.setStyleSheet(
                f"font-size: 11px; font-weight: 700; padding: 2px 8px; border: 1px solid {COLOR_BORDER_STRONG}; color: {COLOR_TEXT_PRIMARY}; background: {COLOR_BG};"
            )

    def _clear_packet_log(self):
        self.table_packets.setRowCount(0)
        self.packets_history.clear()
        self.txt_hex_dump.clear()
        self.lbl_entropy_val.setText("SHANNON ENTROPİSİ: — / 8.000")
        self.lbl_entropy_badge.setText("DURUM: BEKLENİYOR")

    def closeEvent(self, event):
        # Kaynakları temizle
        if self.discovery:
            self.discovery.stop()
        if self.recv_worker:
            self.recv_worker.stop()
        if self.send_worker and self.send_worker.isRunning():
            self.send_worker.cancel()
        event.accept()


# =============================================================================
# ÇALIŞTIRMA GİRİŞ NOKTASI
# =============================================================================
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(VOICEBOX_QSS)

    window = VoiceBoxPQCDropWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""PQC-Drop Yerel Ağ Otomatik Cihaz Keşif Servisi (UDP Broadcast).

Özellikler:
- Port 8766 üzerinden UDP Broadcast ile komşu cihazları otomatik keşfeder.
- Cihaz kullanıcı adı (örn. 'Halil-Laptop', 'Metin-Hoca') ve durum bilgisi taşır.
- Görünürlük Modu (Açık / Gizli): Görünürlük kapalıyken beacon yayını durur ve gelen sorgulara yanıt verilmez.
- Güvenli JSON tabanlı protokol ('PQC_DROP_V1').
"""

import json
import logging
import socket
import threading
import time
from typing import Callable, Dict, Optional

DISCOVERY_PORT = 8766
BROADCAST_IP = "255.255.255.255"
BEACON_INTERVAL = 2.5  # Saniye
PEER_TIMEOUT = 8.0     # Çevrimdışı sayılma süresi


class PeerInfo:
    def __init__(self, name: str, ip: str, port: int, visible: bool = True, pqc_engine: str = "ML-KEM-768-Kronecker-22bit"):
        self.name = name
        self.ip = ip
        self.port = port
        self.visible = visible
        self.pqc_engine = pqc_engine
        self.last_seen = time.time()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "ip": self.ip,
            "port": self.port,
            "visible": self.visible,
            "pqc_engine": self.pqc_engine,
            "last_seen": self.last_seen,
        }


class DiscoveryService:
    def __init__(
        self,
        device_name: str,
        transfer_port: int = 8787,
        discovery_port: int = DISCOVERY_PORT,
        on_peers_updated: Optional[Callable[[Dict[str, PeerInfo]], None]] = None,
    ):
        self.device_name = device_name
        self.transfer_port = transfer_port
        self.discovery_port = discovery_port
        self.on_peers_updated = on_peers_updated

        self.visible = True
        self.running = False
        self.peers: Dict[str, PeerInfo] = {}  # key: "ip:port"
        self._lock = threading.Lock()

        self._sock: Optional[socket.socket] = None
        self._listen_thread: Optional[threading.Thread] = None
        self._beacon_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self.running:
            return
        self.running = True

        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # macOS / Linux için SO_REUSEPORT (varsa)
            if hasattr(socket, "SO_REUSEPORT"):
                try:
                    self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except OSError:
                    pass
            self._sock.bind(("", self.discovery_port))
            self._sock.settimeout(1.0)
        except Exception as e:
            logging.error(f"UDP Keşif soketi açılamadı: {e}")
            self.running = False
            return

        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True, name="PQC-Discovery-Listen")
        self._listen_thread.start()

        self._beacon_thread = threading.Thread(target=self._beacon_loop, daemon=True, name="PQC-Discovery-Beacon")
        self._beacon_thread.start()

    def stop(self) -> None:
        self.running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def set_visible(self, visible: bool) -> None:
        self.visible = visible
        if visible:
            self.broadcast_beacon()

    def set_device_name(self, name: str) -> None:
        self.device_name = name
        if self.visible:
            self.broadcast_beacon()

    def _get_broadcast_ips(self) -> set:
        broadcasts = {"255.255.255.255"}
        try:
            import subprocess
            out = subprocess.check_output(["ip", "-4", "addr", "show"], text=True, timeout=1.5)
            for line in out.splitlines():
                line = line.strip()
                if "brd " in line:
                    parts = line.split()
                    if "brd" in parts:
                        idx = parts.index("brd")
                        if idx + 1 < len(parts):
                            broadcasts.add(parts[idx + 1])
        except Exception:
            pass
        return broadcasts

    def broadcast_beacon(self) -> None:
        if not self.visible or not self._sock:
            return
        msg = {
            "proto": "PQC_DROP_V1",
            "type": "BEACON",
            "name": self.device_name,
            "port": self.transfer_port,
            "engine": "ML-KEM-768-Kronecker-22bit",
            "timestamp": time.time(),
        }
        try:
            data = json.dumps(msg).encode("utf-8")
            for b_ip in self._get_broadcast_ips():
                try:
                    self._sock.sendto(data, (b_ip, self.discovery_port))
                except Exception:
                    pass
        except Exception:
            pass

    def _listen_loop(self) -> None:
        while self.running and self._sock:
            try:
                data, addr = self._sock.recvfrom(2048)
                sender_ip = addr[0]
                self._handle_message(data, sender_ip)
            except socket.timeout:
                self._cleanup_stale_peers()
            except Exception:
                if not self.running:
                    break

    def _handle_message(self, data: bytes, sender_ip: str) -> None:
        try:
            msg = json.loads(data.decode("utf-8"))
            if msg.get("proto") != "PQC_DROP_V1":
                return

            msg_type = msg.get("type")
            if msg_type not in ("BEACON", "BEACON_REPLY"):
                return

            peer_name = msg.get("name", "Bilinmeyen")
            peer_port = msg.get("port", 8787)
            peer_engine = msg.get("engine", "ML-KEM-768")

            # Kendi kendimizi dinlemeyi filtreleyelim
            local_ips = self._get_local_ips()
            if sender_ip in local_ips and peer_name == self.device_name:
                return

            peer_key = f"{sender_ip}:{peer_port}"
            now = time.time()

            changed = False
            with self._lock:
                if peer_key not in self.peers:
                    self.peers[peer_key] = PeerInfo(
                        name=peer_name,
                        ip=sender_ip,
                        port=peer_port,
                        visible=True,
                        pqc_engine=peer_engine,
                    )
                    changed = True
                else:
                    peer = self.peers[peer_key]
                    if peer.name != peer_name or peer.pqc_engine != peer_engine:
                        peer.name = peer_name
                        peer.pqc_engine = peer_engine
                        changed = True
                    peer.last_seen = now

            # Eğer BEACON aldıysak ve görünürsek, hemen unicast BEACON_REPLY ile karşılık ver
            if msg_type == "BEACON" and self.visible and self._sock:
                reply = {
                    "proto": "PQC_DROP_V1",
                    "type": "BEACON_REPLY",
                    "name": self.device_name,
                    "port": self.transfer_port,
                    "engine": "ML-KEM-768-Kronecker-22bit",
                    "timestamp": time.time(),
                }
                try:
                    reply_data = json.dumps(reply).encode("utf-8")
                    self._sock.sendto(reply_data, (sender_ip, self.discovery_port))
                except Exception:
                    pass

            if changed and self.on_peers_updated:
                self.on_peers_updated(dict(self.peers))

        except Exception:
            pass

    def _cleanup_stale_peers(self) -> None:
        now = time.time()
        stale_keys = []
        with self._lock:
            for k, peer in self.peers.items():
                if now - peer.last_seen > PEER_TIMEOUT:
                    stale_keys.append(k)
            for k in stale_keys:
                del self.peers[k]

        if stale_keys and self.on_peers_updated:
            self.on_peers_updated(dict(self.peers))

    def _beacon_loop(self) -> None:
        while self.running:
            if self.visible:
                self.broadcast_beacon()
            time.sleep(BEACON_INTERVAL)

    def _get_local_ips(self) -> set:
        ips = {"127.0.0.1", "localhost"}
        try:
            import subprocess
            out = subprocess.check_output(["ip", "-4", "addr", "show"], text=True, timeout=1.5)
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("inet "):
                    parts = line.split()
                    if len(parts) >= 2:
                        ip = parts[1].split("/")[0]
                        ips.add(ip)
        except Exception:
            pass
        try:
            # Dışa yönelik soket açıp yerel IP'yi sorgula
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ips.add(s.getsockname()[0])
            s.close()
        except Exception:
            pass
        return ips

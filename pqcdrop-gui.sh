#!/usr/bin/env bash
# PQC-Drop GUI Başlatıcı (VoiceBox Design System)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

echo "=========================================================="
echo "🛡️  PQC-DROP // VOICEBOX DESIGN SYSTEM"
echo "Kuantum Güvenli Dosya Aktarımı & Ağ Denetçisi Başlatılıyor..."
echo "=========================================================="

if [ -f "$SCRIPT_DIR/.venv/bin/python3" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python3"
else
    PYTHON_BIN="$(which python3)"
fi

# Eğer grafik ekran (DISPLAY/WAYLAND) yoksa veya PyQt6 kurulu değilse TUI'ye yönlendir
if ! "$PYTHON_BIN" -c "import PyQt6" 2>/dev/null; then
    echo "⚠️  PyQt6 bulunamadı veya grafik ekran yok (SSH oturumu)."
    echo "👉 Terminal ASCII TUI moduna geçiliyor: ./pqcdrop-tui.sh"
    echo "=========================================================="
    exec "$SCRIPT_DIR/pqcdrop-tui.sh" "$@"
fi

exec "$PYTHON_BIN" -m pqc.gui "$@"

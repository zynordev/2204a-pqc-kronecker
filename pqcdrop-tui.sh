#!/usr/bin/env bash
# PQC-Drop ASCII CLI / TUI Başlatıcı (Raspberry Pi & SSH Uyumlu)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Eğer sanal ortam varsa onu kullan, yoksa sistem python3
if [ -f "$SCRIPT_DIR/.venv/bin/python3" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python3"
else
    PYTHON_BIN="python3"
fi

exec "$PYTHON_BIN" -m pqc.tui "$@"

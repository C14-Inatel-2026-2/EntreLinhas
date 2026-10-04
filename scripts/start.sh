#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

VENV_DIR="${VENV_DIR:-.venv}"
export VENV_DIR
if [[ $# -gt 1 || ( $# -eq 1 && "$1" != "--install" ) ]]; then
    echo "Uso: bash scripts/start.sh [--install]" >&2
    exit 1
fi

if [[ "${1:-}" == "--install" || ! -x "$VENV_DIR/bin/python" ]]; then
    command -v python3 >/dev/null || { echo "Instale Python 3.9+." >&2; exit 1; }
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/python" -m pip install -r requirements.txt
fi

# As tabelas SQLite são criadas ao carregar app:app.
exec bash scripts/run.sh

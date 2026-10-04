#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

VENV_DIR="${VENV_DIR:-.venv}"
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    echo "Ambiente virtual ausente. Execute: bash scripts/start.sh --install" >&2
    exit 1
fi

export PORT="${PORT:-5000}"
echo "EntreLinhas: http://localhost:${PORT}"
exec "$VENV_DIR/bin/python" -m gunicorn app:app \
    --bind "${HOST:-127.0.0.1}:${PORT}" \
    --workers 1 --threads 4 --access-logfile - --error-logfile -

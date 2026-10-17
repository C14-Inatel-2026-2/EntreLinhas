#!/bin/sh
set -eu

export DATABASE_PATH="${DATABASE_PATH:-/data/jogo.db}"
export GUNICORN_CMD_ARGS="--bind 0.0.0.0:${PORT:-5000} ${GUNICORN_CMD_ARGS:-}"
mkdir -p "$(dirname "$DATABASE_PATH")"

# Railway mounts volumes as root. Fix ownership, then drop privileges.
if [ "$(id -u)" = "0" ]; then
    chown app:app "$(dirname "$DATABASE_PATH")"
    for file in "$DATABASE_PATH" "$DATABASE_PATH-journal" "$DATABASE_PATH-wal" "$DATABASE_PATH-shm"; do
        if [ -f "$file" ]; then
            chown app:app "$file"
        fi
    done
    exec gosu app "$@"
fi

exec "$@"

#!/usr/bin/env bash
cd "$(dirname "$0")/.."
source .venv/bin/activate
python3 -m http.server 8000 --bind 127.0.0.1 --directory static

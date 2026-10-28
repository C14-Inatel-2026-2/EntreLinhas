"""Publica somente o SHA aprovado e verifica a versão efetivamente servida."""
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]


def main():
    commit = os.environ["RELEASE_COMMIT"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise SystemExit("RELEASE_COMMIT inválido")
    for name in ("DOMAIN_APPROVED_COMMIT", "BACKEND_APPROVED_COMMIT", "TESTS_APPROVED_COMMIT"):
        if os.environ.get(name) != commit:
            raise SystemExit(f"Deploy bloqueado: {name} não aprova o SHA solicitado")
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    changed = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True).strip()
    if actual != commit or changed:
        raise SystemExit("Deploy bloqueado: checkout diferente do commit testado ou arquivos alterados")
    # Artefato temporário de build, incluído no COPY frontend/static do Dockerfile.
    marker = ROOT / "frontend/static/release.json"
    if marker.exists():
        raise SystemExit("Marcador de release preexistente: remova-o antes de publicar")
    marker.write_text(json.dumps({"commit": commit}) + "\n")
    try:
        subprocess.run([
            "railway", "up", "--ci", "--project", os.environ["RAILWAY_PROJECT_ID"],
            "--service", os.environ["RAILWAY_SERVICE"],
            "--environment", os.environ["RAILWAY_ENVIRONMENT"],
            "--message", f"Jenkins {os.environ.get('BUILD_NUMBER', 'local')} commit {commit}",
        ], cwd=ROOT, check=True)
        base = os.environ["PUBLIC_URL"].rstrip("/")
        for attempt in range(36):
            try:
                with urlopen(base + f"/static/release.json?commit={commit}", timeout=10) as response:
                    if json.load(response) != {"commit": commit}:
                        raise ValueError("Versão publicada ainda não corresponde ao commit testado")
                with urlopen(base + "/health", timeout=10) as response:
                    if json.load(response) != {"status": "ok"}:
                        raise ValueError("Banco indisponível")
                with urlopen(base + "/static/index.html", timeout=10) as response:
                    if b'id="form-iniciar"' not in response.read():
                        raise ValueError("Interface indisponível")
                print(f"Deploy verificado: commit {commit}, interface e banco disponíveis.")
                return
            except (OSError, ValueError) as error:
                print(f"Verificação {attempt + 1}/36: {error}", flush=True)
                if attempt < 35:
                    time.sleep(5)
        raise SystemExit("Deploy não passou na verificação da versão, interface e banco")
    finally:
        marker.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

"""Unitários e Cypress contra Flask/SQLite descartáveis, sem usar portas fixas."""
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]


def interromper(signum, frame):
    raise SystemExit(128 + signum)


def main():
    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(signum, interromper)
    reports = ROOT / "frontend/reports"
    (reports / "frontend").mkdir(parents=True, exist_ok=True)
    subprocess.run(["npm", "run", "test:unit:ci"], cwd=ROOT / "frontend", check=True)
    with tempfile.TemporaryDirectory(prefix="entrelinhas-e2e-") as temporary:
        # Mantém a porta reservada até o Gunicorn herdar o socket.
        with socket.socket() as listener, (reports / "flask.log").open("w") as log:
            listener.bind(("127.0.0.1", 0))
            listener.listen(128)
            base = f"http://127.0.0.1:{listener.getsockname()[1]}"
            server = subprocess.Popen(
                [sys.executable, "-m", "gunicorn", "--workers", "1", "--threads", "4",
                 "--bind", f"fd://{listener.fileno()}", "app:app"],
                cwd=ROOT / "backend", stdout=log, stderr=subprocess.STDOUT,
                pass_fds=(listener.fileno(),), start_new_session=True,
                env={**os.environ, "DATABASE_PATH": str(Path(temporary) / "jogo.db")},
            )
            try:
                for attempt in range(30):
                    if server.poll() is not None:
                        raise RuntimeError("Gunicorn encerrou antes de ficar pronto; veja frontend/reports/flask.log")
                    try:
                        with urlopen(base + "/health", timeout=2) as response:
                            healthy = json.load(response) == {"status": "ok"}
                        with urlopen(base + "/static/index.html", timeout=2) as response:
                            healthy = healthy and b'id="form-iniciar"' in response.read()
                        if healthy:
                            break
                    except (OSError, ValueError):
                        pass
                    time.sleep(1)
                else:
                    raise RuntimeError("Flask não ficou pronto; veja frontend/reports/flask.log")
                print(f"Flask pronto em {base}; banco temporário isolado.", flush=True)
                subprocess.run(["npm", "run", "e2e:ci"], cwd=ROOT / "frontend", check=True,
                               env={**os.environ, "CYPRESS_BASE_URL": base})
            finally:
                # Encerra e espera o grupo inteiro, inclusive o worker, antes de apagar o banco.
                try:
                    os.killpg(server.pid, signal.SIGTERM)
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(server.pid, signal.SIGKILL)
                    server.wait()
                except ProcessLookupError:
                    server.wait()


if __name__ == "__main__":
    main()

"""Verifica interface e saúde do banco após o deploy, sem criar partidas."""
import argparse
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen


def verify(base_url):
    with urlopen(f"{base_url}/health", timeout=10) as response:
        if response.status != 200 or json.load(response) != {"status": "ok"}:
            raise ValueError("Healthcheck inválido")
    with urlopen(f"{base_url}/static/index.html", timeout=10) as response:
        if response.status != 200 or b'id="form-iniciar"' not in response.read():
            raise ValueError("Interface indisponível")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    parsed = urlparse(args.url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        parser.error("Informe um domínio HTTPS, sem caminho ou credenciais.")
    base_url = args.url.rstrip("/")
    for attempt in range(12):
        try:
            verify(base_url)
            print("Deploy verificado: interface acessível e banco saudável.")
            return
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
            print(f"Verificação {attempt + 1}/12 falhou: {error}")
            if attempt < 11:
                time.sleep(5)
    raise SystemExit("Deploy não passou na verificação pública.")


if __name__ == "__main__":
    main()

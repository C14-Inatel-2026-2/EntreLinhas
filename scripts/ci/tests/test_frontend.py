import importlib.util
from pathlib import Path
import signal
import subprocess
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("ci_frontend", Path(__file__).parents[1] / "frontend.py")
frontend = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(frontend)


@unittest.skipUnless(importlib.util.find_spec("gunicorn"), "requer as dependências de backend")
class FrontendCleanupTests(unittest.TestCase):
    def test_cypress_failure_stops_real_gunicorn_and_removes_database(self):
        servers = []
        databases = []
        original_popen = subprocess.Popen

        def start(*args, **kwargs):
            databases.append(Path(kwargs["env"]["DATABASE_PATH"]))
            process = original_popen(*args, **kwargs)
            servers.append(process)
            return process

        previous = {sig: signal.getsignal(sig) for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
        try:
            with patch.object(frontend, "executar", side_effect=[None, subprocess.CalledProcessError(1, "cypress")]), patch.object(frontend.subprocess, "Popen", side_effect=start):
                with self.assertRaises(subprocess.CalledProcessError):
                    frontend.main()
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        self.assertEqual(len(servers), 1)
        self.assertIsNotNone(servers[0].poll(), "Gunicorn precisa encerrar mesmo com Cypress em falha")
        self.assertFalse(databases[0].parent.exists(), "banco temporário precisa ser removido")


if __name__ == "__main__":
    unittest.main()

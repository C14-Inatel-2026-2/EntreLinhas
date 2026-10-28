import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from io import BytesIO

SPEC = importlib.util.spec_from_file_location("ci_deploy", Path(__file__).parents[1] / "deploy.py")
deploy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(deploy)
SHA = "a" * 40


class DeployTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "frontend/static").mkdir(parents=True)
        self.marker = self.root / "frontend/static/release.json"
        self.env = {
            "RELEASE_COMMIT": SHA, "DOMAIN_APPROVED_COMMIT": SHA, "BACKEND_APPROVED_COMMIT": SHA,
            "TESTS_APPROVED_COMMIT": SHA, "RAILWAY_PROJECT_ID": "test-project",
            "RAILWAY_SERVICE": "test-service", "RAILWAY_ENVIRONMENT": "test",
            "PUBLIC_URL": "https://example.test",
        }
        for context in (patch.object(deploy, "ROOT", self.root), patch.dict(os.environ, self.env)):
            context.start()
            self.addCleanup(context.stop)

    def test_missing_domain_approval_prevents_upload(self):
        with patch.dict(os.environ, {"DOMAIN_APPROVED_COMMIT": ""}), patch.object(deploy.subprocess, "run") as upload:
            with self.assertRaisesRegex(SystemExit, "DOMAIN_APPROVED_COMMIT"):
                deploy.main()
            upload.assert_not_called()

    def test_missing_suite_approval_prevents_upload(self):
        with patch.dict(os.environ, {"BACKEND_APPROVED_COMMIT": ""}), patch.object(deploy.subprocess, "run") as upload:
            with self.assertRaisesRegex(SystemExit, "BACKEND_APPROVED_COMMIT"):
                deploy.main()
            upload.assert_not_called()

    def test_different_frontend_commit_prevents_upload(self):
        with patch.dict(os.environ, {"TESTS_APPROVED_COMMIT": "b" * 40}), patch.object(deploy.subprocess, "run") as upload:
            with self.assertRaisesRegex(SystemExit, "TESTS_APPROVED_COMMIT"):
                deploy.main()
            upload.assert_not_called()

    def test_changed_checkout_prevents_upload(self):
        for actual, changed in (("b" * 40, ""), (SHA, " M backend/app.py")):
            with self.subTest(actual=actual, changed=changed), patch.object(deploy.subprocess, "check_output", side_effect=[actual, changed]), patch.object(deploy.subprocess, "run") as upload:
                with self.assertRaisesRegex(SystemExit, "checkout diferente"):
                    deploy.main()
                upload.assert_not_called()

    def test_old_public_version_does_not_approve_deploy(self):
        with patch.object(deploy.subprocess, "check_output", side_effect=[SHA, ""]), patch.object(deploy.subprocess, "run"), patch.object(deploy, "urlopen", side_effect=lambda *args, **kwargs: BytesIO(json.dumps({"commit": "b" * 40}).encode())), patch.object(deploy.time, "sleep"):
            with self.assertRaisesRegex(SystemExit, "não passou"):
                deploy.main()
        self.assertFalse(self.marker.exists())

    def test_success_checks_version_health_and_interface(self):
        responses = [BytesIO(json.dumps({"commit": SHA}).encode()), BytesIO(b'{"status":"ok"}'), BytesIO(b'<form id="form-iniciar">')]

        def upload(*args, **kwargs):
            self.assertEqual(json.loads(self.marker.read_text()), {"commit": SHA})
            self.assertIn("--ci", args[0])

        with patch.object(deploy.subprocess, "check_output", side_effect=[SHA, ""]), patch.object(deploy.subprocess, "run", side_effect=upload), patch.object(deploy, "urlopen", side_effect=responses) as public:
            deploy.main()
            self.assertEqual(public.call_count, 3)
        self.assertFalse(self.marker.exists())

    def test_existing_marker_is_preserved_and_blocks_upload(self):
        self.marker.write_text("existing build")
        with patch.object(deploy.subprocess, "check_output", side_effect=[SHA, ""]), patch.object(deploy.subprocess, "run") as upload:
            with self.assertRaisesRegex(SystemExit, "preexistente"):
                deploy.main()
            upload.assert_not_called()
        self.assertEqual(self.marker.read_text(), "existing build")

    def test_railway_failure_removes_marker_and_fails_build(self):
        with patch.object(deploy.subprocess, "check_output", side_effect=[SHA, ""]), patch.object(deploy.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "railway")), patch.object(deploy, "urlopen") as public:
            with self.assertRaises(subprocess.CalledProcessError):
                deploy.main()
            public.assert_not_called()
        self.assertFalse(self.marker.exists())


if __name__ == "__main__":
    unittest.main()

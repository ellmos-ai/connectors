# -*- coding: utf-8 -*-
"""Repository hygiene checks for local credential and runtime artefacts."""

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


@unittest.skipUnless((ROOT / ".git").exists(), "git metadata required")
class RepositoryHygieneTests(unittest.TestCase):
    def test_local_secret_and_runtime_files_are_ignored(self):
        samples = [
            ".env",
            ".env.local",
            ".envrc",
            "local.env",
            ".npmrc",
            ".pypirc",
            "secrets.json",
            "api.secret.json",
            "credentials.json",
            "service_credentials.json",
            "token.txt",
            "bot_token.txt",
            "tokens.json",
            "api_key.txt",
            "api_keys.json",
            "recovery_codes.txt",
            "mfa_recovery_codes.txt",
            "id_rsa",
            "id_ed25519",
            "private.key",
            "client.pem",
            "bundle.p12",
            "cert.crt",
            "local.sqlite",
            "connectors.db",
            "connectors.db-wal",
            "data/messages.json",
        ]
        result = _git("check-ignore", *samples)
        self.assertEqual(result.returncode, 0, result.stderr)
        ignored = set(result.stdout.splitlines())
        self.assertEqual(set(samples), ignored)

    def test_example_env_files_remain_trackable(self):
        result = _git("check-ignore", ".env.example", ".env.sample")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()

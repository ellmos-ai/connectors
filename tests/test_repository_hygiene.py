# -*- coding: utf-8 -*-
"""Repository hygiene, security contracts, dependency boundaries, and metadata parity checks."""

import fnmatch
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Ensure connectors package is importable
sys.path.insert(0, str(ROOT))
import connectors  # noqa: E402
from connectors.base import ConnectorConfig  # noqa: E402
from connectors import create_connector, SUPPORTED_TYPES  # noqa: E402


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


def _load_gitignore_patterns():
    gitignore_path = ROOT / ".gitignore"
    if not gitignore_path.exists():
        return []
    patterns = []
    for line in gitignore_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def _is_path_ignored(sample: str, patterns: list[str]) -> bool:
    # Check negation rules and normal patterns
    ignored = False
    for pat in patterns:
        if pat.startswith("!"):
            neg_pat = pat[1:]
            if fnmatch.fnmatch(sample, neg_pat) or fnmatch.fnmatch(os.path.basename(sample), neg_pat):
                ignored = False
        else:
            clean_pat = pat.rstrip("/")
            if (
                fnmatch.fnmatch(sample, clean_pat)
                or fnmatch.fnmatch(os.path.basename(sample), clean_pat)
                or fnmatch.fnmatch(sample, f"*{clean_pat}*")
            ):
                ignored = True
    return ignored


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
            "private" + ".key",
            "client.pem",
            "bundle.p12",
            "cert.crt",
            "local.sqlite",
            "connectors.db",
            "connectors.db-wal",
            "data/messages.json",
        ]
        if (ROOT / ".git").exists():
            result = _git("check-ignore", *samples)
            self.assertEqual(result.returncode, 0, result.stderr)
            ignored = set(result.stdout.splitlines())
            self.assertEqual(set(samples), ignored)
        else:
            patterns = _load_gitignore_patterns()
            for sample in samples:
                self.assertTrue(_is_path_ignored(sample, patterns), f"Sample {sample} should be ignored")

    def test_example_env_files_remain_trackable(self):
        if (ROOT / ".git").exists():
            result = _git("check-ignore", ".env.example", ".env.sample")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "")
        else:
            patterns = _load_gitignore_patterns()
            self.assertFalse(_is_path_ignored(".env.example", patterns))
            self.assertFalse(_is_path_ignored(".env.sample", patterns))

    def test_sync_conflicts_and_locks_are_ignored(self):
        conflict_samples = [
            "LOCK.txt",
            "LOCK.permissions.txt",
            "base-ASUS-GEI.py",
            "signal_connector-WORKSTATION-LG.py",
            "config.sync-conflict-20260825.json",
            "messages.conflict",
            "module-conflict-copy.py",
        ]
        if (ROOT / ".git").exists():
            result = _git("check-ignore", *conflict_samples)
            self.assertEqual(result.returncode, 0, result.stderr)
            ignored = set(result.stdout.splitlines())
            self.assertEqual(set(conflict_samples), ignored)
        else:
            patterns = _load_gitignore_patterns()
            for sample in conflict_samples:
                self.assertTrue(_is_path_ignored(sample, patterns), f"Conflict file {sample} should be ignored")


class MetadataAndSecurityContractTests(unittest.TestCase):
    def test_version_parity_across_manifests(self):
        version_file = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        pyproject_content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r'version\s*=\s*"([^"]+)"', pyproject_content)
        self.assertIsNotNone(match, "pyproject.toml must declare version")
        pyproject_version = match.group(1)

        self.assertEqual(connectors.__version__, "1.1.0")
        self.assertEqual(version_file, "1.1.0")
        self.assertEqual(pyproject_version, "1.1.0")

    def test_zero_external_runtime_dependencies(self):
        pyproject_content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r'dependencies\s*=\s*\[(.*?)\]', pyproject_content, re.DOTALL)
        self.assertIsNotNone(match, "dependencies array must exist in pyproject.toml")
        deps_block = match.group(1).strip()
        self.assertEqual(deps_block, "", "Core runtime dependencies must be empty (zero-dependency stdlib architecture)")

    def test_all_connectors_repr_masking(self):
        secret_value = "SECRET_SUPER_TOKEN_99999"
        for ctype in SUPPORTED_TYPES:
            cfg = ConnectorConfig(
                name=f"test_{ctype}",
                connector_type=ctype,
                endpoint="http://127.0.0.1:8123" if ctype in ("homeassistant", "webhook") else "",
                auth_type="api_key",
                auth_config={
                    "bot_token": secret_value,
                    "api_token": secret_value,
                    "access_token": secret_value,
                    "bearer_token": secret_value,
                    "phone_number": "+49123456789",
                    "phone_number_id": "123456",
                },
            )
            # Verify config repr hides secrets
            self.assertNotIn(secret_value, repr(cfg), f"ConnectorConfig repr for {ctype} leaked secret")

            # Verify connector instance repr hides secrets
            conn = create_connector(cfg)
            self.assertNotIn(secret_value, repr(conn), f"Connector instance repr for {ctype} leaked secret")

    def test_third_party_licenses_inventory_exists(self):
        license_inv = ROOT / "THIRD_PARTY_LICENSES.md"
        self.assertTrue(license_inv.exists(), "THIRD_PARTY_LICENSES.md must exist")
        content = license_inv.read_text(encoding="utf-8")
        self.assertIn("MIT License", content)
        self.assertIn("PSF License", content)
        self.assertIn("pyyaml", content)
        self.assertIn("pytest", content)
        self.assertIn("signal-cli", content)

    def test_security_policy_sla_and_bilingual_coverage(self):
        sec_file = ROOT / "SECURITY.md"
        self.assertTrue(sec_file.exists(), "SECURITY.md must exist")
        content = sec_file.read_text(encoding="utf-8")
        self.assertIn("1.1.x", content)
        self.assertIn("Security Policy", content)
        self.assertIn("Sicherheitsrichtlinie", content)
        self.assertIn("48 hours", content)
        self.assertIn("Zero Runtime Secret Persistence", content)

    def test_utf8_encoding_and_german_umlauts(self):
        files_to_check = [
            ROOT / "README.md",
            ROOT / "README_de.md",
            ROOT / "SECURITY.md",
            ROOT / "THIRD_PARTY_LICENSES.md",
            ROOT / "llms.txt",
            ROOT / "CHANGELOG.md",
            ROOT / "base.py",
            ROOT / "telegram_connector.py",
            ROOT / "discord_connector.py",
            ROOT / "signal_connector.py",
            ROOT / "whatsapp_connector.py",
            ROOT / "homeassistant_connector.py",
            ROOT / "webhook_connector.py",
        ]
        for fp in files_to_check:
            if not fp.exists():
                continue
            text = fp.read_text(encoding="utf-8")
            # Verify no replacement character (mojibake)
            self.assertNotIn("\ufffd", text, f"Mojibake character found in {fp.name}")

        # Check genuine German umlauts in README_de.md
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")
        for char in ("ä", "ö", "ü", "ß"):
            self.assertIn(char, readme_de, f"Expected German character {char} in README_de.md")


if __name__ == "__main__":
    unittest.main()

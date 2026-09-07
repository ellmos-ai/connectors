# -*- coding: utf-8 -*-
"""Contract tests for documentation, metadata, discoverability, and bilingual parity."""

import re
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

# Ensure connectors package is importable
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class MetadataAndDiscoverabilityContractTests(unittest.TestCase):
    """Verifies that documentation, metadata, and design contracts are strictly fulfilled."""

    def test_readme_and_de_existence(self):
        readme_en = ROOT / "README.md"
        readme_de = ROOT / "README_de.md"
        self.assertTrue(readme_en.exists(), "README.md must exist")
        self.assertTrue(readme_de.exists(), "README_de.md must exist")
        self.assertGreater(readme_en.stat().st_size, 4000, "README.md must be comprehensive (>4000 bytes)")
        self.assertGreater(readme_de.stat().st_size, 4000, "README_de.md must be comprehensive (>4000 bytes)")

    def test_banner_assets_and_accessibility(self):
        banner_png = ROOT / "assets" / "banner.png"
        banner_svg = ROOT / "assets" / "banner.svg"
        self.assertTrue(banner_png.exists(), "assets/banner.png must exist")
        self.assertTrue(banner_svg.exists(), "assets/banner.svg must exist")

        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

        self.assertIn('src="assets/banner.png"', readme_en)
        self.assertIn('alt="connectors Banner"', readme_en)
        self.assertIn('src="assets/banner.png"', readme_de)
        self.assertIn('alt="connectors Banner"', readme_de)

    def test_quick_navigation_anchors(self):
        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

        self.assertIn("## Quick Navigation", readme_en)
        self.assertIn("## Schnellnavigation", readme_de)

        anchors_en = re.findall(r"\[([^\]]+)\]\(#([^\)]+)\)", readme_en)
        anchors_de = re.findall(r"\[([^\]]+)\]\(#([^\)]+)\)", readme_de)

        self.assertGreaterEqual(len(anchors_en), 10, "README.md must have at least 10 quick navigation anchor links")
        self.assertGreaterEqual(len(anchors_de), 10, "README_de.md must have at least 10 quick navigation anchor links")

        # Verify key anchors exist in English
        expected_anchors_en = [
            "key-features",
            "system-architecture",
            "interactive-messaging--polling-lifecycle",
            "supported-connectors--status",
            "governance--safety-invariants",
            "quick-start",
            "secret-management--zero-leakage",
            "threaded-polling--event-callbacks",
            "sibling-ecosystem--partner-repositories",
            "security-policy--vulnerability-reporting",
        ]
        for anchor in expected_anchors_en:
            self.assertIn(f"(#{anchor})", readme_en, f"Anchor #{anchor} missing in README.md")

    def test_bilingual_readme_parity(self):
        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

        # Cross-linking
        self.assertIn("[🇩🇪 DE](README_de.md)", readme_en)
        self.assertIn("[🇬🇧 EN](README.md)", readme_de)

        # Ensure both contain identical code-fence counts
        self.assertEqual(
            readme_en.count("```python"),
            readme_de.count("```python"),
            "Both READMEs must have identical python code snippet counts"
        )
        self.assertEqual(
            readme_en.count("```bash"),
            readme_de.count("```bash"),
            "Both READMEs must have identical bash code snippet counts"
        )
        self.assertEqual(
            readme_en.count("```mermaid"),
            readme_de.count("```mermaid"),
            "Both READMEs must have identical mermaid diagram counts"
        )

    def test_mermaid_diagrams_syntax(self):
        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

        for text, name in [(readme_en, "README.md"), (readme_de, "README_de.md")]:
            self.assertIn("```mermaid\nflowchart TD", text, f"Missing flowchart TD in {name}")
            self.assertIn("```mermaid\nsequenceDiagram", text, f"Missing sequenceDiagram in {name}")
            self.assertIn("BaseConnector", text, f"Missing BaseConnector in {name}")
            self.assertIn("create_connector", text, f"Missing create_connector in {name}")
            self.assertIn("poll_threaded", text, f"Missing poll_threaded in {name}")

    def test_governance_and_safety_invariants_matrix(self):
        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

        self.assertIn("Zero Runtime Dependencies", readme_en)
        self.assertIn("Zero Secret Persistence", readme_en)
        self.assertIn("Masked String Representation", readme_en)
        self.assertIn("Shell Injection Immune", readme_en)
        self.assertIn("Non-Blocking Execution", readme_en)
        self.assertIn("Fail-Closed Error Handling", readme_en)

        self.assertIn("Null Laufzeit-Abhängigkeiten", readme_de)
        self.assertIn("Null Geheimnis-Persistierung", readme_de)
        self.assertIn("Maskierte String-Darstellung", readme_de)
        self.assertIn("Immun gegen Shell-Injection", readme_de)
        self.assertIn("Nicht-blockierende Ausführung", readme_de)
        self.assertIn("Fail-Closed Fehlerbehandlung", readme_de)

    def test_sibling_ecosystem_and_urls(self):
        readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

        required_siblings = [
            "ellmos-ai/bach",
            "ellmos-ai/usmc",
            "ellmos-ai/clutch",
            "ellmos-ai/companion-for-agy",
            "ellmos-ai/system-gap-master",
            "dev-bricks/lock-master",
            "dev-bricks/ticket-master",
            "dev-bricks/automation-master",
            "dev-bricks/safe-start-for-codex",
            "file-bricks/CloudLockFixer",
            "open-bricks/.github",
        ]
        for sibling in required_siblings:
            self.assertIn(sibling, readme_en, f"Missing sibling {sibling} in README.md")
            self.assertIn(sibling, readme_de, f"Missing sibling {sibling} in README_de.md")

    def test_security_policy_integrity(self):
        sec_path = ROOT / "SECURITY.md"
        self.assertTrue(sec_path.exists(), "SECURITY.md must exist")
        sec_text = sec_path.read_text(encoding="utf-8")

        self.assertIn("1.1.x", sec_text)
        self.assertIn("48 hours", sec_text)
        self.assertIn("5 business days", sec_text)
        self.assertIn("Zero Runtime Secret Persistence", sec_text)
        self.assertIn("field(repr=False)", sec_text)
        self.assertIn("https://github.com/ellmos-ai/connectors/security/advisories/new", sec_text)

    def test_llms_txt_structure_and_timestamp(self):
        llms_path = ROOT / "llms.txt"
        self.assertTrue(llms_path.exists(), "llms.txt must exist")
        llms_text = llms_path.read_text(encoding="utf-8")

        self.assertIn("# connectors — LLM-Kontext", llms_text)
        self.assertIn("## Last-checked: 2026-09-07", llms_text)
        self.assertIn("BaseConnector", llms_text)
        self.assertIn("create_connector", llms_text)
        self.assertIn("SecretAdapter", llms_text)
        self.assertIn("field(repr=False)", llms_text)
        self.assertIn("ellmos-ai/bach", llms_text)

    def test_pyproject_metadata_and_urls(self):
        pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('name = "ellmos-connectors"', pyproject_text)
        self.assertIn('version = "1.1.0"', pyproject_text)
        self.assertIn('dependencies = []', pyproject_text)
        self.assertIn('"Parent Org" = "https://github.com/ellmos-ai"', pyproject_text)
        self.assertIn('"Umbrella Ecosystem" = "https://github.com/open-bricks"', pyproject_text)
        self.assertIn('[tool.ruff]', pyproject_text)

    def test_utf8_encoding_and_german_umlauts(self):
        readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")
        self.assertNotIn("\ufffd", readme_de, "README_de.md must not contain replacement characters (mojibake)")
        for char in ("ä", "ö", "ü", "ß"):
            self.assertIn(char, readme_de, f"Expected German umlaut/character '{char}' in README_de.md")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connector Setup Wizard — Standalone
=====================================

Interaktiver Wizard zum Erstellen neuer Connector-Dateien aus Templates.
Läuft vollständig ohne Framework oder Datenbank.

Verwendung:
    python -m connectors.templates.setup_wizard

Features:
    - Template-basierte Connector-Erstellung via YAML-Konfiguration
    - Interaktive Konfiguration (Text, Secret, Choice)
    - Automatische Code-Generierung aus connector_template.py
    - Keine Datenbank-Abhängigkeit (BACH-freie Standalone-Version)

Framework-Integration (optional):
    Subklassen können register_connector() überschreiben, um Connectors
    in einem eigenen Store (DB, JSON, etc.) zu registrieren.

Benötigt: pyyaml (pip install pyyaml)

MIT License — siehe LICENSE
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


class SetupWizard:
    """Interaktiver Setup-Wizard für neue Connectors (standalone)."""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path(__file__).parent.parent.parent
        self.templates_dir = Path(__file__).parent
        self.connectors_dir = Path(__file__).parent.parent

    def run(self) -> None:
        """Hauptschleife des Wizards."""
        print("=" * 60)
        print("Connector Setup Wizard")
        print("=" * 60)
        print()

        template_name = self.select_template()
        if not template_name:
            print("\n[Abbruch] Kein Template ausgewählt.")
            return

        config = self.load_template(template_name)
        if not config:
            print(f"\n[Fehler] Template '{template_name}' konnte nicht geladen werden.")
            return

        print(f"\n Template: {config.get('connector_display_name', template_name)}")
        print(f" Beschreibung: {config.get('connector_description', 'N/A').strip()}")
        print()

        user_config = self.gather_configuration(config)
        if not user_config:
            print("\n[Abbruch] Konfiguration abgebrochen.")
            return

        connector_file = self.generate_connector(config, user_config)
        if not connector_file:
            print("\n[Fehler] Connector-Datei konnte nicht generiert werden.")
            return

        print(f"\n[OK] Connector-Datei erstellt: {connector_file}")

        # Framework-Integration: register_connector() überschreiben
        if self.confirm("Connector registrieren? (Framework-spezifisch)"):
            success = self.register_connector(config, user_config)
            if success:
                print(f"[OK] Connector '{user_config['instance_name']}' registriert.")
            else:
                print("[Info] Registrierung übersprungen (standalone mode).")
                print(f"  → Connector-Datei manuell einbinden:")
                print(f"    from connectors.{config.get('connector_module', 'my_connector')} "
                      f"import {config.get('connector_name', 'My')}Connector")

        print("\n" + "=" * 60)
        print("Setup abgeschlossen!")
        print("=" * 60)

    def select_template(self) -> Optional[str]:
        """Template auswählen."""
        templates = self.list_templates()
        if not templates:
            print("[Fehler] Keine Templates gefunden.")
            return None

        print("Verfügbare Templates:")
        print()
        for i, tmpl in enumerate(templates, 1):
            print(f"  {i}. {tmpl}")
        print()

        while True:
            choice = input("Template wählen (Nummer oder Name): ").strip()
            if not choice:
                return None
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(templates):
                    return templates[idx]
            elif choice in templates:
                return choice
            print("[Fehler] Ungültige Auswahl. Bitte erneut versuchen.")

    def list_templates(self) -> List[str]:
        """Alle verfügbaren Templates auflisten."""
        if not self.templates_dir.exists():
            return []
        templates = []
        for f in self.templates_dir.glob("*_template.yaml"):
            templates.append(f.stem.replace("_template", ""))
        return sorted(templates)

    def load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Template-Konfiguration aus YAML laden."""
        try:
            import yaml
        except ImportError:
            print("[Fehler] PyYAML nicht installiert. Bitte: pip install pyyaml")
            return None

        template_file = self.templates_dir / f"{template_name}_template.yaml"
        if not template_file.exists():
            return None
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[Fehler] Template konnte nicht geladen werden: {e}")
            return None

    def gather_configuration(self, template: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Benutzereingaben sammeln."""
        print("\nKonfiguration:")
        print("-" * 60)

        user_config: Dict[str, Any] = {
            "auth_config": {},
            "options": {},
            "instance_name": "",
        }

        print()
        instance_name = input(
            f"Instanz-Name (z.B. {template.get('connector_instance_name', 'main')}): "
        ).strip()
        if not instance_name:
            instance_name = template.get(
                "connector_instance_name",
                f"{template.get('connector_type', 'connector')}_main",
            )
        user_config["instance_name"] = instance_name

        for q in template.get("setup_questions", []):
            name = q["name"]
            prompt = q["prompt"]
            qtype = q.get("type", "text")
            required = q.get("required", False)
            storage = q.get("storage", "options")
            default = q.get("default", "")

            print()
            if qtype == "secret":
                print(f"{prompt} (wird nicht angezeigt):")
                value = self._input_secret()
            elif qtype == "choice":
                choices = q.get("choices", [])
                print(f"{prompt}")
                for i, c in enumerate(choices, 1):
                    marker = " (default)" if c == default else ""
                    print(f"  {i}. {c}{marker}")
                value = self._input_choice(choices, default)
            else:
                default_text = f" (default: {default})" if default else ""
                value = input(f"{prompt}{default_text}: ").strip() or default

            if required and not value:
                print("[Fehler] Pflichtfeld darf nicht leer sein.")
                return None

            if storage == "auth_config":
                user_config["auth_config"][name] = value
            else:
                user_config["options"][name] = value

        print()
        print("-" * 60)
        print("Konfiguration abgeschlossen.")
        return user_config

    def generate_connector(self, template: Dict[str, Any],
                           user_config: Dict[str, Any]) -> Optional[Path]:
        """Connector-Datei aus Template generieren."""
        template_file = self.templates_dir / "connector_template.py"
        if not template_file.exists():
            print("[Fehler] connector_template.py nicht gefunden.")
            return None

        try:
            with open(template_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"[Fehler] Template-Datei konnte nicht gelesen werden: {e}")
            return None

        replacements = {
            "{{CONNECTOR_NAME}}": template.get("connector_name", "My"),
            "{{CONNECTOR_TYPE}}": template.get("connector_type", "my"),
            "{{CONNECTOR_DISPLAY_NAME}}": template.get("connector_display_name", "My Connector"),
            "{{CONNECTOR_DESCRIPTION}}": template.get("connector_description", ""),
            "{{CONNECTOR_MODULE}}": template.get("connector_module", "my_connector"),
            "{{CONNECTOR_INSTANCE_NAME}}": user_config["instance_name"],
            "{{RECIPIENT_EXAMPLE}}": template.get("recipient_example", "recipient_id"),
            "{{AUTH_TYPE}}": template.get("auth_type", "api_key"),
            "{{AUTH_CONFIG_EXAMPLE}}": template.get("auth_config_example", "{}"),
            "{{OPTIONS_EXAMPLE}}": template.get("options_example", "{}"),
            "{{API_BASE_COMMENT}}": template.get("api_base_comment", ""),
            "{{API_BASE_URL}}": template.get("api_base_url", ""),
            "{{INIT_VARIABLES}}": self._indent(template.get("init_variables", ""), 8),
            "{{CONNECT_VALIDATION}}": self._indent(template.get("connect_validation", "pass"), 8),
            "{{CONNECT_IMPLEMENTATION}}": self._indent(template.get("connect_implementation", "pass"), 12),
            "{{SEND_MESSAGE_IMPLEMENTATION}}": self._indent(template.get("send_message_implementation", "pass"), 12),
            "{{GET_MESSAGES_IMPLEMENTATION}}": self._indent(template.get("get_messages_implementation", "pass"), 12),
            "{{PARSE_MESSAGES_IMPLEMENTATION}}": self._indent(template.get("parse_messages_implementation", "pass"), 12),
            "{{HELPER_METHODS}}": self._indent(template.get("helper_methods", "pass"), 4),
        }

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        module_name = template.get("connector_module", "my_connector")
        if not module_name.endswith(".py"):
            module_name += ".py"
        output_file = self.connectors_dir / module_name

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            return output_file
        except Exception as e:
            print(f"[Fehler] Datei konnte nicht geschrieben werden: {e}")
            return None

    def register_connector(self, template: Dict[str, Any],
                           user_config: Dict[str, Any]) -> bool:
        """Optionale Registrierung — in Standalone-Version nicht implementiert.

        Subklassen können diese Methode überschreiben, um Connectors
        in einem Framework-eigenen Store zu registrieren.

        Beispiel (BACH):
            def register_connector(self, template, user_config):
                import sqlite3
                # ... Eintrag in bach.db ...
                return True
        """
        return False

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _indent(self, text: str, spaces: int) -> str:
        if not text:
            return ""
        indent = " " * spaces
        lines = text.strip().split("\n")
        return "\n".join(indent + line if line.strip() else "" for line in lines)

    def _input_secret(self) -> str:
        try:
            import getpass
            return getpass.getpass("  > ")
        except Exception:
            return input("  > ")

    def _input_choice(self, choices: List[str], default: str = "") -> str:
        while True:
            choice = input("  Auswahl (Nummer oder Text): ").strip()
            if not choice and default:
                return default
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
            elif choice in choices:
                return choice
            print("  [Fehler] Ungültige Auswahl.")

    def confirm(self, prompt: str, default: bool = True) -> bool:
        suffix = " [J/n]" if default else " [j/N]"
        while True:
            answer = input(prompt + suffix + ": ").strip().lower()
            if not answer:
                return default
            if answer in ("j", "ja", "y", "yes"):
                return True
            if answer in ("n", "nein", "no"):
                return False
            print("[Fehler] Bitte 'j' oder 'n' eingeben.")


def main() -> None:
    """Einstiegspunkt für python -m connectors.templates.setup_wizard"""
    wizard = SetupWizard()
    try:
        wizard.run()
    except KeyboardInterrupt:
        print("\n\n[Abbruch] Setup abgebrochen.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[Fehler] Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

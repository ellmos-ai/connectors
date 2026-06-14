# -*- coding: utf-8 -*-
"""
Connector Template System
=========================

Interaktives Template-System zur Erstellung neuer Connectors.

Komponenten:
- connector_template.py: Basis-Template mit Platzhaltern
- setup_wizard.py:       Interaktiver CLI-Wizard (standalone, kein Framework)
- *_template.yaml:       Template-Konfigurationen (Telegram, WhatsApp)

Verwendung:
    python -m connectors.templates.setup_wizard

MIT License — siehe LICENSE
"""

__version__ = "1.0.0"
__all__ = ["setup_wizard"]

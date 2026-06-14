[EN](README.md) | **DE** | [ES](README_es.md) | [JA](README_ja.md) | [RU](README_ru.md) | [ZH](README_zh-Hans.md)

# connectors — Deutsch

Standalone Python-Modul für Messaging-Connectoren: Telegram, Discord, Signal,
WhatsApp, Home Assistant und generische HTTP-Webhooks.

Aus [BACH](../../.AI/.OS/BACH/) extrahiert (`.OS/BACH/system/connectors/`),
vollständig entkoppelt. Kein Framework erforderlich. Keine zwingenden externen
Abhängigkeiten (nur Python stdlib).

> **Status:** v1.0.0 — funktionsfähig, noch nicht als separates Paket veröffentlicht.
> Offene Punkte: [TODO.md](TODO.md)

## Unterstützte Connectoren

| Connector       | Protokoll             | Quelle                     | Status  |
|-----------------|-----------------------|----------------------------|---------|
| `telegram`      | Telegram Bot API      | Portiert aus BACH          | Stabil  |
| `discord`       | Discord Bot + Webhook | Portiert aus BACH          | Stabil  |
| `signal`        | signal-cli            | Portiert aus BACH          | Stabil  |
| `whatsapp`      | WhatsApp Business API | Portiert aus BACH          | Stabil  |
| `homeassistant` | Home Assistant REST   | Portiert aus BACH          | Stabil  |
| `webhook`       | Generischer HTTP POST | Neu (kein BACH-Äquivalent) | Stub    |

Der `webhook`-Connector ist eine **Neuentwicklung** — er war in früheren
Planungsdokumenten erwähnt, existierte aber nicht in BACH. Er ist als
ausgehender HTTP-POST-Connector funktionsfähig und klar als Stub/Basis markiert.

## Schnellstart

```python
import os
from connectors import create_connector, ConnectorConfig

# Telegram-Beispiel
config = ConnectorConfig(
    name="mein_bot",
    connector_type="telegram",
    auth_config={"bot_token": os.environ["TG_BOT_TOKEN"]},
    options={"owner_chat_id": ""},   # optional: nur Nachrichten von dieser Chat-ID
)
conn = create_connector(config)
if conn.connect():
    conn.send_message("CHAT_ID", "Hallo!")

# Nachrichten empfangen (Polling)
thread, stop = conn.poll_threaded(on_message=lambda m: print(m.content))
# ... später:
stop.set()
```

## Secrets

**Tokens niemals hardcoden.** Empfohlene Vorgehensweise:

```python
# 1. Umgebungsvariablen (einfachste Lösung)
auth_config={"bot_token": os.environ["TG_BOT_TOKEN"]}

# 2. python-dotenv + .env-Datei
from dotenv import load_dotenv; load_dotenv()
auth_config={"bot_token": os.getenv("TG_BOT_TOKEN")}

# 3. SecretAdapter (Framework-Integration, z.B. BACH)
from connectors.base import SecretAdapter

class MeinAdapter(SecretAdapter):
    def get_secret(self, key: str) -> str:
        return mein_vault.get(key, "")

conn = create_connector(config, secret_adapter=MeinAdapter())
```

## Eigenen Connector erstellen

Interaktiver Wizard:

```bash
pip install pyyaml   # nur für den Wizard benötigt
python -m connectors.templates.setup_wizard
```

Oder manuell via `templates/connector_template.py`:

1. `connector_template.py` nach `mein_connector.py` kopieren
2. Alle `{{PLATZHALTER}}` ersetzen
3. `connect()`, `disconnect()`, `send_message()`, `get_messages()` implementieren
4. In `__init__.py` → `_CONNECTOR_MAP` registrieren

## BACH-Integration (optional)

Um dieses Modul innerhalb von BACH zu nutzen, `SecretAdapter` implementieren:

```python
from connectors.base import SecretAdapter

class BachSecretAdapter(SecretAdapter):
    def get_secret(self, key: str) -> str:
        try:
            from hub.secrets_handler import SecretsHandler
            return SecretsHandler().get_secret(key) or ""
        except ImportError:
            return ""
```

BACH kann dann optional seine `connectors/`-Schicht auf dieses Modul umstellen.
Siehe [BACH-REIMPORT-NOTE.md](BACH-REIMPORT-NOTE.md) für die zugehörige Task-Notiz.

## Projektstruktur

```
connectors/
├── __init__.py                  # create_connector() Factory
├── base.py                      # BaseConnector, Message, SecretAdapter
├── telegram_connector.py
├── discord_connector.py
├── signal_connector.py
├── whatsapp_connector.py
├── homeassistant_connector.py
├── webhook_connector.py         # Generischer HTTP (Stub/Basis)
├── templates/
│   ├── connector_template.py    # Template für neue Connectoren
│   ├── setup_wizard.py          # Interaktiver CLI-Wizard (standalone)
│   ├── telegram_template.yaml
│   ├── whatsapp_template.yaml
│   └── notification_template.yaml
├── LICENSE                      # MIT
├── requirements.txt             # pyyaml (nur Wizard), sonst stdlib
├── CHANGELOG.md
├── TODO.md
└── llms.txt
```

## Abhängigkeiten

- **Kern:** Python 3.8+, nur stdlib (`urllib`, `json`, `threading`, `subprocess`)
- **Setup-Wizard:** `pyyaml` (`pip install pyyaml`)
- **signal_connector:** `signal-cli` Binary — https://github.com/AsamK/signal-cli

## Verwandte Projekte

- **lock-master** (https://github.com/dev-bricks/lock-master) — verwandter Multi-Agenten-Baustein
- **ticket-master** (https://github.com/dev-bricks/ticket-master) — verwandter Multi-Agenten-Baustein

## Verwandte Module

- **USMC** (`.MODULES/usmc`): Agent-zu-Agent Shared Memory
- **clutch** (`.MODULES/clutch`): Model-Routing (Agent-zu-LLM)
- **connectors** (dieses Modul): Messaging (Agent-zu-Mensch)

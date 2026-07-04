# CHANGELOG — connectors

## v1.1.0 (2026-07-04) — Modul-Review

### Fixed

- **Secrets im Klartext in `repr()`:** `ConnectorConfig.auth_config` (Bot-Token,
  API-Keys) erschien im automatisch generierten Dataclass-`repr` — jedes
  `print(config)`/Debug-Log leakte den Token. Jetzt `field(repr=False)`;
  abgesichert durch Repr-Tests.
- **Webhook-Payload konnte ungültiges JSON erzeugen:** `{content}` wurde per
  naivem `str.replace` (nur `"` escaped) eingesetzt — jede mehrzeilige
  Nachricht erzeugte ein defektes JSON-String-Literal, der HTTP-200 des
  Empfängers täuschte trotzdem Erfolg vor. Jetzt JSON-sicheres Escaping via
  `json.dumps` (deckt `\\`, Zeilenumbrüche, Control-Chars, Umlaute ab).
- **`attachments` wurden von 5 Connectoren still verschluckt:** `send_message()`
  akzeptierte den Parameter laut Kontrakt, ignorierte ihn aber (nur Signal
  sendet Anhänge wirklich) und meldete `True` — stiller Datenverlust. Jetzt
  laute stderr-Warnung „NICHT gesendet" über gemeinsamen Base-Helper
  (`_warn_attachments_unsupported`); echte Attachment-Unterstützung pro
  Kanal bleibt als TODO registriert.
- **Discord/HomeAssistant verschluckten alle HTTP-Fehler:** `_api_call()` gab
  bei 401/403/Rate-Limit still `None` zurück (ununterscheidbar von „keine
  Nachrichten"). Jetzt stderr-Diagnose analog Telegram/WhatsApp (ohne Token).

### Tests

- Neue `tests/test_behavior.py` (15 Tests, gemockt, ohne Netz/Secrets):
  `_resolve_secret()`-Matrix, Secret-freie Reprs, Attachments-Vertrag,
  Webhook-JSON-Escaping, Factory (Case-Insensitivity, ValueError,
  Adapter-Durchreichung, Abstraktheit). Erfüllt das offene TODO
  „Unit-Tests für BaseConnector, Factory, Fehlerfälle". Gesamt: 8→23 grün.

## Unreleased

### Technische Hygiene

- `pyproject.toml` ergänzt, damit das Root-Package unabhängig vom Checkout-Namen
  als `connectors` installierbar ist.
- GitHub-Actions-Smoke-Test für installierbare Imports und Compile-Checks
  hinzugefügt.
- `connectors.templates` als Paket markiert, damit der Setup-Wizard im
  gebauten Package erhalten bleibt.
- Import-Smoke-Test robust gegen Temp-Klone gemacht, deren Ordner nicht
  `connectors` heißt.

## v1.0.0 (2026-06-14)

Erstes Release des neutralen, standalone Connector-Moduls.
Extrahiert und entkoppelt aus BACH `.OS/BACH/system/connectors/`.

### Neu

- `base.py`: `BaseConnector`, `ConnectorConfig`, `Message`, `ConnectorStatus`,
  `SecretAdapter` — vollständig BACH-freies Interface
- `telegram_connector.py`: Telegram Bot API (Polling, Long-Polling, Retry-Logik,
  Owner-Filter, Threaded-Polling)
- `discord_connector.py`: Discord Bot + Webhook-Modus (bidirektional / nur senden)
- `signal_connector.py`: Signal via signal-cli (vollständig portiert)
- `whatsapp_connector.py`: WhatsApp Business API (senden + process_webhook)
- `homeassistant_connector.py`: Home Assistant REST-API (States, Services, History)
- `webhook_connector.py`: Generischer HTTP Webhook (Neu — kein BACH-Äquivalent,
  als Basis-Stub markiert)
- `__init__.py`: `create_connector()` Factory mit Lazy-Imports
- `templates/connector_template.py`: Basis-Template für neue Connectors
- `templates/setup_wizard.py`: Standalone Setup-Wizard (DB-freie Version)
- `templates/telegram_template.yaml`: Telegram-Konfiguration
- `templates/whatsapp_template.yaml`: WhatsApp-Konfiguration
- `templates/notification_template.yaml`: Referenz für Notification-only Channels

### Entkopplung von BACH

| BACH-spezifisch                        | Neutral ersetzt durch                          |
|----------------------------------------|------------------------------------------------|
| `from hub.bach_paths import BACH_DB`   | `SecretAdapter`-Interface (optional, DI)       |
| `from hub.secrets_handler import …`    | `SecretAdapter.get_secret()` (überschreibbar)  |
| `from hub._services.voice.voice_stt …` | Entfernt (BACH-intern, kein allg. Interface)   |
| DB-Registrierung im setup_wizard       | `register_connector()` überschreibbar (stub)   |
| `bach.db` / `connections`-Tabelle      | Keine DB-Abhängigkeit im Kern                  |
| BACH-spezifische Thread-Namen          | `connectors-{type}-poll` (neutral)             |

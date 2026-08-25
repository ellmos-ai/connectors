# CHANGELOG — connectors

## Unreleased

### Setup-Wizard templates (2026-08-26)

- Added credential-free, deterministic Signal and Discord templates aligned
  with the real `ConnectorConfig`, secret, endpoint, and options contracts.
- Added explicit Wizard support for `ConnectorConfig.endpoint` questions and
  fixed generated-code indentation so all connector templates compile.
- Added seven offline contract tests; the full suite now passes 39/39 tests
  without platform connections or real credentials.

### Security & Dependency Audit (2026-08-25)

- **Version Parity:** Synchronized `__init__.__version__` to `1.1.0` (matching `pyproject.toml` and `VERSION`).
- **Software & License Inventory (`THIRD_PARTY_LICENSES.md`):** Added comprehensive third-party inventory documenting zero runtime dependencies for the core library, optional `pyyaml` (MIT), `pytest` (MIT), and `signal-cli` (GPL-3.0) external process boundary. Referenced in `pyproject.toml` `license-files`.
- **Security Policy (`SECURITY.md`):** Expanded policy into bilingual German/English document with explicit response SLA (48h acknowledgment, 5 days triage), token masking guarantees, and threat scope.
- **CI Matrix & Concurrency (`.github/workflows/tests.yml`):** Added concurrency group with `cancel-in-progress: true`, multi-OS matrix (`ubuntu-latest`, `windows-latest`, `macos-latest`) across Python 3.10–3.13, and automated execution of the full `pytest` suite.
- **Repository Hygiene & Contract Testsuite (`tests/test_repository_hygiene.py`):** Enhanced test suite with mirror-safe non-git fallback and 7 new security/contract tests covering version parity, zero-dependency invariant, secret masking across all connector classes, sync-conflict gitignore patterns, license inventories, and UTF-8 typography integrity (32/32 tests passed).
- **Documentation & LLM Context:** Updated `llms.txt`, `README.md`, and `README_de.md` badges to 32 tests passed.

### Discoverability & Marketing Audit (2026-07-30)

- Updated `llms.txt` Last-checked timestamp to 2026-07-30.
- Integrated Ecosystem (`ellmos-ai`) & Umbrella (`open-bricks`) Shields.io badges and machine-readable context links in `README.md` and `README_de.md`.
- Verified 25/25 Pytest unit tests (100% green).

### Documentation hygiene

- Synchronised the documented test count with the current 25-test suite.
- Corrected the documented compile command so it excludes both generated build
  artefacts and the intentionally unrendered connector template.
- Updated the supported-version table to the current 1.1.x release line.

### Discoverability & Documentation

- README.md und README_de.md um Shields.io Badges (Python 3.8+, Pytest 25 passed), GFM LLM Note Callout (`> [!NOTE]`) & Mermaid Systemarchitektur-Diagramme erweitert.
- `llms.txt` Metadaten Last-checked auf 2026-07-26 aktualisiert.

### Security

- `.gitignore` um typische lokale Token-, Credential-, Recovery-Code-,
  private Schlüssel-, Zertifikats- und SQLite-Artefakte erweitert; neuer
  Repository-Hygiene-Test hält die Schutzmuster fest.

### Release hygiene

- Final-Gate-Vertrag nachgezogen: explizites `*.pyc`-Muster und eine
  maschinenlesbare STATUS-Tabelle ergänzt; Test-Fixtures bleiben funktional,
  ohne den Secret-Scanner mit Dateinamen zu verwechseln.

### Documentation

- Sprachfassungen ES/JA/RU/ZH auf den Stand der englischen und deutschen
  README nachgezogen: Banner, Lizenz- und Versions-Badge, einheitliche
  Sprachleiste, Abschnitt „Development Smoke Tests"; der Statushinweis stand
  dort noch auf v1.0.0.
- Verweise auf BACH und die Nachbarmodule zeigen jetzt in allen sechs
  Sprachfassungen auf die öffentlichen Repositories statt auf lokale,
  von außen nicht auflösbare Pfade.
- `TODO.md`: Release-Abschnitt an den tatsächlichen Stand angeglichen
  (Repository ist veröffentlicht; offen bleiben Release-Tag und die
  Entscheidung über eine PyPI-Veröffentlichung).
- Modul-Manifest: `visibility` von `public-candidate` auf `public` gesetzt.

### CI/CD & Testing

- `pyproject.toml` um `test`-Extra erweitert (inkl. pytest und pyyaml), um Unit-Tests standardisiert auszuführen.
- `llms.txt` Metadaten Last-checked auf 2026-07-25 aktualisiert.

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

## v1.0.1 (2026-06-25) — Hygiene

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

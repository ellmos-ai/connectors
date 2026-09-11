# CHANGELOG — connectors

## [1.2.1] - 2026-09-11

### Technical Hygiene & CI Hardening — Pfad A (2026-09-11)

- **CI Workflow & Runner Hardening (`.github/workflows/tests.yml`):** Added `timeout-minutes: 15` job guardrail to eliminate runaway runner risks, and standardized test step to `python -m pytest -ra -v`.
- **PEP 621 Standard URLs & Pytest Runner Options (`pyproject.toml`):** Added `"LLM Ready"` machine-readable context URL pointing to `llms.txt`, expanded `[tool.pytest.ini_options]` with `addopts = "-ra -v"`, and strengthened Ruff linting configuration with 7 rule sets (`E`, `F`, `W`, `B`, `SIM`, `C4`, `RUF`).
- **Multi-Host Sync & Lock Exclusions (`.gitignore`):** Hardened gitignore patterns covering multi-host sync conflicts (`* (kopie)*`, `* (copy)*`, `*.sync-temp-*`, `*-ASUS-GEI*`, `*-WORKSTATION*`), multi-agent locks (`LOCK.*`, `uv.lock`, `*.lock`), coverage caches (`.coverage.*`, `coverage/`, `wheelhouse/`), and editor artifacts (`*~`, `*.orig`).
- **Code Modernization & Linter Hygiene:** Sorted `__all__` exports in `__init__.py` (RUF022), optimized dictionary lookups in `base.py` (RUF019), wrapped overlong lines in test suites (E501), combined multiple mock contexts in `tests/test_behavior.py`, and sanitized exception assertions in `tests/test_imports.py` (B011).
- **Security Policy & LLM Context Freshness (`SECURITY.md`, `llms.txt`):** Synchronized audit timestamps to `2026-09-11`, verified `1.2.x` active release support line, and updated verified test baseline.
- **Automated Contract Suite Expansion (`tests/test_metadata.py`, `tests/test_repository_hygiene.py`):** Added contract tests for CI job timeout (`timeout-minutes: 15`), PEP 621 extended URLs (`LLM Ready`), expanded gitignore patterns, and changelog release section.

## [1.2.0] - 2026-09-10

### Added & Enhanced — Pfad B (Marketing, Discoverability & New Connectors)

- **Slack Integration (`SlackConnector`):** Direct support for Slack Bot API (`chat.postMessage`, `conversations.history`) and Incoming Webhooks using zero-dependency `urllib.request`.
- **macOS iMessage Integration (`iMessageConnector`):** Read incoming messages directly from local macOS `chat.db` (SQLite) and dispatch outgoing messages via AppleScript `osascript` subprocess execution. Built-in fail-closed platform guards for non-Darwin environments.
- **Third-Party Attribution (`THIRD_PARTY_LICENSES.md`):** Formal attribution in `THIRD_PARTY_LICENSES.md` for OpenClaw and Hermes Agent multi-channel and agentic messaging abstractions under MIT License.
- **Discoverability & Bilingual Showcase Overhaul (`README.md` & `README_de.md`):** 15+ point bilingual Quick Navigation with 100% anchor parity, dual Mermaid diagrams (`flowchart TD` architecture covering all 8 connectors and `sequenceDiagram` lifecycle with autonumbering), standardized 10 Governance & Runtime Invariants (`INV-LOCAL-01` to `INV-SLA-10`), and expanded 16-repository Sibling Ecosystem.
- **Local Marketing & Personas Strategy (`MARKETING-LOG.txt`):** Codified 4 target personas (Autonomous AI Agent Engineers, Smart Home Automators, Privacy-Conscious SecOps, Multi-Platform Dispatchers), architectural pillars, and roadmap.
- **Packaging & PEP 621 Parity (`pyproject.toml`, `VERSION`, `connectors/__init__.py`):** Synchronized version to `1.2.0`, added `slack` and `imessage` keywords, and added project URLs for `"Third-Party Licenses"` and `"Marketing Log"`.
- **Security Policy (`SECURITY.md`):** Updated to 2026-09-10, verified `1.2.x` active support line, added iMessage and Slack security guarantees, and updated direct maintainer contacts.
- **Automated Contract & Hygiene Suite (`tests/test_metadata.py`, `tests/test_repository_hygiene.py`):** Expanded contract tests covering 15+ quick nav anchors, dual Mermaid diagrams, 10 invariants, 16 sibling repos, version parity across all manifests at `1.2.0`, and full test suite passing 100%.

## [1.1.0] - 2026-09-08

### Technical Hygiene & CI Hardening — Pfad A (2026-09-08)

- **GitHub Actions CI Hardening (`.github/workflows/tests.yml`):** Fixed action versions (`actions/checkout@v4`, `actions/setup-python@v5` with pip caching), integrated Ruff linting gate (`ruff check .`), added cross-platform Python bytecode compilation validation (`python -m compileall -q -x "templates[\\/]connector_template\.py" .`), and maintained full multi-OS matrix (`ubuntu-latest`, `windows-latest`, `macos-latest`) across Python 3.10–3.13 with concurrency `cancel-in-progress: true`.
- **PEP 621 Standard Classifiers & Ecosystem URLs (`pyproject.toml`):** Added standard OS classifiers (`Operating System :: OS Independent`, `Operating System :: Microsoft :: Windows`, `Operating System :: POSIX :: Linux`, `Operating System :: MacOS`), standard project URLs (`Parent Organization` and `Parent Org`), and registered explicit `[tool.pytest.ini_options]`.
- **Sync Conflict & Lock Hardening (`.gitignore`):** Hardened ignore patterns to cover international conflict files (`*-CONFLIT-*`), multi-agent lock patterns (`*.lock`), linter caches (`.ruff_cache/`), temporary artifacts (`*.tmp`, `*.bak`), and test distribution smoke directories (`.wheel-smoke/`).
- **Security Policy & Direct Maintainer Contacts (`SECURITY.md`):** Updated policy to 2026-09-08 with direct security contact channels (`security@open-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com`) alongside GitHub Security Advisories.
- **Contract Test Suite Expansion (`tests/test_metadata.py` & `tests/test_repository_hygiene.py`):** Added automated contract tests validating CI workflow structure, PEP 621 classifier standards, and hardened sync-conflict patterns. Full suite now verified at 52/52 tests passing.
- **Documentation & Machine-Readable Context Sync (`llms.txt`, `README.md`, `README_de.md`):** Updated badges to 52 passed tests, synchronized `Last-checked: 2026-09-08` in `llms.txt`.

### Discoverability, Showcase Design & Parity Audit (2026-09-07)

- **Bilingual Documentation Overhaul (`README.md` & `README_de.md`):** Complete structural and visual refresh featuring 12+ anchor jumps in Quick Navigation, interactive Mermaid architecture (`flowchart TD`) and message/polling lifecycle (`sequenceDiagram`) diagrams, expanded Governance & Safety Invariants matrix, updated Shields.io badges (50 passed tests, Python 3.8+, Zero Dependencies, 48h SLA), and comprehensive Sibling Ecosystem matrix linking 10+ partner repositories across `ellmos-ai`, `dev-bricks`, and `file-bricks`.
- **Automated Metadata & Discoverability Contract Suite (`tests/test_metadata.py`):** Added 11 new automated contract tests enforcing README existence, banner integrity, quick navigation anchors, bilingual code fence parity, mermaid syntax, governance invariants, sibling ecosystem URLs, security policy SLA, `llms.txt` freshness, and UTF-8 encoding without mojibake (full suite now at 50/50 passed tests).
- **Linter & Packaging Configuration (`pyproject.toml`):** Configured `[tool.ruff]` to ensure 100% clean lint checks across codebase, and enriched `[project.urls]` with Documentation, Bug Tracker, Changelog, Security Policy, Parent Org, and Umbrella Ecosystem.
- **LLM Context & Security Sync (`llms.txt` & `SECURITY.md`):** Synchronized `Last-checked: 2026-09-07`, updated architecture, secret handling guarantees, and 50 passed test verification.

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

# TODO — connectors

Status: `v1.1.0 — funktionsfähig, veröffentlicht; CI-/Release-Nachweise offen`

## STATUS

| Category | Status | Notes |
|---|---|---|
| Tests | OK | 39 lokale, netzfreie Tests bestanden. |
| Compile | BLOCKIERT | Lokale Produktionsmodule kompilieren; GitHub-Run 33709473384 scheitert auf Windows beim über-escaped Template-Ausschluss (TASKPLAN 205). |
| Final Gate | NACHWEIS VERALTET | Historischer Check 10 PASS / 0 FAIL / 0 WARN; `RELEASE_GATE.md` fehlt im aktuellen Checkout (TASKPLAN 211). |
| Release | Teilweise | Repository veröffentlicht: https://github.com/ellmos-ai/connectors. Ein Release-Tag `v1.1.0` existiert noch nicht. |

## Review 2026-07-15 (Security-/Dependency-Audit)

- [x] **(mittel)** Repository-Hygiene für lokale Messaging-Credentials gehärtet:
      `.gitignore` schützt jetzt typische Token-, Credential-, Recovery-Code-,
      private Schlüssel-, Zertifikats- und SQLite-Artefakte; Regressionstest ergänzt.
- [x] Security-Audit „keine echten Secrets in Quellen“ durchgeführt: Treffer
      waren Dokumentation, Platzhalter, Header-Erzeugung und Tests, keine realen
      Credentials.

## Review 2026-07-04 (Modul-Review-Loop Lauf 5, frischer Subagent — alle Funde gefixt)

- [x] **(hoch)** `ConnectorConfig.auth_config` leakte Secrets im Dataclass-`repr`
      → `field(repr=False)` + Repr-Tests.
- [x] **(hoch)** Webhook-Payload: naives `str.replace`-Escaping erzeugte bei
      mehrzeiligen Nachrichten ungültiges JSON, HTTP-200 täuschte Erfolg vor
      → JSON-sicheres Escaping via `json.dumps`.
- [x] **(hoch)** `attachments` in 5 Connectoren still verschluckt (True trotz
      nie gesendeter Datei) → gemeinsamer Base-Helper warnt laut auf stderr.
- [x] **(mittel)** Discord/HA `_api_call()` verschluckte HTTP-Fehler ohne Log
      → stderr-Diagnose analog Telegram/WhatsApp.
- [ ] **(Folge)** Echte Attachment-Unterstützung: Telegram `sendDocument`,
      Discord Multipart, WhatsApp Media-API (HA/Webhook: dokumentiert nicht
      unterstützt).

## Offen

### Qualität

- [x] Unit-Tests für `BaseConnector`, `create_connector()` Factory, Fehlerfälle
      (erledigt 2026-07-04: `tests/test_behavior.py`, 15 Tests — Secret-Matrix,
      Reprs, Attachments-Vertrag, Webhook-Escaping, Factory; 8→23 grün)
- [x] Smoke-Tests ohne echte Secrets (Mock-Adapter)
- [x] Import-Verifikation als CI-Schritt (python -c "from connectors import ...")

### Erweiterungen

- [ ] `email_connector.py` (SMTP/IMAP) — Niederpriorität
- [ ] `slack_connector.py` — Niederpriorität
- [ ] `matrix_connector.py` — Zukunftsidee
- [ ] `webhook_connector.py` ausbauen: eingehender Webhook-Server (http.server)
- [x] Templates: [`signal_template.yaml`](templates/signal_template.yaml) hinzugefügt (Wizard-Vorlage für Signal)
- [x] Templates: [`discord_template.yaml`](templates/discord_template.yaml) hinzugefügt

### Integration

- [ ] BACH-Reimport evaluieren (siehe BACH-REIMPORT-NOTE.md)
- [ ] Gardener-Integration prüfen
- [x] Entscheidung: eigenständiges Repository (veröffentlicht als `ellmos-ai/connectors`)

### Release

- [x] `pyproject.toml` erstellen
- [x] Security-Audit (keine echten Secrets in Quellen)
- [x] GitHub-Repo angelegt und veröffentlicht (`ellmos-ai/connectors`)
- [ ] Release-Tag `v1.1.0` setzen — CHANGELOG und Version-Badge führen v1.1.0,
      `gh release list` ist leer; wer die Version sucht, findet keinen Anhaltspunkt.
- [ ] Entscheiden, ob `ellmos-connectors` auf PyPI veröffentlicht wird
      (Name ist frei; derzeit nur Installation aus dem Repository möglich).
- [ ] `RELEASE_GATE.md` nach bestandenem Gate-Check

## Erledigt

### v1.0.0 (2026-06-14)

- [x] base.py entkoppelt (SecretAdapter statt harter BACH-Imports)
- [x] telegram_connector.py portiert (VoiceSTT entfernt, SecretAdapter)
- [x] discord_connector.py portiert
- [x] signal_connector.py portiert
- [x] whatsapp_connector.py portiert
- [x] homeassistant_connector.py portiert
- [x] webhook_connector.py neu erstellt (Stub/Basis, klar markiert)
- [x] __init__.py mit create_connector() Factory
- [x] templates/connector_template.py angepasst (SecretAdapter, neutrale Thread-Namen)
- [x] templates/setup_wizard.py standalone (DB-freie Version, register_connector überschreibbar)
- [x] templates/telegram_template.yaml + whatsapp_template.yaml
- [x] templates/notification_template.yaml (Env-Var basiert)
- [x] LICENSE (MIT), requirements.txt, .gitignore, CHANGELOG.md, llms.txt
- [x] README.md (EN), README_de.md (DE)
- [x] BACH-REIMPORT-NOTE.md (Task-Notiz für BACH)
- [x] Anonymisierungs-Grep: 0 Treffer auf echte Tokens/IDs/Pfade
- [x] webhook-Korrektur: In BACH nicht vorhanden, klar als Neuentwicklung/Stub markiert
- [x] Import-Verifikation: base.py + telegram_connector importierbar ohne BACH

### v1.0.1 Hygiene (2026-06-25)

- [x] Package-Installation über `pyproject.toml`
- [x] GitHub-Actions-Smoke-Test für installierbare Imports
- [x] Temp-Klon-unabhängiger Import-Smoke

## TASKWRITER-Review 2026-09-05

Presentation `66ba31f8-407e-4f59-ac60-35689d418651`; vollständig gelesen
wurden die sechs Sprachfassungen der README, TODO.md, CHANGELOG.md,
SECURITY.md, llms.txt, pyproject.toml, VERSION, BACH-REIMPORT-NOTE.md,
ellmos-module.v2.json, requirements.txt, der GitHub-Workflow sowie die
Paketmodule und Tests. `main` war sauber und exakt auf `origin/main`
(`225a9f5`). Das Repository ist öffentlich; es gab keine offenen Issues oder
Pull Requests.

Lokal liefen 39 Tests, Import-Smoke und produktives `compileall` erfolgreich.
`ruff check .` meldete 50 Befunde (darunter echte ungenutzte Imports und die
bewusst nicht-Python-Platzhalterdatei). Der Live-Workflow-Run `33709473384`
war auf Ubuntu/macOS erfolgreich, aber auf Windows 3.10–3.13 im Compile-Schritt
rot; die 39 Pytest blieben dort grün. Der aktuelle Status oben wurde deshalb
von „Compile/Final Gate OK“ auf belegte Zustände korrigiert.

### Neue, formalisierte Aufgaben

- [ ] **TASKPLAN 205 — Windows-CI-Compile-Gate und deklarierte
      Python-Unterstützung konsistent machen** (high, medium, local). Das
      über-escaped Ausschlussregex verfehlt `templates/connector_template.py`;
      außerdem sind Python 3.8/3.9 deklariert, aber nicht in der Matrix.
- [ ] **TASKPLAN 206 — Lint- und Template-Prüfgrenze reproduzierbar festlegen**
      (medium, medium, local). Produktions-/Testcode, Roh-Platzhalter und
      gerenderte Templates brauchen einen klaren Qualitätsbefehl.
- [ ] **TASKPLAN 207 — Message-Zeitstempel und since-Pagination
      kanalübergreifend vereinheitlichen** (medium, medium, local). Mehrere
      Connectoren liefern naive Zeitstempel oder ignorieren/überladen `since`.
- [ ] **TASKPLAN 208 — Echte Attachment-Unterstützung nur mit kanalgenauen
      Verträgen ergänzen** (medium, large, local). Die vorhandene Warnung bleibt
      korrekt; reale Media-APIs sind ein gesondertes, nicht autonomes Vorhaben.
- [ ] **TASKPLAN 209 — Niedrigprioritäre Connector-Erweiterungen und
      Webhook-Eingang als Roadmap-Entscheidungen formalisieren** (low, large,
      local): E-Mail, Slack, Matrix und eingehender Webhook-Server.
- [ ] **TASKPLAN 210 — BACH- und Gardener-Integration ausschließlich als
      externe Entscheidung vorbereiten** (medium, special, local). Keine fremden
      Repositories ohne deren Owner ändern.
- [ ] **TASKPLAN 211 — v1.1.0 Release-Tag, RELEASE_GATE und PyPI-Frage als
      Nutzerentscheidung behandeln** (high, special, local). Kein Tagging,
      Upload oder Push ohne ausdrückliche Freigabe und Gate-Nachweis.

### Offene Entscheidungen und Schutzgrenzen

- TASKPLAN 205/206 benötigen eine bewusste CI-/Lint-Scope-Entscheidung; ein
  grüner Job darf die Rohvorlage nicht einfach global verschweigen.
- TASKPLAN 208–211 sind large/special bzw. extern: Der TASKWRITER führt sie
  nur als sichtbare nächste Schritte, führt sie nicht aus und behauptet keinen
  Release-, Upload-, Integrations- oder Live-Plattform-Erfolg.

### Review-Log

- Keine Aufgabe ausgeführt; bestehende Dateien außerhalb dieses Registers sowie
  externe Repositories unverändert.
- TASKPLAN-Register synchronisiert: IDs 205–211; alle mit Ergebnis, Quelle,
  Herleitung, Abnahme, Verifikation, Abhängigkeiten/Blocker, Aufwand, Scope und
  Prioritätsbegründung.

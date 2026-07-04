# TODO — connectors

Status: `v1.1.0 — functional`

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
- [ ] Templates: `signal_template.yaml` hinzufügen (Wizard-Vorlage für Signal)
- [ ] Templates: `discord_template.yaml` hinzufügen

### Integration

- [ ] BACH-Reimport evaluieren (siehe BACH-REIMPORT-NOTE.md)
- [ ] Gardener-Integration prüfen
- [ ] Entscheidung: `.MODULES/` oder eigenständiges Repo

### Release-Vorbereitung (wenn veröffentlicht werden soll)

- [x] `pyproject.toml` erstellen
- [ ] Security-Audit (keine echten Secrets in Quellen)
- [ ] GitHub-Repo anlegen (nur nach Audit)
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

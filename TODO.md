# TODO — connectors

Status: `v1.0.0 — functional`

## Offen

### Qualität

- [ ] Unit-Tests für `BaseConnector`, `create_connector()` Factory, Fehlerfälle
- [ ] Smoke-Tests ohne echte Secrets (Mock-Adapter)
- [ ] Import-Verifikation als CI-Schritt (python -c "from connectors import ...")

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

- [ ] `pyproject.toml` erstellen
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

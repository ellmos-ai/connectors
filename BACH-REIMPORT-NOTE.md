# BACH-Reimport-Notiz

**Erstellt:** 2026-06-14
**Adressiert an:** BACH (Entscheidung liegt beim System)

## Kontext

Das neutrale `connectors`-Modul wurde aus `BACH/system/connectors/` extrahiert
und in `.MODULES/.CONNECTORS/connectors/` als standalone, BACH-freies Modul abgelegt (v1.0.0).

Pfad: `C:\Users\User\OneDrive\.TOPICS\.AI\.MODULES\.CONNECTORS\connectors\`

## Offene Frage für BACH

BACH soll **selbst entscheiden**, ob und wann es sein internes
`system/connectors/`-Verzeichnis auf dieses neutrale Modul umstellt.

Mögliche Optionen:

1. **Beibehaltung Status quo:** BACH nutzt weiterhin `system/connectors/` intern.
   Das Modul in `.MODULES/` wird für andere Projekte (Gardener, Rinnsal etc.) genutzt.
   → Kein Handlungsbedarf für BACH.

2. **Partieller Import:** BACH importiert `BaseConnector`, `Message` etc. aus
   `.MODULES/.CONNECTORS/connectors/base.py`, behält aber eigene Connector-Implementierungen
   (wegen VoiceSTT, DB-Registrierung, Daemon-Integration).

3. **Vollständiger Reimport:** BACH stellt `system/connectors/` auf das Modul um,
   implementiert `BachSecretAdapter` und `BachSetupWizard` (mit DB-Registrierung)
   als Subklassen/Erweiterungen.

## Was das Modul bereitstellt (Vorteil für BACH)

- Entkoppelte `SecretAdapter`-Schnittstelle (kein harter `hub.secrets_handler`-Import)
- `register_connector()` in `SetupWizard` als überschreibbare Methode
- Alle 5 BACH-Connectoren portiert + neuer `webhook_connector` als Basis
- Kein Voice-STT (BACH-intern, bleibt in `hub._services.voice`)
- MIT-Lizenz, keine externen Abhängigkeiten im Kern

## Entscheidung

Diese Entscheidung liegt bei BACH. Kein Code in `system/connectors/` wurde
durch diese Extraktion verändert.

Stand der BACH-Quelle zum Zeitpunkt der Extraktion: SKILL.md v2.1.0 (2026-02-17).

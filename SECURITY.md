# Security Policy / Sicherheitsrichtlinie

**Project:** `connectors` (`ellmos-connectors`)
**Ecosystem:** [ellmos-ai](https://github.com/ellmos-ai)
**Umbrella:** [open-bricks](https://github.com/open-bricks)
**Last Updated:** 2026-08-25

---

## Supported Versions / Unterstützte Versionen

| Version | Supported / Unterstützt | Status |
|---------|------------------------|--------|
| `1.1.x` | :white_check_mark: Yes | Current Active Release Line |
| `< 1.1.0` | :x: No | End of Life / Upgrade Recommended |

---

## Reporting a Vulnerability / Sicherheitslücke Melden

If you discover a security vulnerability in this project, please do **not** open a public GitHub issue.

### Preferred Channels / Bevorzugte Meldewege

1. **GitHub Security Advisory (Recommended / Empfohlen):**
   Open a private advisory via [GitHub Security Advisories](https://github.com/ellmos-ai/connectors/security/advisories/new).
2. **Direct Maintainer Contact:**
   Reach out via the contact information published on the organization profile (`https://github.com/ellmos-ai`).

### Information to Provide / Erforderliche Angaben

Please include as much detail as possible:
- Type of vulnerability (e.g., credential exposure, SSRF, command injection, path traversal)
- Affected connector module (`telegram_connector.py`, `discord_connector.py`, `signal_connector.py`, etc.)
- Step-by-step reproduction instructions and minimal proof-of-concept
- Potential impact and threat model
- Suggested mitigation or patch (if available)

### Response SLA / Reaktionszeiten

- **Acknowledgment:** Within 48 hours (Empfangsbestätigung innerhalb von 48 Stunden)
- **Initial Assessment & Triage:** Within 5 business days (Ersteinschätzung innerhalb von 5 Werktagen)
- **Fix & Advisory Release:** Coordinated disclosure following verified resolution

---

## Security Guarantees & Token Architecture / Sicherheitsgarantien & Token-Architektur

1. **Zero Runtime Secret Persistence:**
   `connectors` never writes API tokens, bot credentials, or session data to disk or persistent state stores.
2. **Repr & Log Leak Prevention:**
   `ConnectorConfig.auth_config` is defined with `field(repr=False)`. All connector classes ensure their `__repr__()` implementations mask secrets and only expose identifier and status metadata.
3. **Pluggable Secret Resolution:**
   Secrets can be resolved via environment variables (`os.environ`), `.env` files, or through the decoupled `SecretAdapter` interface for external key vaults.
4. **Injection Safety:**
   Process invocations in `SignalConnector` strictly pass arguments as structured arrays to `subprocess.run` (without `shell=True`) to prevent shell injection.
5. **Zero Mandatory Runtime Dependencies:**
   The core library relies exclusively on Python standard library modules (`urllib`, `json`, `threading`, `subprocess`, etc.), minimizing supply-chain attack surfaces.

---

## Out-of-Scope / Nicht im Sicherheitsbereich

- Third-party platform infrastructure outages or security incidents (Telegram, Discord, Meta WhatsApp, Signal Network, Home Assistant).
- Vulnerabilities within external system binaries such as `signal-cli` (report upstream to [AsamK/signal-cli](https://github.com/AsamK/signal-cli)).
- Insecure storage of secrets in user code, configuration files, or environment variable management outside this library's boundaries.

# Security Policy

## Supported Versions

| Version | Supported          |
|---------|-------------------|
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please do **not** open
a public GitHub issue. Instead:

1. Open a [GitHub Security Advisory](https://github.com/ellmos-ai/connectors/security/advisories/new)
   (recommended — keeps details private until a fix is released).
2. Or email the maintainers directly via the contact listed in the repository profile.

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- (Optional) A suggested fix

You can expect an initial response within 5 business days.

## Scope

This module handles **no secrets at runtime** by default — all tokens and API keys
must be supplied by the caller via environment variables or the `SecretAdapter`
interface. The module never stores, logs, or transmits credentials on its own.

Known out-of-scope items:
- Security of the downstream messaging services (Telegram, Discord, etc.)
- Vulnerabilities in `signal-cli` (report upstream to AsamK/signal-cli)
- Issues arising from callers hardcoding secrets in `auth_config` (against documented best practice)

# Third-Party Licenses & Software Inventory

**Project:** `connectors` (`ellmos-connectors`)
**License:** [MIT License](LICENSE)
**Audit Date:** 2026-09-10

---

## Runtime Architecture & Dependencies

`connectors` follows a strict **zero-dependency** core architecture for its primary runtime messaging interfaces.

### Core Runtime Dependencies

| Package | Version | License | Direct/Transitive | Purpose |
|:---|:---|:---|:---|:---|
| *None* (Python Standard Library only) | >=3.8 | PSF License | N/A | `urllib`, `json`, `threading`, `subprocess`, `sqlite3`, `abc`, `dataclasses`, `enum`, `socket`, `datetime`, `pathlib` |

All built-in connectors (`TelegramConnector`, `DiscordConnector`, `WhatsAppConnector`, `HomeAssistantConnector`, `WebhookConnector`, `SignalConnector`, `SlackConnector`, `iMessageConnector`) rely exclusively on Python standard library modules.

---

## Optional & Development Dependencies

| Package / Tool | Version / Spec | License | Scope | Purpose |
|:---|:---|:---|:---|:---|
| [pyyaml](https://pyyaml.org/) | `>=6.0` | MIT | `[wizard]`, `[test]` | YAML template parsing for interactive setup wizard |
| [pytest](https://pytest.org/) | `>=7.0` | MIT | `[test]` | Automated test runner and contract verification |

---

## External Binary Boundaries

| External Binary / Protocol | Interface / Protocol | License | Scope | Notice / Boundary |
|:---|:---|:---|:---|:---|
| [signal-cli](https://github.com/AsamK/signal-cli) | CLI / JSON-RPC via `subprocess` | GPL-3.0-or-later | Optional (`SignalConnector`) | Not bundled or distributed with `connectors`. Executed strictly via external CLI invocation if configured. |
| macOS `osascript` | AppleScript IPC via `subprocess` | Apple Proprietary / System | Optional (`iMessageConnector`) | Native macOS system tool for AppleScript execution. Not bundled; available only on Darwin systems. |

---

## Architectural References & Upstream Attribution

`connectors` contains clean-room, zero-dependency implementations for messaging protocols. Specific interface patterns and protocol mappings draw conceptual inspiration from open-source multi-channel projects:

| Project / Upstream | Repository | License | Notice & Attribution |
|:---|:---|:---|:---|
| **OpenClaw** | [openclaw/openclaw](https://github.com/openclaw/openclaw) | MIT License | Copyright (c) 2024-2026 OpenClaw Contributors. Multi-channel gateway abstractions (Slack, WhatsApp, Signal, Discord). |
| **Hermes Agent** | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | MIT License | Copyright (c) 2024-2026 Nous Research. Agentic messaging gateway patterns and tool integration paradigms. |

> **License Distinction Notice (Hermes Agent vs. Weights):**
> Hermes Agent software is licensed under the MIT License. Model weights published under the "Nous Hermes" name (e.g. Hermes 3/4) are separate artifacts subject to upstream base model terms (e.g., Meta Llama Community License or Apache 2.0). `connectors` contains solely communication interfaces and does not bundle or distribute model weights.

---

## License Texts & Attribution

### MIT License (`connectors`, `pyyaml`, `pytest`, `OpenClaw`, `Hermes Agent`)

Per the terms of the MIT License (*"The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software"*), the complete license text is provided below:

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

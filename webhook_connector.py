#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebhookConnector — Generic HTTP Webhook Connector
=================================================

Status: STUB / Basis-Implementierung
=======================================
Diese Datei ist eine Neuentwicklung (kein direktes BACH-Äquivalent vorhanden).
Sie dient als Ausgangspunkt und ist NICHT produktionsreif.

Unterstützt:
- Ausgehende Webhooks: HTTP POST an eine konfigurierte URL (senden)
- Eingehende Webhooks: Verarbeitung von Webhook-Payloads via process_webhook()
  (erfordert eigenen HTTP-Server — dieser Connector stellt keinen bereit)

Für einen eingehenden Webhook-Server empfiehlt sich:
- Python: http.server.BaseHTTPRequestHandler
- FastAPI / Flask (externe Abhängigkeit)
- n8n / ähnliche Orchestrierungs-Tools

Schnellstart (nur senden):

    import os
    from connectors.base import ConnectorConfig
    from connectors.webhook_connector import WebhookConnector

    config = ConnectorConfig(
        name="webhook_notify",
        connector_type="webhook",
        endpoint=os.environ["WEBHOOK_URL"],
        options={
            "method": "POST",               # HTTP-Methode
            "content_type": "application/json",
            "payload_template": '{"text": "{content}"}',  # {content} wird ersetzt
        },
    )
    wh = WebhookConnector(config)
    wh.connect()
    wh.send_message("", "Hallo via Webhook!")

MIT License — siehe LICENSE
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Optional, Dict, Any

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from connectors.base import (
    BaseConnector, ConnectorConfig, ConnectorStatus, Message, SecretAdapter
)


class WebhookConnector(BaseConnector):
    """Generic HTTP Webhook Connector (Stub).

    Ausgehend (senden): HTTP POST an endpoint mit konfigurierbarem Payload.
    Eingehend (empfangen): process_webhook() zum Verarbeiten eingehender Daten.
    get_messages() gibt [] zurück — kein eigener HTTP-Server enthalten.
    """

    def __init__(self, config: ConnectorConfig,
                 secret_adapter: Optional[SecretAdapter] = None):
        super().__init__(config, secret_adapter)
        self._url = config.endpoint
        self._method = config.options.get("method", "POST").upper()
        self._content_type = config.options.get(
            "content_type", "application/json"
        )
        self._payload_template = config.options.get(
            "payload_template", '{"text": "{content}"}'
        )
        # Optionaler Bearer-Token für Auth
        self._bearer_token = self._resolve_secret(
            config.auth_config, "bearer_token"
        )

    def connect(self) -> bool:
        """Prüft ob die Webhook-URL gesetzt ist (kein echtes Handshake)."""
        if not self._url:
            self._status = ConnectorStatus.ERROR
            return False
        self._status = ConnectorStatus.CONNECTED
        return True

    def disconnect(self) -> bool:
        self._status = ConnectorStatus.DISCONNECTED
        return True

    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """HTTP-Request an den konfigurierten Webhook senden.

        Args:
            recipient: Wird ignoriert (Ziel ist via endpoint konfiguriert).
            content:   Nachrichtentext — ersetzt {content} im payload_template.
        """
        try:
            payload_str = self._payload_template.replace(
                "{content}", content.replace('"', '\\"')
            )
            data = payload_str.encode("utf-8")
            headers = {"Content-Type": self._content_type}
            if self._bearer_token:
                headers["Authorization"] = f"Bearer {self._bearer_token}"

            req = urllib.request.Request(
                self._url, data=data, headers=headers, method=self._method
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status < 400
        except Exception as e:
            print(f"[Webhook send_message Error] {type(e).__name__}: {e}",
                  file=sys.stderr)
            return False

    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """Webhook-Connector hat keinen eingehenden Poll-Mechanismus.

        Nutzen Sie process_webhook() in Ihrem HTTP-Handler.

        Returns:
            Immer [].
        """
        return []

    def process_webhook(self, payload: Dict[str, Any],
                        sender: str = "",
                        content_key: str = "text") -> List[Message]:
        """Eingehende Webhook-Daten in Message-Objekte umwandeln.

        Args:
            payload:     Geparster JSON-Body des eingehenden Requests.
            sender:      Optionale Absender-Kennung.
            content_key: JSON-Schlüssel im Payload für den Nachrichtentext.

        Returns:
            Liste mit einer Message, oder [] wenn kein Inhalt gefunden.
        """
        content = payload.get(content_key, "")
        if not content:
            # Fallback: kompletten Payload serialisieren
            content = json.dumps(payload, ensure_ascii=False)

        return [
            Message(
                channel="webhook",
                sender=sender,
                content=content,
                timestamp=datetime.utcnow().isoformat(),
                direction="in",
                metadata={"raw_payload": payload},
            )
        ]

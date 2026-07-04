#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsAppConnector — WhatsApp Business API Connector
====================================================

Implementiert BaseConnector für die WhatsApp Business API (Meta).
Eingehende Nachrichten werden über Webhooks empfangen (kein Polling möglich).

Docs: https://developers.facebook.com/docs/whatsapp/cloud-api

Schnellstart:

    import os
    from connectors.base import ConnectorConfig
    from connectors.whatsapp_connector import WhatsAppConnector

    config = ConnectorConfig(
        name="whatsapp_main",
        connector_type="whatsapp",
        auth_type="api_key",
        auth_config={
            "api_token": os.environ["WA_API_TOKEN"],
            "phone_number_id": os.environ["WA_PHONE_NUMBER_ID"],
        },
    )
    connector = WhatsAppConnector(config)
    if connector.connect():
        connector.send_message("49XXXXXXXXXX", "Hallo!")

Webhook-Empfang (eingehende Nachrichten):

    # In Ihrem Webhook-Handler:
    messages = connector.process_webhook(webhook_json_body)

MIT License — siehe LICENSE
"""

import json
import os
import sys
import time
import threading
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Optional, Callable, Tuple, Dict, Any

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


class WhatsAppConnector(BaseConnector):
    """WhatsApp Business API Connector.

    Senden: via Cloud API (graph.facebook.com).
    Empfangen: via Webhook (process_webhook); get_messages() gibt [] zurück.

    Polling-Loop ist für zukünftige Webhook-Cache-Integration vorbereitet.
    """

    API_BASE = "https://graph.facebook.com/v18.0"

    def __init__(self, config: ConnectorConfig,
                 secret_adapter: Optional[SecretAdapter] = None):
        super().__init__(config, secret_adapter)
        self._api_token = self._resolve_secret(config.auth_config, "api_token")
        self._phone_number_id = config.auth_config.get("phone_number_id", "")
        self._session_data = None
        self._polling = False

    def connect(self) -> bool:
        """Verbindung prüfen via Phone-Number-Info-Endpoint."""
        if not self._api_token or not self._phone_number_id:
            self._status = ConnectorStatus.ERROR
            return False

        self._status = ConnectorStatus.CONNECTING
        try:
            url = f"{self.API_BASE}/{self._phone_number_id}"
            headers = {"Authorization": f"Bearer {self._api_token}"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                self._session_data = json.loads(resp.read().decode("utf-8"))
            self._status = ConnectorStatus.CONNECTED
            return True
        except Exception as e:
            print(f"[WhatsApp connect Error] {type(e).__name__}: {e}",
                  file=sys.stderr)
        self._status = ConnectorStatus.ERROR
        return False

    def disconnect(self) -> bool:
        self._polling = False
        self._status = ConnectorStatus.DISCONNECTED
        return True

    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """Textnachricht senden.

        Args:
            recipient: Telefonnummer ohne "+" (z.B. "49XXXXXXXXXX").
            content:   Nachrichtentext.
            attachments: NICHT unterstuetzt (Warnung auf stderr).
        """
        self._warn_attachments_unsupported(attachments)
        try:
            url = f"{self.API_BASE}/{self._phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self._api_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "text",
                "text": {"body": content},
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result is not None
        except Exception as e:
            print(f"[WhatsApp send_message Error] {type(e).__name__}: {e}",
                  file=sys.stderr)
            return False

    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """WhatsApp Business API liefert eingehende Nachrichten via Webhook.

        Implementieren Sie process_webhook() in Ihrem HTTP-Handler und
        speichern Sie die Nachrichten in einem lokalen Cache, den Sie
        hier zurückgeben — oder nutzen Sie direkt process_webhook().

        Returns:
            Immer [] (Webhook-basierter Empfang, kein Polling möglich).
        """
        return []

    def process_webhook(self, webhook_data: Dict[str, Any]) -> List[Message]:
        """Eingehende Webhook-Daten von Meta verarbeiten.

        Args:
            webhook_data: Geparster JSON-Body des Webhook-POST-Requests.

        Returns:
            Liste eingehender Textnachrichten.
        """
        messages = []
        try:
            for entry in webhook_data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    for msg in value.get("messages", []):
                        if msg.get("type") == "text":
                            messages.append(Message(
                                channel="whatsapp",
                                sender=msg.get("from", ""),
                                content=msg.get("text", {}).get("body", ""),
                                timestamp=datetime.fromtimestamp(
                                    int(msg.get("timestamp", 0))).isoformat(),
                                direction="in",
                                message_id=msg.get("id", ""),
                                metadata={"type": msg.get("type", "text")},
                            ))
        except Exception as e:
            print(f"[WhatsApp Webhook Error] {e}", file=sys.stderr)
        return messages

    # ------------------------------------------------------------------
    # Polling Runtime (vorbereitet für zukünftige Webhook-Cache-Integration)
    # ------------------------------------------------------------------

    def poll_loop(self, on_message: Callable[[Message], None],
                  interval: float = 5.0,
                  stop_event: Optional[threading.Event] = None) -> None:
        """Loop-Platzhalter. Nützlich sobald get_messages() einen Cache nutzt."""
        self._polling = True
        while self._polling and not (stop_event and stop_event.is_set()):
            try:
                for msg in self.get_messages():
                    try:
                        on_message(msg)
                    except Exception as e:
                        print(
                            f"[WhatsApp on_message callback Error] "
                            f"{type(e).__name__}: {e}",
                            file=sys.stderr,
                        )
            except Exception as e:
                print(f"[WhatsApp poll_loop Error] {type(e).__name__}: {e}",
                      file=sys.stderr)
            time.sleep(interval)

    def poll_threaded(
        self,
        on_message: Callable[[Message], None],
        interval: float = 5.0,
    ) -> Tuple[threading.Thread, threading.Event]:
        """Startet Poll-Loop in eigenem Daemon-Thread."""
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self.poll_loop,
            args=(on_message, interval, stop_event),
            daemon=True,
            name="connectors-whatsapp-poll",
        )
        thread.start()
        return thread, stop_event

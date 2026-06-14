#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{{CONNECTOR_NAME}}Connector — {{CONNECTOR_DISPLAY_NAME}} Connector
===================================================================

{{CONNECTOR_DESCRIPTION}}

Implementiert BaseConnector für {{CONNECTOR_DISPLAY_NAME}}.

Schnellstart:

    from connectors.{{CONNECTOR_MODULE}} import {{CONNECTOR_NAME}}Connector
    from connectors.base import ConnectorConfig

    config = ConnectorConfig(
        name="{{CONNECTOR_INSTANCE_NAME}}",
        connector_type="{{CONNECTOR_TYPE}}",
        auth_type="{{AUTH_TYPE}}",
        auth_config={{AUTH_CONFIG_EXAMPLE}},
        options={{OPTIONS_EXAMPLE}},
    )
    connector = {{CONNECTOR_NAME}}Connector(config)
    connector.connect()
    connector.send_message("{{RECIPIENT_EXAMPLE}}", "Hallo!")

MIT License — siehe LICENSE
"""

import os
import sys
import json
import time
import threading
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Optional, Callable, Tuple

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


class {{CONNECTOR_NAME}}Connector(BaseConnector):
    """{{CONNECTOR_DISPLAY_NAME}} Connector mit Polling-Runtime."""

    {{API_BASE_COMMENT}}
    API_BASE = "{{API_BASE_URL}}"

    def __init__(self, config: ConnectorConfig,
                 secret_adapter: Optional[SecretAdapter] = None):
        super().__init__(config, secret_adapter)
        {{INIT_VARIABLES}}
        self._polling = False

    def connect(self) -> bool:
        """Verbindung herstellen."""
        {{CONNECT_VALIDATION}}

        self._status = ConnectorStatus.CONNECTING
        try:
            {{CONNECT_IMPLEMENTATION}}
            self._status = ConnectorStatus.CONNECTED
            return True
        except Exception as e:
            print(f"[{{CONNECTOR_NAME}} connect Error] {type(e).__name__}: {e}",
                  file=sys.stderr)

        self._status = ConnectorStatus.ERROR
        return False

    def disconnect(self) -> bool:
        """Verbindung trennen."""
        self._polling = False
        self._status = ConnectorStatus.DISCONNECTED
        return True

    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """Nachricht senden."""
        try:
            {{SEND_MESSAGE_IMPLEMENTATION}}
            return True
        except Exception as e:
            print(f"[{{CONNECTOR_NAME}} send_message Error] {type(e).__name__}: {e}",
                  file=sys.stderr)
            return False

    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """Neue Nachrichten abrufen."""
        try:
            {{GET_MESSAGES_IMPLEMENTATION}}

            messages = []
            {{PARSE_MESSAGES_IMPLEMENTATION}}

            return messages
        except Exception as e:
            print(f"[{{CONNECTOR_NAME}} get_messages Error] {type(e).__name__}: {e}",
                  file=sys.stderr)
            return []

    # ------------------------------------------------------------------
    # Polling Runtime
    # ------------------------------------------------------------------

    def poll_loop(self, on_message: Callable[[Message], None],
                  interval: float = 5.0,
                  stop_event: Optional[threading.Event] = None) -> None:
        """Blockierender Polling-Loop."""
        self._polling = True
        while self._polling and not (stop_event and stop_event.is_set()):
            try:
                for msg in self.get_messages():
                    try:
                        on_message(msg)
                    except Exception as e:
                        print(
                            f"[{{CONNECTOR_NAME}} on_message callback Error] "
                            f"{type(e).__name__}: {e}",
                            file=sys.stderr,
                        )
            except Exception as e:
                print(f"[{{CONNECTOR_NAME}} poll_loop Error] {type(e).__name__}: {e}",
                      file=sys.stderr)
            time.sleep(interval)

    def poll_threaded(
        self,
        on_message: Callable[[Message], None],
        interval: float = 5.0,
    ) -> Tuple[threading.Thread, threading.Event]:
        """Startet Polling in eigenem Daemon-Thread."""
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self.poll_loop,
            args=(on_message, interval, stop_event),
            daemon=True,
            name="connectors-{{CONNECTOR_TYPE}}-poll",
        )
        thread.start()
        return thread, stop_event

    # ------------------------------------------------------------------
    # Internal Helper Methods
    # ------------------------------------------------------------------

    {{HELPER_METHODS}}

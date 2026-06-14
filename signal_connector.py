#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SignalConnector — Signal Messenger Connector
============================================

Implementiert BaseConnector für Signal Messenger via signal-cli.
Benötigt: signal-cli installiert und konfiguriert auf dem System.
  Docs: https://github.com/AsamK/signal-cli

Schnellstart:

    from connectors.base import ConnectorConfig
    from connectors.signal_connector import SignalConnector

    config = ConnectorConfig(
        name="signal_main",
        connector_type="signal",
        auth_type="none",
        auth_config={"phone_number": "+49XXXXXXXXXX"},
        options={"signal_cli_path": "/usr/local/bin/signal-cli"},
    )
    connector = SignalConnector(config)
    if connector.connect():
        connector.send_message("+49XXXXXXXXXX", "Hallo!")
        messages = connector.get_messages()

MIT License — siehe LICENSE
"""

import json
import os
import subprocess
import sys
import time
import threading
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


class SignalConnector(BaseConnector):
    """Signal Messenger Connector via signal-cli.

    Hinweis: Die Telefonnummer muss bereits mit signal-cli registriert sein.
    Registrierung: signal-cli -a +49XXXXXXXXXX register --voice
    """

    def __init__(self, config: ConnectorConfig,
                 secret_adapter: Optional[SecretAdapter] = None):
        super().__init__(config, secret_adapter)
        self._phone_number = (
            config.auth_config.get("phone_number", "")
            or config.options.get("phone_number", "")
        )
        self._signal_cli_path = config.options.get("signal_cli_path", "signal-cli")
        self._last_timestamp = config.options.get("last_timestamp", 0)
        self._polling = False

    def connect(self) -> bool:
        """Prüft ob signal-cli verfügbar und die Nummer registriert ist."""
        if not self._phone_number:
            self._status = ConnectorStatus.ERROR
            return False

        self._status = ConnectorStatus.CONNECTING
        try:
            result = subprocess.run(
                [self._signal_cli_path, "--version"],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=5,
            )
            if result.returncode == 0:
                self._status = ConnectorStatus.CONNECTED
                return True
        except FileNotFoundError:
            print(
                f"[Signal connect Error] signal-cli nicht gefunden: "
                f"{self._signal_cli_path}",
                file=sys.stderr,
            )
        except subprocess.TimeoutExpired:
            print("[Signal connect Error] signal-cli Timeout", file=sys.stderr)

        self._status = ConnectorStatus.ERROR
        return False

    def disconnect(self) -> bool:
        self._polling = False
        self._status = ConnectorStatus.DISCONNECTED
        return True

    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """Nachricht senden via signal-cli.

        Args:
            recipient:   Telefonnummer des Empfängers (z.B. "+49XXXXXXXXXX").
            content:     Nachrichtentext.
            attachments: Optionale Liste lokaler Dateipfade.
        """
        try:
            cmd = [
                self._signal_cli_path,
                "-a", self._phone_number,
                "send",
                "-m", content,
                recipient,
            ]
            if attachments:
                for att in attachments:
                    cmd.extend(["-a", att])

            result = subprocess.run(
                cmd, capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=30,
            )
            return result.returncode == 0
        except Exception as e:
            print(f"[Signal send_message Error] {type(e).__name__}: {e}",
                  file=sys.stderr)
            return False

    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """Neue Nachrichten via signal-cli receive --json abrufen."""
        try:
            result = subprocess.run(
                [self._signal_cli_path, "-a", self._phone_number, "receive", "--json"],
                capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=30,
            )
            if result.returncode != 0:
                return []

            messages = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                try:
                    envelope = json.loads(line)
                    if "envelope" not in envelope:
                        continue
                    env = envelope["envelope"]

                    timestamp = env.get("timestamp", 0)
                    if timestamp <= self._last_timestamp:
                        continue
                    self._last_timestamp = max(self._last_timestamp, timestamp)

                    data_msg = env.get("dataMessage")
                    if not data_msg:
                        continue
                    msg_text = data_msg.get("message", "")
                    if not msg_text:
                        continue

                    sender = env.get("source", "") or env.get("sourceNumber", "")
                    messages.append(Message(
                        channel="signal",
                        sender=sender,
                        content=msg_text,
                        timestamp=datetime.fromtimestamp(
                            timestamp / 1000).isoformat(),
                        direction="in",
                        message_id=str(timestamp),
                        metadata={
                            "source_device": env.get("sourceDevice", 0),
                            "timestamp_ms": timestamp,
                        },
                    ))
                except json.JSONDecodeError:
                    continue

            return messages[:limit]
        except Exception as e:
            print(f"[Signal get_messages Error] {type(e).__name__}: {e}",
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
                            f"[Signal on_message callback Error] "
                            f"{type(e).__name__}: {e}",
                            file=sys.stderr,
                        )
            except Exception as e:
                print(f"[Signal poll_loop Error] {type(e).__name__}: {e}",
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
            name="connectors-signal-poll",
        )
        thread.start()
        return thread, stop_event

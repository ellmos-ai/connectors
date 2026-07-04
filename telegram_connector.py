#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TelegramConnector — Telegram Bot API Connector
===============================================

Implementiert BaseConnector für die Telegram Bot API.
Benötigt: Bot-Token von @BotFather (Umgebungsvariable TG_BOT_TOKEN empfohlen).

Nur stdlib (urllib, json, threading) — keine externen Abhängigkeiten.

Schnellstart:

    import os
    from connectors.base import ConnectorConfig
    from connectors.telegram_connector import TelegramConnector

    config = ConnectorConfig(
        name="my_bot",
        connector_type="telegram",
        auth_type="api_key",
        auth_config={"bot_token": os.environ["TG_BOT_TOKEN"]},
        options={"owner_chat_id": ""},   # Optional: Nur diesen Chat akzeptieren
    )
    bot = TelegramConnector(config)
    if bot.connect():
        bot.send_message("CHAT_ID", "Hallo!")
        # Polling:
        thread, stop = bot.poll_threaded(on_message=lambda m: print(m.content))

BACH-Integration (optional):
    Wenn _secret_refs verwendet wird, SecretAdapter aus base.py übergeben:

        config = ConnectorConfig(
            name="my_bot",
            connector_type="telegram",
            auth_config={"_secret_refs": {"bot_token": "telegram_bot_token"}},
        )
        bot = TelegramConnector(config, secret_adapter=BachSecretAdapter())

MIT License — siehe LICENSE
"""

import json
import os
import socket
import sys
import time
import threading
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Optional, Callable, Tuple

# UTF-8 Encoding sicherstellen (wichtig auf Windows)
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


class TelegramConnector(BaseConnector):
    """Telegram Bot API Connector mit Polling-Runtime.

    Unterstützte Features:
    - Nachrichten senden (Text, Markdown-Fallback auf Plain)
    - Nachrichten empfangen via getUpdates (Long-Polling)
    - Optionaler Owner-Filter (nur Nachrichten von einer Chat-ID)
    - Threaded Polling mit Stop-Event
    - Retry-Logik bei Netzwerkfehlern
    """

    API_BASE = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, config: ConnectorConfig,
                 secret_adapter: Optional[SecretAdapter] = None):
        super().__init__(config, secret_adapter)
        self._bot_token = self._resolve_secret(config.auth_config, "bot_token")
        self._owner_chat_id = str(config.options.get("owner_chat_id", ""))
        self._last_update_id = int(config.auth_config.get("last_update_id", 0))
        self._bot_info = None
        self._polling = False

    def connect(self) -> bool:
        """Verbindung prüfen via getMe."""
        if not self._bot_token:
            self._status = ConnectorStatus.ERROR
            return False

        self._status = ConnectorStatus.CONNECTING
        try:
            result = self._api_call("getMe")
            if result:
                self._bot_info = result
                self._status = ConnectorStatus.CONNECTED
                return True
        except Exception:
            pass

        self._status = ConnectorStatus.ERROR
        return False

    def disconnect(self) -> bool:
        """Polling stoppen (Telegram benötigt keinen expliziten Disconnect)."""
        self._polling = False
        self._status = ConnectorStatus.DISCONNECTED
        return True

    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """Nachricht an chat_id senden.

        Versucht zuerst Markdown; bei Parse-Fehler automatisch Plain-Text.
        attachments werden derzeit NICHT unterstuetzt (Warnung auf stderr).
        """
        self._warn_attachments_unsupported(attachments)
        try:
            params = {
                "chat_id": recipient or self._owner_chat_id,
                "text": content,
                "parse_mode": "Markdown",
            }
            result = self._api_call("sendMessage", params, retries=1)

            if result is None:
                # Retry ohne Markdown bei Parse-Fehlern
                params = {
                    "chat_id": recipient or self._owner_chat_id,
                    "text": content,
                }
                result = self._api_call("sendMessage", params)

            return result is not None
        except Exception as e:
            print(f"[Telegram send_message Error] {type(e).__name__}: {e}",
                  file=sys.stderr)
            return False

    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """Neue Nachrichten via getUpdates abrufen (Long-Polling, 30s).

        Wenn owner_chat_id gesetzt: Nachrichten anderer Chats werden ignoriert.
        """
        try:
            params = {
                "offset": self._last_update_id + 1,
                "limit": min(limit, 100),
                "timeout": 30,
            }
            result = self._api_call("getUpdates", params, timeout=40)
            if not result:
                return []

            messages = []
            for update in result:
                self._last_update_id = max(
                    self._last_update_id, update.get("update_id", 0)
                )

                msg = update.get("message")
                if not msg:
                    continue

                chat = msg.get("chat", {})
                sender_id = str(chat.get("id", ""))

                # Owner-Filter
                if self._owner_chat_id and sender_id != self._owner_chat_id:
                    continue

                from_user = msg.get("from", {})
                sender_name = (
                    from_user.get("first_name", "") + " "
                    + from_user.get("last_name", "")
                ).strip()

                content = msg.get("text", "") or msg.get("caption", "")
                if not content:
                    continue

                messages.append(Message(
                    channel="telegram",
                    sender=sender_id,
                    content=content,
                    timestamp=datetime.fromtimestamp(
                        msg.get("date", 0)).isoformat(),
                    direction="in",
                    message_id=str(msg.get("message_id", "")),
                    metadata={
                        "chat_type": chat.get("type", ""),
                        "sender_name": sender_name,
                        "update_id": update.get("update_id", 0),
                    },
                ))

            return messages
        except Exception as e:
            print(f"[Telegram get_messages Error] {type(e).__name__}: {e}",
                  file=sys.stderr)
            return []

    # ------------------------------------------------------------------
    # Polling Runtime
    # ------------------------------------------------------------------

    def poll_loop(self, on_message: Callable[[Message], None],
                  interval: float = 5.0,
                  stop_event: Optional[threading.Event] = None) -> None:
        """Blockierender Polling-Loop. Ruft on_message() für jede neue Nachricht auf.

        Args:
            on_message: Callback der für jede eingehende Nachricht aufgerufen wird.
            interval:   Sekunden zwischen Polls (Standard: 5).
            stop_event: threading.Event zum Stoppen von außen.
        """
        self._polling = True
        while self._polling and not (stop_event and stop_event.is_set()):
            try:
                for msg in self.get_messages():
                    try:
                        on_message(msg)
                    except Exception as e:
                        print(
                            f"[Telegram on_message callback Error] "
                            f"{type(e).__name__}: {e}",
                            file=sys.stderr,
                        )
            except Exception as e:
                print(f"[Telegram poll_loop Error] {type(e).__name__}: {e}",
                      file=sys.stderr)
            time.sleep(interval)

    def poll_threaded(
        self,
        on_message: Callable[[Message], None],
        interval: float = 5.0,
    ) -> Tuple[threading.Thread, threading.Event]:
        """Startet Polling in eigenem Daemon-Thread.

        Returns:
            (Thread, StopEvent) — StopEvent.set() hält den Loop an.
        """
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self.poll_loop,
            args=(on_message, interval, stop_event),
            daemon=True,
            name="connectors-telegram-poll",
        )
        thread.start()
        return thread, stop_event

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _api_call(self, method: str, params: Optional[dict] = None,
                  retries: int = 3, timeout: int = 15):
        """Telegram Bot API aufrufen (urllib, mit Retry bei Netzwerkfehlern).

        Args:
            method:  Telegram-Methode (z.B. "sendMessage").
            params:  Parameter als dict (optional).
            retries: Anzahl Wiederholungsversuche.
            timeout: HTTP-Timeout in Sekunden (bei Long-Polling höher setzen).

        Returns:
            API-Result-Objekt oder None bei Fehler.
        """
        url = self.API_BASE.format(token=self._bot_token, method=method)

        for attempt in range(retries):
            if params:
                data = json.dumps(params, ensure_ascii=False).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data,
                    headers={"Content-Type": "application/json; charset=utf-8"},
                )
            else:
                req = urllib.request.Request(url)

            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                    if body.get("ok"):
                        return body.get("result")
                    if attempt == retries - 1:
                        print(
                            f"[Telegram API Error] {method}: "
                            f"{body.get('description', 'Unknown error')}",
                            file=sys.stderr,
                        )
                    return None
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    print(f"[Telegram HTTP Error] {method}: HTTP {e.code}",
                          file=sys.stderr)
                    return None
                if attempt == retries - 1:
                    print(f"[Telegram HTTP Error] {method}: HTTP {e.code}",
                          file=sys.stderr)
                    return None
                time.sleep(2 * (attempt + 1))
            except urllib.error.URLError as e:
                if attempt == retries - 1:
                    print(f"[Telegram Network Error] {method}: {e.reason}",
                          file=sys.stderr)
                    return None
                time.sleep(2 * (attempt + 1))
            except socket.timeout:
                if method == "getUpdates":
                    return []
                if attempt == retries - 1:
                    print(f"[Telegram Timeout] {method}", file=sys.stderr)
                    return None
                time.sleep(2 * (attempt + 1))
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                print(f"[Telegram Exception] {method}: {type(e).__name__}: {e}",
                      file=sys.stderr)
                return None

        return None

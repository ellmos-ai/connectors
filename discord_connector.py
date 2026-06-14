#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DiscordConnector — Discord Bot/Webhook Connector
=================================================

Implementiert BaseConnector für Discord.
Dual-Modus: Bot-API (bidirektional) oder Webhook-URL (nur senden).

Nur stdlib (urllib, json, threading) — keine externen Abhängigkeiten.

Schnellstart Bot-Modus (bidirektional):

    import os
    from connectors.base import ConnectorConfig
    from connectors.discord_connector import DiscordConnector

    config = ConnectorConfig(
        name="discord_main",
        connector_type="discord",
        auth_type="api_key",
        auth_config={"bot_token": os.environ["DISCORD_BOT_TOKEN"]},
        options={"default_channel": "CHANNEL_ID"},
    )
    bot = DiscordConnector(config)
    if bot.connect():
        bot.send_message("CHANNEL_ID", "Hallo!")
        thread, stop = bot.poll_threaded(on_message=lambda m: print(m.content))

Schnellstart Webhook-Modus (nur senden):

    config = ConnectorConfig(
        name="discord_webhook",
        connector_type="discord",
        endpoint=os.environ["DISCORD_WEBHOOK_URL"],
    )
    bot = DiscordConnector(config)
    bot.connect()
    bot.send_message("", "Hallo via Webhook!")

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


class DiscordConnector(BaseConnector):
    """Discord Bot/Webhook Connector mit Polling-Runtime.

    Bot-Modus: Erfordert Bot-Token und Bot-Berechtigung im Server.
    Webhook-Modus: Nur Senden — kein Empfang/Polling möglich.
    """

    API_BASE = "https://discord.com/api/v10"

    def __init__(self, config: ConnectorConfig,
                 secret_adapter: Optional[SecretAdapter] = None):
        super().__init__(config, secret_adapter)
        self._bot_token = self._resolve_secret(config.auth_config, "bot_token")
        self._webhook_url = config.endpoint  # Discord Webhook URL (optional)
        self._bot_info = None
        self._last_message_id = config.options.get("last_message_id", "")
        self._polling = False

    def connect(self) -> bool:
        """Verbindung prüfen (Bot: /users/@me; Webhook: sofort ok)."""
        if not self._bot_token and not self._webhook_url:
            self._status = ConnectorStatus.ERROR
            return False

        self._status = ConnectorStatus.CONNECTING

        if self._bot_token:
            try:
                result = self._api_call("GET", "/users/@me")
                if result:
                    self._bot_info = result
                    self._status = ConnectorStatus.CONNECTED
                    return True
            except Exception:
                pass
        elif self._webhook_url:
            self._status = ConnectorStatus.CONNECTED
            return True

        self._status = ConnectorStatus.ERROR
        return False

    def disconnect(self) -> bool:
        self._polling = False
        self._status = ConnectorStatus.DISCONNECTED
        return True

    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """Nachricht senden (Webhook hat Vorrang vor Bot, wenn endpoint gesetzt)."""
        if self._webhook_url:
            return self._send_webhook(content)
        if self._bot_token:
            return self._send_bot(recipient, content)
        return False

    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """Nachrichten aus dem konfigurierten Default-Channel abrufen (Bot-Modus)."""
        if not self._bot_token:
            return []
        channel_id = self.config.options.get("default_channel", "")
        if not channel_id:
            return []

        try:
            params = f"?limit={min(limit, 100)}"
            if since:
                params += f"&after={since}"
            result = self._api_call("GET", f"/channels/{channel_id}/messages{params}")
            if not result or not isinstance(result, list):
                return []

            messages = []
            for msg in result:
                author = msg.get("author", {})
                if self._bot_info and author.get("id") == self._bot_info.get("id"):
                    continue
                msg_id = msg.get("id", "")
                messages.append(Message(
                    channel="discord",
                    sender=author.get("username", "unknown"),
                    content=msg.get("content", ""),
                    timestamp=msg.get("timestamp", ""),
                    direction="in",
                    message_id=msg_id,
                    metadata={
                        "channel_id": msg.get("channel_id", ""),
                        "author_id": author.get("id", ""),
                        "guild_id": msg.get("guild_id", ""),
                    },
                ))
                if msg_id:
                    self._last_message_id = msg_id

            return messages
        except Exception:
            return []

    def get_new_messages(self) -> List[Message]:
        """Nur neue Nachrichten seit letztem Poll (inkrementell)."""
        if not self._bot_token:
            return []
        channel_id = self.config.options.get("default_channel", "")
        if not channel_id:
            return []

        try:
            params = "?limit=50"
            if self._last_message_id:
                params += f"&after={self._last_message_id}"
            result = self._api_call("GET", f"/channels/{channel_id}/messages{params}")
            if not result or not isinstance(result, list):
                return []

            messages = []
            for msg in result:
                author = msg.get("author", {})
                if self._bot_info and author.get("id") == self._bot_info.get("id"):
                    continue
                msg_id = msg.get("id", "")
                messages.append(Message(
                    channel="discord",
                    sender=author.get("username", "unknown"),
                    content=msg.get("content", ""),
                    timestamp=msg.get("timestamp", ""),
                    direction="in",
                    message_id=msg_id,
                    metadata={
                        "channel_id": msg.get("channel_id", ""),
                        "author_id": author.get("id", ""),
                        "guild_id": msg.get("guild_id", ""),
                    },
                ))
                if msg_id:
                    self._last_message_id = msg_id

            return messages
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Polling Runtime
    # ------------------------------------------------------------------

    def poll_loop(self, on_message: Callable[[Message], None],
                  interval: float = 10.0,
                  stop_event: Optional[threading.Event] = None) -> None:
        """Blockierender Polling-Loop (Discord Rate-Limit: ≥10s empfohlen)."""
        self._polling = True
        while self._polling and not (stop_event and stop_event.is_set()):
            try:
                for msg in self.get_new_messages():
                    try:
                        on_message(msg)
                    except Exception as e:
                        print(
                            f"[Discord on_message callback Error] "
                            f"{type(e).__name__}: {e}",
                            file=sys.stderr,
                        )
            except Exception as e:
                print(f"[Discord poll_loop Error] {type(e).__name__}: {e}",
                      file=sys.stderr)
            time.sleep(interval)

    def poll_threaded(
        self,
        on_message: Callable[[Message], None],
        interval: float = 10.0,
    ) -> Tuple[threading.Thread, threading.Event]:
        """Startet Polling in eigenem Daemon-Thread.

        Returns:
            (Thread, StopEvent)
        """
        stop_event = threading.Event()
        thread = threading.Thread(
            target=self.poll_loop,
            args=(on_message, interval, stop_event),
            daemon=True,
            name="connectors-discord-poll",
        )
        thread.start()
        return thread, stop_event

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _api_call(self, method: str, endpoint: str, data: Optional[dict] = None):
        url = f"{self.API_BASE}{endpoint}"
        headers = {
            "Authorization": f"Bot {self._bot_token}",
            "Content-Type": "application/json",
        }
        body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError:
            return None
        except urllib.error.URLError:
            return None

    def _send_bot(self, channel_id: str, content: str) -> bool:
        result = self._api_call(
            "POST", f"/channels/{channel_id}/messages", {"content": content}
        )
        return result is not None

    def _send_webhook(self, content: str) -> bool:
        data = json.dumps({"content": content}, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self._webhook_url, data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status < 400
        except Exception:
            return False

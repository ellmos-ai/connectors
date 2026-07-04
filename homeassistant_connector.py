#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HomeAssistantConnector — Home Assistant REST-API Connector
==========================================================

Implementiert BaseConnector für die Home Assistant REST-API.
Nur stdlib (urllib) — keine externen Abhängigkeiten.

Docs: https://developers.home-assistant.io/docs/api/rest

Schnellstart:

    import os
    from connectors.base import ConnectorConfig
    from connectors.homeassistant_connector import HomeAssistantConnector

    config = ConnectorConfig(
        name="ha_main",
        connector_type="homeassistant",
        endpoint="http://homeassistant.local:8123",
        auth_type="token",
        auth_config={"access_token": os.environ["HA_TOKEN"]},
    )
    ha = HomeAssistantConnector(config)
    if ha.connect():
        states = ha.get_states()
        ha.call_service("light", "turn_on", {"entity_id": "light.living_room"})
        ha.send_message("notify.mobile_app", "Hallo!")

MIT License — siehe LICENSE
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
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


class HomeAssistantConnector(BaseConnector):
    """Home Assistant REST-API Connector.

    send_message() sendet Notifications via HA notify-Services.
    get_messages() gibt [] zurück (HA hat kein natürliches Nachrichtenformat;
    nutzen Sie get_states() / get_history() für HA-Daten).
    """

    def __init__(self, config: ConnectorConfig,
                 secret_adapter: Optional[SecretAdapter] = None):
        super().__init__(config, secret_adapter)
        self._token = self._resolve_secret(config.auth_config, "access_token")
        self._base_url = config.endpoint.rstrip("/") if config.endpoint else ""
        self._ha_version = None

    def connect(self) -> bool:
        """Verbindung via /api/ prüfen."""
        if not self._token or not self._base_url:
            self._status = ConnectorStatus.ERROR
            return False

        self._status = ConnectorStatus.CONNECTING
        result = self._api_call("GET", "/api/")
        if result and "message" in result:
            self._ha_version = result.get("message", "")
            self._status = ConnectorStatus.CONNECTED
            return True

        self._status = ConnectorStatus.ERROR
        return False

    def disconnect(self) -> bool:
        self._status = ConnectorStatus.DISCONNECTED
        return True

    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """HA-Notification senden.

        Args:
            recipient: HA notify-Service-Name (z.B. "notify.mobile_app_phone").
            content:   Nachrichtentext.
            attachments: NICHT unterstuetzt (Warnung auf stderr).
        """
        self._warn_attachments_unsupported(attachments)
        return self.call_service("notify", recipient, {"message": content})

    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """Home Assistant hat kein Nachrichten-System — gibt [] zurück.

        Nutzen Sie get_states() / get_history() für HA-Entitätsdaten.
        """
        return []

    # ------------------------------------------------------------------
    # HA-spezifische Methoden
    # ------------------------------------------------------------------

    def get_states(self) -> List[Dict[str, Any]]:
        """Alle Entity-States abrufen."""
        result = self._api_call("GET", "/api/states")
        return result if isinstance(result, list) else []

    def get_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Status einer einzelnen Entity abrufen."""
        return self._api_call("GET", f"/api/states/{entity_id}")

    def call_service(self, domain: str, service: str,
                     data: Optional[Dict[str, Any]] = None) -> bool:
        """HA-Service aufrufen (z.B. light.turn_on).

        Args:
            domain:  Service-Domain (z.B. "light", "switch", "notify").
            service: Service-Name (z.B. "turn_on").
            data:    Service-Daten (z.B. {"entity_id": "light.living_room"}).
        """
        result = self._api_call("POST", f"/api/services/{domain}/{service}", data)
        return result is not None

    def get_history(self, entity_id: str, hours: int = 24) -> List[Any]:
        """Historie einer Entity abrufen.

        Args:
            entity_id: HA-Entity-ID (z.B. "sensor.temperature").
            hours:     Stunden zurück (Standard: 24).
        """
        since = (
            datetime.now(timezone.utc) - timedelta(hours=hours)
        ).isoformat().replace("+00:00", "Z")
        result = self._api_call(
            "GET",
            f"/api/history/period/{since}?filter_entity_id={entity_id}",
        )
        return result if isinstance(result, list) else []

    def fire_event(self, event_type: str,
                   data: Optional[Dict[str, Any]] = None) -> bool:
        """HA-Event feuern."""
        result = self._api_call("POST", f"/api/events/{event_type}", data)
        return result is not None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _api_call(self, method: str, endpoint: str,
                  data: Optional[dict] = None) -> Any:
        url = f"{self._base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print(f"[HomeAssistant HTTP Error] {method} {endpoint}: HTTP {e.code}",
                  file=sys.stderr)
            return None
        except urllib.error.URLError as e:
            print(f"[HomeAssistant URL Error] {method} {endpoint}: {e.reason}",
                  file=sys.stderr)
            return None

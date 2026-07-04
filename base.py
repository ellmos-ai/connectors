# -*- coding: utf-8 -*-
"""
Connector Base Interface
========================

Abstrakte Basisklasse für alle Messaging-Connectors.
Jeder Connector implementiert dieses Interface.

Standalone-Nutzung (kein Framework nötig):

    class MyConnector(BaseConnector):
        def connect(self) -> bool: ...
        def send_message(self, recipient, content) -> bool: ...
        def disconnect(self) -> bool: ...
        def get_messages(self, since=None, limit=50) -> List[Message]: ...

BACH-Integration (optional):
    Wenn das Modul innerhalb von BACH genutzt wird, kann ein optionaler
    SecretsAdapter übergeben werden, um Tokens aus bach.db / secrets.json
    zu laden. Siehe ``SecretAdapter`` weiter unten.

MIT License — siehe LICENSE
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Callable


class ConnectorStatus(Enum):
    """Status eines Connectors."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class Message:
    """Einheitliches Nachrichtenformat für alle Channels."""
    channel: str            # "signal", "whatsapp", "discord", "telegram"
    sender: str             # Absender-ID (Telefonnummer, User-ID, etc.)
    content: str            # Nachrichtentext
    timestamp: str          # ISO-8601
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    direction: str = "in"   # "in" oder "out"
    message_id: str = ""    # Channel-spezifische ID


@dataclass
class ConnectorConfig:
    """Konfiguration für einen Connector.

    Secrets (Tokens, API-Keys) sollten NIEMALS fest in auth_config
    eingebettet werden. Bevorzugte Methoden:
      1. Umgebungsvariablen (``os.environ``): auth_config = {"bot_token": os.environ["TG_BOT_TOKEN"]}
      2. .env-Datei (python-dotenv): auth_config = {"bot_token": os.getenv("TG_BOT_TOKEN")}
      3. Optionaler SecretsAdapter (Framework-Integration): auth_config = {"_secret_refs": {"bot_token": "my_key"}}
    """
    name: str               # Eindeutiger Name (z.B. "signal_main")
    connector_type: str     # "signal", "discord", "whatsapp", etc.
    endpoint: str = ""      # URL oder Pfad
    auth_type: str = "none" # "none", "api_key", "oauth", "token"
    # repr=False: auth_config enthaelt Secrets — darf nie in repr()/Logs landen
    auth_config: Dict[str, str] = field(default_factory=dict, repr=False)
    options: Dict[str, Any] = field(default_factory=dict)


class SecretAdapter(ABC):
    """Optionales Interface für Framework-seitige Secret-Auflösung.

    Implementieren Sie dieses Interface, um Tokens aus einem
    Secret-Store (Datenbank, Vault, Keychain …) nachzuladen,
    wenn ``auth_config`` nur ``_secret_refs``-Schlüssel enthält.

    Beispiel (BACH):
        class BachSecretAdapter(SecretAdapter):
            def get_secret(self, key: str) -> str:
                from hub.secrets_handler import SecretsHandler
                return SecretsHandler().get_secret(key) or ""

    Beispiel (python-dotenv):
        class EnvSecretAdapter(SecretAdapter):
            def get_secret(self, key: str) -> str:
                return os.environ.get(key, "")
    """

    @abstractmethod
    def get_secret(self, key: str) -> str:
        """Gibt den Secret-Wert für ``key`` zurück, oder "" wenn nicht gefunden."""
        ...


class BaseConnector(ABC):
    """Abstrakte Basisklasse für Messaging-Connectors.

    Standalone:
        config = ConnectorConfig(
            name="my_bot",
            connector_type="telegram",
            auth_type="api_key",
            auth_config={"bot_token": os.environ["TG_BOT_TOKEN"]},
        )
        bot = TelegramConnector(config)

    Mit SecretsAdapter (optionale Framework-Integration):
        config = ConnectorConfig(
            name="my_bot",
            connector_type="telegram",
            auth_type="api_key",
            auth_config={"_secret_refs": {"bot_token": "telegram_bot_token"}},
        )
        bot = TelegramConnector(config, secret_adapter=BachSecretAdapter())
    """

    def __init__(self, config: ConnectorConfig,
                 secret_adapter: Optional[SecretAdapter] = None):
        self.config = config
        self._secret_adapter = secret_adapter
        self._status = ConnectorStatus.DISCONNECTED

    def _resolve_secret(self, auth_config: Dict[str, str], key: str) -> str:
        """Löst einen Secret auf – direkt oder via SecretAdapter.

        Reihenfolge:
        1. Direkt in auth_config vorhanden → zurückgeben
        2. ``_secret_refs[key]`` vorhanden + SecretAdapter gesetzt → nachschlagen
        3. Sonst leerer String
        """
        # Direkter Wert
        if key in auth_config and auth_config[key]:
            return auth_config[key]
        # Über Adapter
        if self._secret_adapter:
            refs = auth_config.get("_secret_refs", {})
            if isinstance(refs, dict) and key in refs:
                return self._secret_adapter.get_secret(refs[key]) or ""
        return ""

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def connector_type(self) -> str:
        return self.config.connector_type

    @property
    def status(self) -> ConnectorStatus:
        return self._status

    @abstractmethod
    def connect(self) -> bool:
        """Verbindung herstellen. Returns True bei Erfolg."""
        ...

    @abstractmethod
    def disconnect(self) -> bool:
        """Verbindung trennen. Returns True bei Erfolg."""
        ...

    @abstractmethod
    def send_message(self, recipient: str, content: str,
                     attachments: Optional[List[str]] = None) -> bool:
        """Nachricht senden. Returns True bei Erfolg."""
        ...

    @abstractmethod
    def get_messages(self, since: Optional[str] = None,
                     limit: int = 50) -> List[Message]:
        """Nachrichten abrufen seit Zeitstempel (ISO-8601)."""
        ...

    def get_status(self) -> ConnectorStatus:
        """Aktuellen Status abfragen."""
        return self._status

    def _warn_attachments_unsupported(
        self, attachments: Optional[List[str]]
    ) -> None:
        """Warnt laut, wenn attachments uebergeben wurden, die dieser
        Connector nicht unterstuetzt — statt sie still zu verschlucken
        (send_message gaebe sonst True zurueck, obwohl die Datei nie
        verschickt wurde)."""
        if attachments:
            import sys
            print(
                f"[{self.config.connector_type}] WARNUNG: attachments werden "
                "von diesem Connector nicht unterstuetzt und wurden NICHT "
                "gesendet.",
                file=sys.stderr,
            )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name={self.name} status={self._status.value}>"
        )

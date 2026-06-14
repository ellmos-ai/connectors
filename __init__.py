# -*- coding: utf-8 -*-
"""
connectors — Standalone Messaging-Connector-Modul
==================================================

Einheitliches Interface für Messaging-Plattformen: Telegram, Discord,
Signal, WhatsApp, Home Assistant, generische Webhooks.

Standalone (kein Framework nötig):

    import os
    from connectors import create_connector, ConnectorConfig

    config = ConnectorConfig(
        name="my_bot",
        connector_type="telegram",
        auth_config={"bot_token": os.environ["TG_BOT_TOKEN"]},
    )
    conn = create_connector(config)
    conn.connect()
    conn.send_message("CHAT_ID", "Hallo!")

Mit SecretAdapter (optionale Framework-Integration):

    from connectors import create_connector, ConnectorConfig
    from connectors.base import SecretAdapter

    class MyAdapter(SecretAdapter):
        def get_secret(self, key: str) -> str:
            return my_vault.get(key, "")

    conn = create_connector(config, secret_adapter=MyAdapter())

Unterstützte Connector-Typen:
    telegram, discord, signal, whatsapp, homeassistant, webhook

MIT License — siehe LICENSE
"""

__version__ = "1.0.0"
__author__ = "connectors contributors"

from connectors.base import (
    BaseConnector,
    ConnectorConfig,
    ConnectorStatus,
    Message,
    SecretAdapter,
)

# Lazy Imports — nur laden wenn tatsächlich genutzt
_CONNECTOR_MAP = {
    "telegram": ("connectors.telegram_connector", "TelegramConnector"),
    "discord": ("connectors.discord_connector", "DiscordConnector"),
    "signal": ("connectors.signal_connector", "SignalConnector"),
    "whatsapp": ("connectors.whatsapp_connector", "WhatsAppConnector"),
    "homeassistant": ("connectors.homeassistant_connector", "HomeAssistantConnector"),
    "webhook": ("connectors.webhook_connector", "WebhookConnector"),
}

SUPPORTED_TYPES = list(_CONNECTOR_MAP.keys())


def create_connector(
    config: ConnectorConfig,
    secret_adapter: "SecretAdapter | None" = None,
) -> BaseConnector:
    """Factory: Erzeugt den passenden Connector für config.connector_type.

    Args:
        config:         ConnectorConfig mit connector_type gesetzt.
        secret_adapter: Optionaler SecretAdapter für Framework-Integration.

    Returns:
        Instanz des passenden BaseConnector-Subtyps.

    Raises:
        ValueError: Wenn connector_type nicht unterstützt wird.
    """
    ctype = config.connector_type.lower()
    if ctype not in _CONNECTOR_MAP:
        raise ValueError(
            f"Connector-Typ '{ctype}' nicht unterstützt. "
            f"Verfügbar: {', '.join(SUPPORTED_TYPES)}"
        )

    module_path, class_name = _CONNECTOR_MAP[ctype]
    import importlib
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(config, secret_adapter=secret_adapter)


__all__ = [
    "BaseConnector",
    "ConnectorConfig",
    "ConnectorStatus",
    "Message",
    "SecretAdapter",
    "create_connector",
    "SUPPORTED_TYPES",
]

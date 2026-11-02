# -*- coding: utf-8 -*-
"""
hermes_gateway — MIT-compatible Gateway Config Importer & Multi-Channel Router
===============================================================================

Adapted from MIT-licensed gateway patterns (NousResearch/hermes-agent, MIT License):
normalizes external gateway definitions (Telegram, Discord, Slack, WhatsApp, Signal,
Home Assistant, Webhook) into canonical `ConnectorConfig` instances while stripping
raw plaintext secrets in favor of environment variable references.

MIT License — see LICENSE
"""

from __future__ import annotations

from typing import Any

from connectors.base import ConnectorConfig

SUPPORTED_GATEWAY_PLATFORMS = {
    "telegram",
    "discord",
    "slack",
    "whatsapp",
    "signal",
    "homeassistant",
    "webhook",
    "imessage",
}


def import_hermes_gateway_config(raw_gateway: dict[str, Any]) -> list[ConnectorConfig]:
    """Convert a Hermes/OpenClaw-style `gateways` dict into `ConnectorConfig` objects."""
    if not isinstance(raw_gateway, dict):
        raise ValueError("raw_gateway must be a dictionary")

    channels = raw_gateway.get("platforms") or raw_gateway.get("gateways") or raw_gateway
    configs: list[ConnectorConfig] = []

    for platform, spec in sorted(channels.items()):
        ctype = str(platform).strip().lower()
        if ctype not in SUPPORTED_GATEWAY_PLATFORMS or not isinstance(spec, dict):
            continue
        if spec.get("enabled", True) is False:
            continue
        name = str(spec.get("name") or f"hermes_{ctype}")
        endpoint = str(spec.get("endpoint") or spec.get("base_url") or "")
        auth_cfg: dict[str, Any] = {}
        for k in ("token_env", "bot_token_env", "api_key_env", "secret_ref"):
            if k in spec and isinstance(spec[k], str):
                auth_cfg[k] = spec[k].strip()
        options: dict[str, Any] = {
            "allowlist_chat_ids": list(spec.get("allowlist_chat_ids", [])),
            "voice_memo_stt": bool(spec.get("voice_memo_stt", True)),
            "source_schema": "hermes-gateway-mit-v1",
        }
        configs.append(
            ConnectorConfig(
                name=name,
                connector_type=ctype,
                endpoint=endpoint,
                auth_config=auth_cfg,
                options=options,
            )
        )
    return configs

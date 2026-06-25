#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Smoke Tests for connectors module.

Verifies that all public symbols are importable without BACH or external
dependencies. No real credentials required.

Run:
    python -m pytest tests/ -v
    # or without pytest:
    python tests/test_imports.py
"""

import sys
import os
import importlib.util

# Allow running from any directory: add the parent of the 'connectors' package
# directory when the checkout directory is named 'connectors'. In arbitrary
# temp clones, load the local root package under the canonical package name.
_here = os.path.dirname(os.path.abspath(__file__))
_pkg_root = os.path.dirname(_here)      # connectors/
_modules_root = os.path.dirname(_pkg_root)  # .MODULES/

if os.path.basename(_pkg_root) == "connectors":
    sys.path.insert(0, _modules_root)
elif "connectors" not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        "connectors",
        os.path.join(_pkg_root, "__init__.py"),
        submodule_search_locations=[_pkg_root],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["connectors"] = module
    spec.loader.exec_module(module)


def test_base_imports():
    """All base types importable."""
    from connectors.base import (
        BaseConnector,
        ConnectorConfig,
        ConnectorStatus,
        Message,
        SecretAdapter,
    )
    assert BaseConnector is not None
    assert ConnectorConfig is not None
    assert ConnectorStatus is not None
    assert Message is not None
    assert SecretAdapter is not None


def test_package_imports():
    """Top-level package exports importable."""
    from connectors import create_connector, ConnectorConfig, SUPPORTED_TYPES
    assert callable(create_connector)
    assert isinstance(SUPPORTED_TYPES, list)
    assert len(SUPPORTED_TYPES) >= 6


def test_connector_imports():
    """All connector classes importable individually."""
    from connectors.telegram_connector import TelegramConnector
    from connectors.discord_connector import DiscordConnector
    from connectors.signal_connector import SignalConnector
    from connectors.whatsapp_connector import WhatsAppConnector
    from connectors.homeassistant_connector import HomeAssistantConnector
    from connectors.webhook_connector import WebhookConnector

    for cls in (
        TelegramConnector,
        DiscordConnector,
        SignalConnector,
        WhatsAppConnector,
        HomeAssistantConnector,
        WebhookConnector,
    ):
        assert cls is not None, f"{cls} should not be None"


def test_create_connector_factory():
    """create_connector() produces the right class for each type."""
    from connectors import create_connector, ConnectorConfig

    test_cases = [
        ("telegram", "TelegramConnector"),
        ("discord", "DiscordConnector"),
        ("signal", "SignalConnector"),
        ("whatsapp", "WhatsAppConnector"),
        ("homeassistant", "HomeAssistantConnector"),
        ("webhook", "WebhookConnector"),
    ]

    for ctype, expected_class in test_cases:
        config = ConnectorConfig(name=f"test_{ctype}", connector_type=ctype)
        conn = create_connector(config)
        assert type(conn).__name__ == expected_class, (
            f"Expected {expected_class}, got {type(conn).__name__}"
        )


def test_create_connector_unknown_type():
    """create_connector() raises ValueError for unknown type."""
    from connectors import create_connector, ConnectorConfig
    config = ConnectorConfig(name="bad", connector_type="nonexistent")
    try:
        create_connector(config)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_secret_adapter_interface():
    """SecretAdapter can be subclassed without BACH."""
    from connectors.base import SecretAdapter

    class MockAdapter(SecretAdapter):
        def get_secret(self, key: str) -> str:
            return f"mock_{key}"

    adapter = MockAdapter()
    assert adapter.get_secret("foo") == "mock_foo"


def test_message_dataclass():
    """Message dataclass instantiable with defaults."""
    from connectors.base import Message
    msg = Message(
        channel="telegram",
        sender="123",
        content="Hello",
        timestamp="2026-06-14T00:00:00",
    )
    assert msg.channel == "telegram"
    assert msg.attachments == []
    assert msg.direction == "in"


def test_connector_config_defaults():
    """ConnectorConfig works with minimal arguments."""
    from connectors.base import ConnectorConfig
    cfg = ConnectorConfig(name="test", connector_type="webhook")
    assert cfg.endpoint == ""
    assert cfg.auth_type == "none"
    assert cfg.auth_config == {}


if __name__ == "__main__":
    tests = [
        test_base_imports,
        test_package_imports,
        test_connector_imports,
        test_create_connector_factory,
        test_create_connector_unknown_type,
        test_secret_adapter_interface,
        test_message_dataclass,
        test_connector_config_defaults,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  OK  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)

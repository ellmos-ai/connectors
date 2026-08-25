# -*- coding: utf-8 -*-
"""Offline contracts for setup-wizard templates.

The tests deliberately render with sentinel credentials and never connect to
Signal, Discord, or any other external platform.
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Mirror the repository's import smoke-test bootstrap so the suite also works
# from temp clones whose checkout directory is not literally named connectors.
ROOT = Path(__file__).resolve().parents[1]
if ROOT.name == "connectors":
    sys.path.insert(0, str(ROOT.parent))
elif "connectors" not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        "connectors",
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["connectors"] = module
    spec.loader.exec_module(module)

from connectors.base import ConnectorConfig
from connectors.discord_connector import DiscordConnector
from connectors.signal_connector import SignalConnector
from connectors.templates.setup_wizard import SetupWizard


TEMPLATES = ROOT / "templates"


def _wizard(output_dir: Path) -> SetupWizard:
    wizard = SetupWizard()
    wizard.templates_dir = TEMPLATES
    wizard.connectors_dir = output_dir
    return wizard


def test_signal_and_discord_are_in_template_inventory(tmp_path):
    templates = _wizard(tmp_path).list_templates()

    assert templates == sorted(templates)
    assert {"signal", "discord"}.issubset(templates)


@pytest.mark.parametrize(
    ("template_name", "expected_questions"),
    [
        (
            "signal",
            {
                "phone_number": "auth_config",
                "signal_cli_path": "options",
                "last_timestamp": "options",
            },
        ),
        (
            "discord",
            {
                "bot_token": "auth_config",
                "webhook_url": "endpoint",
                "default_channel": "options",
                "last_message_id": "options",
            },
        ),
    ],
)
def test_template_questions_match_connector_config_storage(
    tmp_path, template_name, expected_questions
):
    template = _wizard(tmp_path).load_template(template_name)

    assert template is not None
    assert {
        question["name"]: question["storage"]
        for question in template["setup_questions"]
    } == expected_questions


def test_wizard_maps_discord_endpoint_without_persisting_it_in_source(tmp_path):
    wizard = _wizard(tmp_path)
    template = wizard.load_template("discord")
    secret_token = "sentinel-discord-token"
    secret_webhook = "https://sentinel.invalid/webhook"

    with patch("builtins.input", side_effect=["discord_test", "123", "456"]), patch.object(
        wizard, "_input_secret", side_effect=[secret_token, secret_webhook]
    ):
        gathered = wizard.gather_configuration(template)

    assert gathered == {
        "instance_name": "discord_test",
        "endpoint": secret_webhook,
        "auth_config": {"bot_token": secret_token},
        "options": {"default_channel": "123", "last_message_id": "456"},
    }

    rendered_path = wizard.generate_connector(template, gathered)
    rendered = rendered_path.read_text(encoding="utf-8")
    assert secret_token not in rendered
    assert secret_webhook not in rendered


@pytest.mark.parametrize(
    ("template_name", "expected_fragments"),
    [
        (
            "signal",
            [
                'os.environ["SIGNAL_PHONE_NUMBER"]',
                'config.auth_config.get("phone_number", "")',
                'config.options.get("signal_cli_path", "signal-cli")',
                'config.options.get("last_timestamp", 0)',
            ],
        ),
        (
            "discord",
            [
                'endpoint=os.environ.get("DISCORD_WEBHOOK_URL", "")',
                'self._resolve_secret(config.auth_config, "bot_token")',
                'config.options.get("last_message_id", "")',
                'self.config.options.get("default_channel", "")',
            ],
        ),
    ],
)
def test_rendering_is_deterministic_compilable_and_credential_free(
    tmp_path, template_name, expected_fragments
):
    wizard = _wizard(tmp_path)
    template = wizard.load_template(template_name)
    first_config = {
        "instance_name": f"{template_name}_test",
        "endpoint": "https://first-secret.invalid",
        "auth_config": {"token": "first-secret-token"},
        "options": {},
    }
    second_config = {
        **first_config,
        "endpoint": "https://second-secret.invalid",
        "auth_config": {"token": "second-secret-token"},
    }

    first_path = wizard.generate_connector(template, first_config)
    first = first_path.read_text(encoding="utf-8")
    second_path = wizard.generate_connector(template, second_config)
    second = second_path.read_text(encoding="utf-8")

    assert first == second
    assert "secret-token" not in first
    assert "secret.invalid" not in first
    assert "{{" not in first and "}}" not in first
    for fragment in expected_fragments:
        assert fragment in first
    compile(first, str(first_path), "exec")


def test_templates_feed_the_real_connector_contracts_without_connections():
    signal_config = ConnectorConfig(
        name="signal_test",
        connector_type="signal",
        auth_config={"phone_number": "+49000000000"},
        options={"signal_cli_path": "signal-cli-test", "last_timestamp": 17},
    )
    signal = SignalConnector(signal_config)
    assert signal._phone_number == "+49000000000"
    assert signal._signal_cli_path == "signal-cli-test"
    assert signal._last_timestamp == 17

    discord_config = ConnectorConfig(
        name="discord_test",
        connector_type="discord",
        endpoint="https://example.invalid/webhook",
        auth_type="api_key",
        auth_config={"bot_token": "offline-token"},
        options={"default_channel": "123", "last_message_id": "456"},
    )
    discord = DiscordConnector(discord_config)
    assert discord._bot_token == "offline-token"
    assert discord._webhook_url == "https://example.invalid/webhook"
    assert discord._last_message_id == "456"
    assert discord.config.options["default_channel"] == "123"

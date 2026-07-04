# -*- coding: utf-8 -*-
"""Behavior tests: secret resolution, secret-safe repr, attachments contract,
webhook JSON escaping, factory semantics.

Complements tests/test_imports.py (structure-only smokes) with the unit tests
requested in TODO ("Unit-Tests fuer BaseConnector, create_connector() Factory,
Fehlerfaelle"). No network, no real secrets — everything mocked.
"""
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from connectors.base import (  # noqa: E402
    BaseConnector, ConnectorConfig, SecretAdapter,
)
from connectors import create_connector  # noqa: E402


class DictAdapter(SecretAdapter):
    def __init__(self, data):
        self._data = data

    def get_secret(self, key):
        return self._data.get(key)


class DummyConnector(BaseConnector):
    """Minimal konkreter Connector fuer Base-Tests."""

    def connect(self):
        return True

    def disconnect(self):
        return True

    def send_message(self, recipient, content, attachments=None):
        self._warn_attachments_unsupported(attachments)
        return True

    def get_messages(self, since=None, limit=50):
        return []


def _cfg(**kw):
    base = dict(name="t", connector_type="dummy")
    base.update(kw)
    return ConnectorConfig(**base)


class TestResolveSecret(unittest.TestCase):
    def test_direct_value_wins(self):
        conn = DummyConnector(_cfg(auth_config={"tok": "direct"}),
                              secret_adapter=DictAdapter({"ref": "adapted"}))
        self.assertEqual(conn._resolve_secret(conn.config.auth_config, "tok"),
                         "direct")

    def test_secret_refs_via_adapter(self):
        cfg = _cfg(auth_config={"_secret_refs": {"tok": "ref"}})
        conn = DummyConnector(cfg, secret_adapter=DictAdapter({"ref": "adapted"}))
        self.assertEqual(conn._resolve_secret(cfg.auth_config, "tok"), "adapted")

    def test_secret_refs_without_adapter_empty(self):
        cfg = _cfg(auth_config={"_secret_refs": {"tok": "ref"}})
        conn = DummyConnector(cfg)
        self.assertEqual(conn._resolve_secret(cfg.auth_config, "tok"), "")

    def test_missing_key_empty(self):
        conn = DummyConnector(_cfg())
        self.assertEqual(conn._resolve_secret({}, "tok"), "")

    def test_adapter_none_result_becomes_empty(self):
        cfg = _cfg(auth_config={"_secret_refs": {"tok": "missing"}})
        conn = DummyConnector(cfg, secret_adapter=DictAdapter({}))
        self.assertEqual(conn._resolve_secret(cfg.auth_config, "tok"), "")


class TestSecretSafety(unittest.TestCase):
    def test_config_repr_hides_auth_config(self):
        cfg = _cfg(auth_config={"bot_token": "SUPERSECRET"})
        self.assertNotIn("SUPERSECRET", repr(cfg))

    def test_connector_repr_hides_auth_config(self):
        conn = DummyConnector(_cfg(auth_config={"bot_token": "SUPERSECRET"}))
        self.assertNotIn("SUPERSECRET", repr(conn))


class TestAttachmentsContract(unittest.TestCase):
    def test_unsupported_attachments_warn_on_stderr(self):
        conn = DummyConnector(_cfg())
        buf = io.StringIO()
        with mock.patch.object(sys, "stderr", buf):
            conn.send_message("x", "hallo", attachments=["a.pdf"])
        self.assertIn("NICHT gesendet", buf.getvalue())

    def test_no_attachments_no_warning(self):
        conn = DummyConnector(_cfg())
        buf = io.StringIO()
        with mock.patch.object(sys, "stderr", buf):
            conn.send_message("x", "hallo")
        self.assertEqual(buf.getvalue(), "")


class TestWebhookPayload(unittest.TestCase):
    def _send(self, content):
        cfg = ConnectorConfig(name="w", connector_type="webhook",
                              endpoint="http://127.0.0.1:9/hook")
        conn = create_connector(cfg)
        captured = {}

        class _Resp:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def fake_urlopen(req, timeout=0):
            captured["body"] = req.data.decode("utf-8")
            return _Resp()

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            ok = conn.send_message("", content)
        self.assertTrue(ok)
        return captured["body"]

    def test_multiline_and_quotes_produce_valid_json(self):
        content = 'Zeile1\nZeile2 "quoted" \\ backslash\tTab'
        body = self._send(content)
        parsed = json.loads(body)  # ungueltiges JSON wuerde hier werfen
        self.assertEqual(parsed["text"], content)

    def test_umlauts_survive(self):
        body = self._send("Grüße äöüß")
        parsed = json.loads(body)
        self.assertIn("Grüße äöüß", str(parsed))


class TestFactory(unittest.TestCase):
    def test_case_insensitive_type(self):
        cfg = ConnectorConfig(name="w", connector_type="Webhook",
                              endpoint="http://127.0.0.1:9/hook")
        conn = create_connector(cfg)
        self.assertEqual(conn.connector_type, "Webhook")

    def test_unknown_type_raises_value_error(self):
        with self.assertRaises(ValueError):
            create_connector(ConnectorConfig(name="x", connector_type="nope"))

    def test_secret_adapter_passed_through(self):
        adapter = DictAdapter({"k": "v"})
        cfg = ConnectorConfig(name="w", connector_type="webhook",
                              endpoint="http://127.0.0.1:9/hook")
        conn = create_connector(cfg, secret_adapter=adapter)
        self.assertIs(conn._secret_adapter, adapter)

    def test_base_connector_is_abstract(self):
        with self.assertRaises(TypeError):
            BaseConnector(_cfg())  # type: ignore[abstract]


if __name__ == "__main__":
    unittest.main()

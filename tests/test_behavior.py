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


class TestSlackConnector(unittest.TestCase):
    def test_slack_webhook_connect_and_send(self):
        from connectors.slack_connector import SlackConnector

        captured = {}

        class DummyResponse:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return b"ok"

        def fake_urlopen(req, timeout=15):
            captured["url"] = req.full_url
            captured["data"] = json.loads(req.data.decode("utf-8"))
            return DummyResponse()

        cfg = ConnectorConfig(
            name="slack_wh",
            connector_type="slack",
            endpoint="https://hooks.slack.com/services/T00/B00/X00",
        )
        conn = SlackConnector(cfg)
        self.assertTrue(conn.connect())

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            ok = conn.send_message("C123", "Test Nachricht")
            self.assertTrue(ok)
            self.assertEqual(captured["url"], "https://hooks.slack.com/services/T00/B00/X00")
            self.assertEqual(captured["data"]["text"], "Test Nachricht")
            self.assertEqual(captured["data"]["channel"], "C123")

    def test_slack_bot_connect_and_send(self):
        from connectors.slack_connector import SlackConnector

        captured = {}

        class DummyResponse:
            status = 200
            def __init__(self, payload): self._payload = payload
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return json.dumps(self._payload).encode("utf-8")

        def fake_urlopen(req, timeout=15):
            captured["auth"] = req.headers.get("Authorization")
            if "auth.test" in req.full_url:
                return DummyResponse({"ok": True, "user_id": "U123", "team_id": "T456"})
            if "chat.postMessage" in req.full_url:
                captured["body"] = json.loads(req.data.decode("utf-8"))
                return DummyResponse({"ok": True, "ts": "1700000000.000100"})
            return DummyResponse({"ok": False})

        cfg = ConnectorConfig(
            name="slack_bot",
            connector_type="slack",
            auth_config={"bot_token": "xoxb-secret-token"},
            options={"default_channel": "C999"},
        )
        conn = SlackConnector(cfg)

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            self.assertTrue(conn.connect())
            self.assertEqual(captured["auth"], "Bearer xoxb-secret-token")

            ok = conn.send_message("", "Hallo Slack Bot!")
            self.assertTrue(ok)
            self.assertEqual(captured["body"]["channel"], "C999")
            self.assertEqual(captured["body"]["text"], "Hallo Slack Bot!")


class TestIMessageConnector(unittest.TestCase):
    def setUp(self):
        import tempfile
        import sqlite3
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "chat.db"

        # Create mock chat.db SQLite schema
        conn = sqlite3.connect(str(self.db_path))
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE handle (
                ROWID INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE message (
                ROWID INTEGER PRIMARY KEY AUTOINCREMENT,
                guid TEXT NOT NULL,
                text TEXT,
                handle_id INTEGER,
                date INTEGER,
                is_from_me INTEGER
            );
        """)
        # Insert test handle
        cur.execute("INSERT INTO handle (id) VALUES ('+491701234567')")
        # Insert test messages (Apple epoch nano: ~2024-01-01)
        # 2024-01-01 = 1704067200 unix = 725760000 apple sec = 725760000000000000 apple nano
        cur.execute("""
            INSERT INTO message (guid, text, handle_id, date, is_from_me)
            VALUES ('msg-1', 'Hallo iMessage', 1, 725760000000000000, 0)
        """)
        cur.execute("""
            INSERT INTO message (guid, text, handle_id, date, is_from_me)
            VALUES ('msg-2', 'Antwort zurück', 1, 725760010000000000, 1)
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_imessage_connect_with_db(self):
        from connectors.imessage_connector import iMessageConnector
        from connectors.base import ConnectorStatus

        cfg = ConnectorConfig(
            name="imsg_test",
            connector_type="imessage",
            options={"chat_db_path": str(self.db_path)},
        )
        conn = iMessageConnector(cfg)
        self.assertTrue(conn.connect())
        self.assertEqual(conn.status, ConnectorStatus.CONNECTED)

    def test_imessage_get_messages(self):
        from connectors.imessage_connector import iMessageConnector

        cfg = ConnectorConfig(
            name="imsg_test",
            connector_type="imessage",
            options={"chat_db_path": str(self.db_path)},
        )
        conn = iMessageConnector(cfg)
        msgs = conn.get_messages(limit=10)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0].content, "Hallo iMessage")
        self.assertEqual(msgs[0].sender, "+491701234567")
        self.assertEqual(msgs[0].direction, "in")
        self.assertEqual(msgs[1].content, "Antwort zurück")
        self.assertEqual(msgs[1].direction, "out")

    def test_imessage_send_message_darwin(self):
        from connectors.imessage_connector import iMessageConnector

        cfg = ConnectorConfig(
            name="imsg_test",
            connector_type="imessage",
            options={"chat_db_path": str(self.db_path), "default_recipient": "+491701234567"},
        )
        conn = iMessageConnector(cfg)

        captured_cmd = []

        def fake_run(cmd, *args, **kwargs):
            captured_cmd.extend(cmd)
            class Res:
                returncode = 0
            return Res()

        with mock.patch.object(conn, "is_darwin", return_value=True):
            with mock.patch("subprocess.run", side_effect=fake_run):
                ok = conn.send_message("", "Testnachricht")
                self.assertTrue(ok)
                self.assertIn("osascript", captured_cmd)
                self.assertIn("+491701234567", captured_cmd)
                self.assertIn("Testnachricht", captured_cmd)

    def test_imessage_fail_closed_non_darwin(self):
        from connectors.imessage_connector import iMessageConnector

        cfg = ConnectorConfig(
            name="imsg_test",
            connector_type="imessage",
            options={"chat_db_path": "/nonexistent/path/chat.db"},
        )
        conn = iMessageConnector(cfg)
        with mock.patch.object(conn, "is_darwin", return_value=False):
            self.assertFalse(conn.connect())
            self.assertFalse(conn.send_message("+491701234567", "Hallo"))


if __name__ == "__main__":
    unittest.main()

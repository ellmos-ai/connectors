# -*- coding: utf-8 -*-
"""HomeAssistantConnector: URL-path / SSRF hardening (PB-13, #3996). No network."""
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from connectors.base import ConnectorConfig
from connectors.homeassistant_connector import HomeAssistantConnector

URLOPEN = "connectors.homeassistant_connector.urllib.request.urlopen"


def _ha():
    return HomeAssistantConnector(ConnectorConfig(
        name="ha", connector_type="homeassistant",
        endpoint="http://127.0.0.1:8123", auth_type="token",
        auth_config={"access_token": "t"},
    ))


def _ok():
    resp = mock.MagicMock()
    resp.read.return_value = json.dumps([]).encode()
    resp.__enter__.return_value = resp
    return resp


BAD_NAMES = ["../config", "light/turn_on", "turn_on?x=1", "turn_on#f", "http://evil/x",
             "turn on", "Turn_On", "", "a.b", "..", "turn_on\n"]
BAD_ENTITIES = ["../../config", "light", "light.", ".a", "light/a.b", "light.a b",
                "light.a?x", "light.a#x", "http://evil/a.b", "LIGHT.a", "light.a.b", "all", ""]


class TestCallServiceValidation(unittest.TestCase):
    def test_valid_call_goes_out(self):
        with mock.patch(URLOPEN, return_value=_ok()) as m:
            self.assertTrue(_ha().call_service("light", "turn_on", {"entity_id": "light.wohnzimmer"}))
        self.assertEqual(m.call_args[0][0].full_url, "http://127.0.0.1:8123/api/services/light/turn_on")

    def test_bad_domain_or_service_rejected_without_network(self):
        for bad in BAD_NAMES:
            for args in ((bad, "turn_on"), ("light", bad)):
                with self.subTest(args=args), mock.patch(URLOPEN) as m:
                    self.assertFalse(_ha().call_service(*args))
                    m.assert_not_called()

    def test_bad_entity_id_in_data_rejected_without_network(self):
        for bad in BAD_ENTITIES:
            for data in ({"entity_id": bad}, {"entity_id": ["light.ok", bad]}):
                with self.subTest(data=data), mock.patch(URLOPEN) as m:
                    self.assertFalse(_ha().call_service("light", "turn_on", data))
                    m.assert_not_called()

    def test_entity_id_list_and_non_string_types(self):
        with mock.patch(URLOPEN, return_value=_ok()):
            self.assertTrue(_ha().call_service("light", "turn_on", {"entity_id": ["light.a", "light.b"]}))
        for bad in (5, {"x": 1}, None):
            with self.subTest(bad=bad), mock.patch(URLOPEN) as m:
                self.assertFalse(_ha().call_service("light", "turn_on", {"entity_id": bad}))
                m.assert_not_called()

    def test_blocked_domains_rejected_without_network(self):
        for dom in ("shell_command", "command_line", "python_script", "pyscript", "hassio", "rest_command"):
            with self.subTest(dom=dom), mock.patch(URLOPEN) as m:
                self.assertFalse(_ha().call_service(dom, "run", {}))
                m.assert_not_called()

    def test_send_message_accepts_notify_prefix(self):
        with mock.patch(URLOPEN, return_value=_ok()) as m:
            self.assertTrue(_ha().send_message("notify.mobile_app_phone", "hi"))
        self.assertTrue(m.call_args[0][0].full_url.endswith("/api/services/notify/mobile_app_phone"))


class TestOtherUrlBuilders(unittest.TestCase):
    def test_get_state_history_event_reject_bad_input(self):
        ha = _ha()
        with mock.patch(URLOPEN) as m:
            self.assertIsNone(ha.get_state("../../config"))
            self.assertEqual(ha.get_history("light.a&x=1"), [])
            self.assertFalse(ha.fire_event("../x"))
            m.assert_not_called()

    def test_get_state_valid_goes_out(self):
        with mock.patch(URLOPEN, return_value=_ok()) as m:
            _ha().get_state("sensor.temperature_1")
        self.assertTrue(m.call_args[0][0].full_url.endswith("/api/states/sensor.temperature_1"))


if __name__ == "__main__":
    unittest.main()

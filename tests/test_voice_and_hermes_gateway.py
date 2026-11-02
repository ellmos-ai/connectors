# -*- coding: utf-8 -*-
"""Tests for VoiceMemoTranscriber and Hermes MIT gateway config importer (#3768)."""

from __future__ import annotations

import pytest

from connectors.hermes_gateway import import_hermes_gateway_config
from connectors.voice_memo_transcriber import VoiceMemoTranscriber


def test_voice_memo_transcriber_enriches_message():
    transcriber = VoiceMemoTranscriber(
        default_language="de",
        speech_to_text_enabled=True,
        transcribe_fn=lambda data, suffix, lang: f"[{lang}:{suffix}:{len(data)}] Hallo Ocean",
    )
    msg = {"sender": "lukas", "voice_bytes": b"OggS-audio-payload", "voice_suffix": ".ogg"}
    enriched = transcriber.enrich_message_payload(msg)
    assert enriched["voice_transcript"] == "[de:.ogg:18] Hallo Ocean"
    assert enriched["text"] == "[de:.ogg:18] Hallo Ocean"


def test_voice_memo_transcriber_respects_permission_gate():
    transcriber = VoiceMemoTranscriber(speech_to_text_enabled=False)
    with pytest.raises(PermissionError, match="speech_to_text=False"):
        transcriber.transcribe_audio_bytes(b"OggS")
    enriched = transcriber.enrich_message_payload({"voice_bytes": b"OggS"})
    assert enriched["voice_transcription_skipped"] == "permission_disabled"


def test_import_hermes_gateway_config():
    sample = {
        "platforms": {
            "telegram": {
                "enabled": True,
                "name": "ocean_tg",
                "bot_token_env": "TELEGRAM_BOT_TOKEN",
                "allowlist_chat_ids": ["12345"],
                "voice_memo_stt": True,
            },
            "discord": {
                "enabled": False,
                "name": "disabled_dc",
            },
        }
    }
    configs = import_hermes_gateway_config(sample)
    assert len(configs) == 1
    assert configs[0].connector_type == "telegram"
    assert configs[0].auth_config["bot_token_env"] == "TELEGRAM_BOT_TOKEN"
    assert configs[0].options["voice_memo_stt"] is True

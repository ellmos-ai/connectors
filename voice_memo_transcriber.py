# -*- coding: utf-8 -*-
"""
voice_memo_transcriber — Automatic voice-memo transcription for Messaging Connectors
=====================================================================================

Uses `ellmos-voice-io` (`VoiceIO.transcribe_bytes` / `SpeechToText.transcribe_file`)
to automatically transcribe incoming voice memos from Telegram, WhatsApp, Discord,
and Signal messages when `speech_to_text` permission is enabled.

MIT License — see LICENSE
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


class VoiceMemoTranscriber:
    """Transcribes incoming connector voice attachments using ellmos-voice-io."""

    def __init__(
        self,
        *,
        default_language: str = "de",
        speech_to_text_enabled: bool = True,
        transcribe_fn: Callable[[bytes, str, str], str] | None = None,
    ):
        self.default_language = default_language
        self.speech_to_text_enabled = speech_to_text_enabled
        self._transcribe_fn = transcribe_fn

    def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        *,
        suffix: str = ".ogg",
        language: str | None = None,
    ) -> str:
        if not self.speech_to_text_enabled:
            raise PermissionError("Speech-to-text is disabled in Permissions (speech_to_text=False).")
        if not audio_bytes:
            raise ValueError("audio_bytes must not be empty")
        lang = language or self.default_language
        if self._transcribe_fn is not None:
            return self._transcribe_fn(audio_bytes, suffix, lang)
        from ellmos_voice_io.service import VoiceIO

        return VoiceIO().transcribe_bytes(audio_bytes, suffix=suffix, language=lang)

    def enrich_message_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """If `payload` contains `voice_bytes` or `audio_path`, attach `voice_transcript`."""
        enriched = dict(payload)
        if not self.speech_to_text_enabled:
            enriched["voice_transcription_skipped"] = "permission_disabled"
            return enriched

        lang = str(enriched.get("language") or self.default_language)
        if isinstance(enriched.get("voice_bytes"), (bytes, bytearray)) and enriched["voice_bytes"]:
            suffix = str(enriched.get("voice_suffix") or ".ogg")
            transcript = self.transcribe_audio_bytes(bytes(enriched["voice_bytes"]), suffix=suffix, language=lang)
            enriched["voice_transcript"] = transcript
            if not enriched.get("text"):
                enriched["text"] = transcript
        elif enriched.get("audio_path"):
            p = Path(str(enriched["audio_path"]))
            if p.is_file():
                transcript = self.transcribe_audio_bytes(
                    p.read_bytes(),
                    suffix=p.suffix or ".wav",
                    language=lang,
                )
                enriched["voice_transcript"] = transcript
                if not enriched.get("text"):
                    enriched["text"] = transcript
        return enriched

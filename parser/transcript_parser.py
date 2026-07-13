"""
parsers/transcript_parser.py

Parser for Whisper / WhisperX transcript JSON.

Supported inputs:
- WhisperX diarized JSON with speaker labels
- Whisper JSON with segments
- Already loaded dict objects
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from models.transcript import ParsedTranscript, TranscriptTurn
from services.speaker_role_resolver import SpeakerRoleResolver


class TranscriptParser:
    """
    Converts raw transcript JSON into a normalized ParsedTranscript.
    """

    BOT_SPEAKER_LABELS = {"bot", "agent", "assistant", "ivr"}
    CUSTOMER_SPEAKER_LABELS = {"customer", "user", "caller"}

    def __init__(self) -> None:
        self.role_resolver = SpeakerRoleResolver()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_file(self, file_path: str | Path) -> ParsedTranscript:
        """
        Load transcript JSON file and parse it.
        """
        path = Path(file_path)
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return self.parse_dict(data)

    def parse_dict(self, data: Dict[str, Any]) -> ParsedTranscript:
        """
        Parse transcript JSON dict into ParsedTranscript.
        """
        segments = self._extract_segments(data)

        # Resolve speaker_00 / speaker_01 etc. into bot/customer
        resolution = self.role_resolver.resolve(segments)

        turns: List[TranscriptTurn] = []
        for segment in segments:
            turn = self._segment_to_turn(segment, resolution.mapping)
            if turn:
                turns.append(turn)

        return ParsedTranscript(turns=turns)

    # ------------------------------------------------------------------
    # Segment extraction
    # ------------------------------------------------------------------

    def _extract_segments(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract segment list from different transcript shapes.

        Supported shapes:
        1. {"segments": [...]}
        2. {"result": {"segments": [...]}}
        """
        if isinstance(data, dict):
            if isinstance(data.get("segments"), list):
                return data["segments"]

            result = data.get("result")
            if isinstance(result, dict) and isinstance(result.get("segments"), list):
                return result["segments"]

        return []

    # ------------------------------------------------------------------
    # Segment -> Turn mapping
    # ------------------------------------------------------------------

    def _segment_to_turn(
        self,
        segment: Dict[str, Any],
        speaker_mapping: Dict[str, str],
    ) -> Optional[TranscriptTurn]:
        """
        Convert one transcript segment into TranscriptTurn.
        """
        text = self._clean_text(segment.get("text", ""))
        if not text:
            return None

        speaker = self._normalize_speaker(segment, speaker_mapping)

        return TranscriptTurn(
            speaker=speaker,
            text=text,
            start=self._to_float(segment.get("start")),
            end=self._to_float(segment.get("end")),
        )

    def _normalize_speaker(
        self,
        segment: Dict[str, Any],
        speaker_mapping: Dict[str, str],
    ) -> str:
        """
        Normalize speaker labels into:
        - bot
        - customer
        - unknown
        """
        raw_speaker = (
            segment.get("speaker")
            or segment.get("speaker_label")
            or segment.get("role")
            or ""
        )
        speaker = str(raw_speaker).strip().lower()

        # Direct semantic labels
        if speaker in self.BOT_SPEAKER_LABELS:
            return "bot"

        if speaker in self.CUSTOMER_SPEAKER_LABELS:
            return "customer"

        # Diarization labels -> resolved role
        if speaker in speaker_mapping:
            return speaker_mapping[speaker]

        return "unknown"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_text(text: Any) -> str:
        if text is None:
            return ""
        return " ".join(str(text).split()).strip()

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
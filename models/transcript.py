"""
models/transcript.py

Domain models for parsed conversation transcripts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TranscriptTurn:
    """
    One utterance/segment in the conversation.
    """

    speaker: str
    text: str
    start: Optional[float] = None
    end: Optional[float] = None

    @property
    def duration(self) -> Optional[float]:
        if self.start is None or self.end is None:
            return None
        return round(self.end - self.start, 3)


@dataclass
class ParsedTranscript:
    """
    Normalized transcript used by extractor/validator.
    """

    turns: List[TranscriptTurn] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return " ".join(turn.text for turn in self.turns if turn.text).strip()

    @property
    def customer_turns(self) -> List[TranscriptTurn]:
        return [t for t in self.turns if t.speaker == "customer"]

    @property
    def bot_turns(self) -> List[TranscriptTurn]:
        return [t for t in self.turns if t.speaker == "bot"]

    @property
    def customer_text(self) -> str:
        return " ".join(t.text for t in self.customer_turns if t.text).strip()

    @property
    def bot_text(self) -> str:
        return " ".join(t.text for t in self.bot_turns if t.text).strip()

    def has_customer_audio(self) -> bool:
        return len(self.customer_turns) > 0

    def has_bot_audio(self) -> bool:
        return len(self.bot_turns) > 0
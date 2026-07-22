from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SpeakerProfile:

    speaker_id: str

    utterances: List[str] = field(default_factory=list)

    total_words: int = 0

    question_count: int = 0

    greeting_count: int = 0

    help_count: int = 0

    order_mentions: int = 0

    email_mentions: int = 0

    phone_mentions: int = 0

    tracking_mentions: int = 0

    refund_mentions: int = 0

    return_mentions: int = 0

    language_selection_count: int = 0

    average_length: float = 0.0

    bot_score: float = 0.0

    customer_score: float = 0.0

    confidence: float = 0.0

    role: str = "unknown"

    conversation_text: str = ""

    total_turns: int = 0

    first_timestamp: float | None = None

    last_timestamp: float | None = None

    script_repetition: int = 0

    avg_words_per_turn: float = 0

    greeting_ratio: float = 0

    question_ratio: float = 0

    conversation_position: float = 0

    def add(self, text: str):

        self.utterances.append(text)

        words = text.split()

        self.total_words += len(words)

        self.average_length = (
            self.total_words / len(self.utterances)
            if self.utterances
            else 0
        )

    def to_dict(self):

        return {

            "speaker": self.speaker_id,

            "role": self.role,

            "utterances": len(self.utterances),

            "avg_length": round(self.average_length, 2),

            "bot_score": self.bot_score,

            "customer_score": self.customer_score,

            "confidence": self.confidence,
        }
    
    def finalize(self):

        if self.total_turns:

            self.avg_words_per_turn = (
                self.total_words /
                self.total_turns
            )

            self.question_ratio = (
                self.question_count /
                self.total_turns
            )

            self.greeting_ratio = (
                self.greeting_count /
                self.total_turns
            )
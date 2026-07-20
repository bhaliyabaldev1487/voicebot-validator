from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SpeakerProfile:
    """
    Aggregated information for a single speaker across
    the entire conversation.

    Example:

        SPEAKER_00
            Hello...
            English or Arabic?
            Please share your order number.

        ->
            role = BOT
    """

    speaker: str

    utterances: list[str] = field(default_factory=list)

    bot_score: int = 0

    customer_score: int = 0

    role: str = "unknown"

    @property
    def full_text(self) -> str:
        """
        Entire conversation spoken by this speaker.
        """
        return " ".join(self.utterances).lower()

    def add(self, text: str) -> None:
        """
        Add one utterance.
        """
        if text:
            self.utterances.append(text.strip())

    def add_bot(self, score: int = 1) -> None:
        self.bot_score += score

    def add_customer(self, score: int = 1) -> None:
        self.customer_score += score

    @property
    def utterance_count(self) -> int:
        return len(self.utterances)

    def decide_role(self) -> str:
        """
        Decide final role.
        """

        if self.bot_score > self.customer_score:
            self.role = "bot"

        elif self.customer_score > self.bot_score:
            self.role = "customer"

        else:
            self.role = "unknown"

        return self.role

    def to_dict(self) -> dict:

        return {
            "speaker": self.speaker,
            "utterance_count": self.utterance_count,
            "bot_score": self.bot_score,
            "customer_score": self.customer_score,
            "role": self.role,
            "utterances": self.utterances,
        }
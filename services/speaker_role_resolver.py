"""
services/speaker_role_resolver.py

Resolve diarization speaker labels (e.g. SPEAKER_00 / SPEAKER_01)
into semantic roles:
- bot
- customer

This is important because WhisperX / diarization only gives speaker IDs,
not business roles.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional


# ----------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------


@dataclass
class SpeakerRoleResolution:
    """
    Final mapping of diarization speaker -> semantic role.
    Example:
        {"speaker_00": "bot", "speaker_01": "customer"}
    """

    mapping: Dict[str, str]

    def resolve(self, raw_speaker: str) -> str:
        return self.mapping.get(raw_speaker.lower(), "unknown")


# ----------------------------------------------------------------------
# Resolver
# ----------------------------------------------------------------------


class SpeakerRoleResolver:
    """
    Infer whether each diarized speaker is bot or customer.

    Strategy:
    - Score each speaker based on utterance content
    - Bot tends to say scripted phrases / greeting / help prompts
    - Customer tends to ask about order, shipping, return, refund etc.
    """

    BOT_HINTS = [
        "welcome",
        "how may i help you",
        "how can i help you",
        "please share your order number",
        "please tell me your order number",
        "can you confirm your email",
        "let me check",
        "one moment please",
        "i can help you with",
        "thank you for calling",
        "your order status is",
        "your order has been",
        "anything else i can help",
    ]

    CUSTOMER_HINTS = [
        "where is my order",
        "i want to know my order status",
        "my order number is",
        "i placed an order",
        "i want to return",
        "i need refund",
        "my number is",
        "my email is",
        "can you check my order",
        "when will it be delivered",
    ]

    def resolve(self, segments: List[dict]) -> SpeakerRoleResolution:
        """
        Build speaker -> role mapping from transcript segments.
        """
        speaker_scores = defaultdict(lambda: {"bot": 0, "customer": 0})

        for seg in segments:
            raw_speaker = self._get_raw_speaker(seg)
            if not raw_speaker:
                continue

            text = self._normalize_text(seg.get("text", ""))

            bot_score = self._score_bot(text)
            customer_score = self._score_customer(text)

            speaker_scores[raw_speaker]["bot"] += bot_score
            speaker_scores[raw_speaker]["customer"] += customer_score

        mapping = self._finalize_mapping(speaker_scores, segments)
        return SpeakerRoleResolution(mapping=mapping)

    # ------------------------------------------------------------------
    # Internal scoring
    # ------------------------------------------------------------------

    def _score_bot(self, text: str) -> int:
        score = 0
        for hint in self.BOT_HINTS:
            if hint in text:
                score += 2

        # Bot often has longer informational statements
        if "your order" in text and ("status" in text or "has been" in text):
            score += 2

        return score

    def _score_customer(self, text: str) -> int:
        score = 0
        for hint in self.CUSTOMER_HINTS:
            if hint in text:
                score += 2

        # Questions are more likely customer-side
        if "?" in text:
            score += 1

        if "my order" in text or "my email" in text or "my number" in text:
            score += 1

        return score

    # ------------------------------------------------------------------
    # Mapping logic
    # ------------------------------------------------------------------

    def _finalize_mapping(
        self,
        speaker_scores: Dict[str, dict],
        segments: List[dict],
    ) -> Dict[str, str]:
        """
        Convert scores into final speaker role mapping.
        """
        speakers = list(speaker_scores.keys())

        if not speakers:
            return {}

        # Simple case: one speaker
        if len(speakers) == 1:
            only = speakers[0]
            scores = speaker_scores[only]
            role = "bot" if scores["bot"] >= scores["customer"] else "customer"
            return {only: role}

        # Score-based role assignment
        scored = []
        for speaker, scores in speaker_scores.items():
            scored.append(
                (
                    speaker,
                    scores["bot"],
                    scores["customer"],
                    scores["bot"] - scores["customer"],
                )
            )

        # speaker with higher (bot - customer) becomes bot
        scored.sort(key=lambda x: x[3], reverse=True)

        mapping: Dict[str, str] = {}

        if len(scored) >= 2:
            top = scored[0]
            second = scored[1]

            mapping[top[0]] = "bot"
            mapping[second[0]] = "customer"

            # Any additional speakers -> unknown for now
            for extra in scored[2:]:
                mapping[extra[0]] = "unknown"

        # fallback if still unresolved
        if not mapping:
            mapping = self._fallback_by_first_turn(segments)

        return mapping

    def _fallback_by_first_turn(self, segments: List[dict]) -> Dict[str, str]:
        """
        If scoring is weak, use the first meaningful turn:
        first greeting/help prompt is usually bot.
        """
        for seg in segments:
            raw_speaker = self._get_raw_speaker(seg)
            text = self._normalize_text(seg.get("text", ""))

            if not raw_speaker or not text:
                continue

            if any(hint in text for hint in self.BOT_HINTS):
                return {raw_speaker: "bot"}

            if any(hint in text for hint in self.CUSTOMER_HINTS):
                return {raw_speaker: "customer"}

        return {}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_raw_speaker(segment: dict) -> Optional[str]:
        raw = (
            segment.get("speaker")
            or segment.get("speaker_label")
            or segment.get("role")
        )
        if not raw:
            return None
        return str(raw).strip().lower()

    @staticmethod
    def _normalize_text(text: str) -> str:
        return " ".join(str(text).lower().split())
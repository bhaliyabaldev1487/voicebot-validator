from __future__ import annotations

import re
from typing import Dict, List

from models.speaker_profile import SpeakerProfile


class SpeakerProfileBuilder:

    GREETING_WORDS = {
        "hello",
        "hi",
        "welcome",
        "good morning",
        "good evening",
    }

    HELP_WORDS = {
        "help",
        "assist",
        "support",
    }

    ORDER_WORDS = {
        "order",
        "tracking",
        "shipment",
        "delivery",
    }

    REFUND_WORDS = {
        "refund",
        "cancel",
        "exchange",
        "return",
    }

    LANGUAGE_WORDS = {
        "english",
        "arabic",
        "hindi",
    }

    EMAIL_REGEX = re.compile(r"\S+@\S+\.\S+")

    PHONE_REGEX = re.compile(r"\d{10}")

    def build(self, segments: List[dict]) -> Dict[str, SpeakerProfile]:

        profiles: Dict[str, SpeakerProfile] = {}

        for segment in segments:

            speaker = (
                segment.get("speaker")
                or segment.get("speaker_label")
                or "unknown"
            ).lower()

            profile = profiles.setdefault(
                speaker,
                SpeakerProfile(speaker_id=speaker),
            )

            text = str(segment.get("text", "")).strip()

            if not text:
                continue

            profile.add(text)

            lower = text.lower()

            if "?" in text:
                profile.question_count += 1

            if any(word in lower for word in self.GREETING_WORDS):
                profile.greeting_count += 1

            if any(word in lower for word in self.HELP_WORDS):
                profile.help_count += 1

            if any(word in lower for word in self.ORDER_WORDS):
                profile.order_mentions += 1

            if any(word in lower for word in self.REFUND_WORDS):
                profile.refund_mentions += 1

            if any(word in lower for word in self.LANGUAGE_WORDS):
                profile.language_selection_count += 1

            if self.EMAIL_REGEX.search(lower):
                profile.email_mentions += 1

            if self.PHONE_REGEX.search(lower):
                profile.phone_mentions += 1

        return profiles
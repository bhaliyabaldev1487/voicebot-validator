from __future__ import annotations

from collections import Counter
from typing import Dict, List

from models.speaker_profile import SpeakerProfile


class ConversationFlow:

    """
    Analyses overall conversation flow.

    Produces additional confidence for each speaker.

    It does NOT assign BOT/CUSTOMER.
    It only boosts confidence using conversation statistics.
    """

    def score(
        self,
        segments: List[dict],
        profiles: Dict[str, SpeakerProfile],
    ) -> None:

        if not segments:
            return

        speaker_sequence = []

        for segment in segments:

            speaker = (
                segment.get("speaker")
                or segment.get("speaker_label")
                or ""
            ).lower()

            if speaker:
                speaker_sequence.append(speaker)

        counts = Counter(speaker_sequence)

        total_turns = len(speaker_sequence)

        if total_turns == 0:
            return

        for speaker, profile in profiles.items():

            profile.conversation_position = (
                counts[speaker] / total_turns
            )

            # Speakers dominating the conversation
            # are slightly more likely to be BOT.
            if profile.conversation_position > 0.45:
                profile.bot_score += 2

            # Few turns usually indicate customer.
            elif profile.conversation_position < 0.25:
                profile.customer_score += 1
from typing import Dict

from models.speaker_profile import SpeakerProfile


class ConversationClassifier:

    def score(
        self,
        profiles: Dict[str, SpeakerProfile],
    ):

        if len(profiles) <= 1:
            return

        for profile in profiles.values():

            total = (
                profile.bot_score +
                profile.customer_score
            )

            if total == 0:
                profile.confidence = 0
                profile.role = "unknown"
                continue

            if profile.bot_score >= profile.customer_score:

                profile.role = "bot"

                profile.confidence = (
                    profile.bot_score / total
                )

            else:

                profile.role = "customer"

                profile.confidence = (
                    profile.customer_score / total
                )
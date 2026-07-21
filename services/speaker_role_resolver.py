from __future__ import annotations

import logging
from typing import Dict, List

from classifiers.bot_classifier import BotClassifier
from classifiers.conversation_classifier import ConversationClassifier
from classifiers.customer_classifier import CustomerClassifier
from classifiers.speaker_profile_builder import SpeakerProfileBuilder

from models.speaker_role_resolution import SpeakerRoleResolution

logger = logging.getLogger(__name__)


class SpeakerRoleResolver:

    def __init__(self):

        self.builder = SpeakerProfileBuilder()

        self.bot_classifier = BotClassifier()

        self.customer_classifier = CustomerClassifier()

        self.conversation_classifier = ConversationClassifier()

    def resolve(
        self,
        segments: List[dict],
    ) -> SpeakerRoleResolution:

        profiles = self.builder.build(segments)

        for profile in profiles.values():

            self.bot_classifier.score(profile)

            self.customer_classifier.score(profile)

        self.conversation_classifier.score(
            profiles
        )

        mapping = {}

        confidence = {}

        logger.info("========== SPEAKER SCORES ==========")

        for speaker, profile in profiles.items():

            logger.info(
                "%s bot=%s customer=%s role=%s confidence=%.2f",
                speaker,
                profile.bot_score,
                profile.customer_score,
                profile.role,
                profile.confidence,
            )

            mapping[speaker.lower()] = profile.role

            confidence[speaker.lower()] = profile.confidence

        logger.info("====================================")

        return SpeakerRoleResolution(
            mapping=mapping,
            confidence=confidence,
        )
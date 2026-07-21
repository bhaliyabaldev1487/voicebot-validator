from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class SpeakerRoleResolution:
    mapping: Dict[str, str]

    confidence: Dict[str, float]

    def resolve(self, speaker: str) -> str:
        return self.mapping.get(
            speaker.lower(),
            "unknown",
        )

    def get_confidence(self, speaker: str) -> float:

        return self.confidence.get(
            speaker.lower(),
            0.0,
        )

    def to_dict(self):

        return {

            "mapping": self.mapping,

            "confidence": self.confidence,
        }
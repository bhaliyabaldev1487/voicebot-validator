from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class SpeakerRoleResolution:
    """
    Final mapping between diarized speakers and semantic roles.

    Example:
        speaker_00 -> bot
        speaker_01 -> bot
        speaker_02 -> bot
        speaker_03 -> customer
    """

    mapping: Dict[str, str]

    def resolve(self, speaker: str) -> str:
        if not speaker:
            return "unknown"

        return self.mapping.get(
            speaker.lower(),
            "unknown",
        )

    def to_dict(self):
        return self.mapping
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models.lookup import LookupResult
from models.transcript import ParsedTranscript
from models.validation_context import ValidationResult


@dataclass
class Conversation:

    conversation_id: Optional[str] = None

    caller_phone: Optional[str] = None

    transcript: Optional[ParsedTranscript] = None

    speaker_profiles: Dict[str, Any] = field(default_factory=dict)

    speaker_mapping: Dict[str, str] = field(default_factory=dict)

    intent: Optional[str] = None

    entities: Any = None

    bot_response: Any = None

    lookup_result: Optional[LookupResult] = None

    validation_result: Optional[ValidationResult] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):

        return {

            "conversation_id": self.conversation_id,

            "caller_phone": self.caller_phone,

            "intent": self.intent,

            "speaker_mapping": self.speaker_mapping,

            "metadata": self.metadata,
        }
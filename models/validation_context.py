"""
models/validation_context.py

Validation context passed into validators.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from extractors.order_entities_extractor import OrderEntities
from models.lookup import LookupResult
from models.transcript import ParsedTranscript
from models.bot_response import BotOrderResponse

@dataclass
class ValidationContext:
    """
    Full context required by order flow validator.
    """

    transcript: ParsedTranscript
    entities: OrderEntities
    lookup_result: LookupResult

    # NEW
    bot_response: Optional[BotOrderResponse] = None

    # call metadata
    caller_phone: Optional[str] = None
    transcript_file: Optional[str] = None
    conversation_id: Optional[str] = None

    @property
    def customer_text(self) -> str:
        return self.transcript.customer_text

    @property
    def bot_text(self) -> str:
        return self.transcript.bot_text

    @property
    def full_text(self) -> str:
        return self.transcript.full_text
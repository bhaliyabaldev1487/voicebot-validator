from dataclasses import dataclass
from typing import Optional

from models.customer import Customer
from models.order import Order
from models.transcript import Transcript
from models.lookup import LookupResult
from models.bot_response import BotOrderResponse
from extractors.order_entities_extractor import OrderEntities


@dataclass
class ConversationContext:

    transcript: Transcript

    lookup_result: LookupResult

    customer: Optional[Customer]

    order: Optional[Order]

    extracted_entities: OrderEntities

    bot_response: BotOrderResponse

    caller_phone: Optional[str] = None

    conversation_id: Optional[str] = None

    @property
    def bot_text(self):

        return " ".join(
            s.text
            for s in self.transcript.segments
            if s.speaker.upper() == "BOT"
        )

    @property
    def customer_text(self):

        return " ".join(
            s.text
            for s in self.transcript.segments
            if s.speaker.upper() == "CUSTOMER"
        )
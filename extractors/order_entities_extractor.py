"""
extractors/order_entities_extractor.py

Extract structured order-related entities from transcript text.

This extractor is intentionally regex/rule-based for Phase 1:
- order number
- email
- phone / mobile
- intent hints

Later we can upgrade it with LLM/NER if needed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


# ----------------------------------------------------------------------
# Extracted entities
# ----------------------------------------------------------------------


@dataclass
class OrderEntities:
    """
    Structured entities extracted from a transcript.
    """

    order_number: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_mobile: Optional[str] = None
    intent: Optional[str] = None


# ----------------------------------------------------------------------
# Extractor
# ----------------------------------------------------------------------


class OrderEntitiesExtractor:
    """
    Extract order-flow entities from transcript text.

    Supported entities:
    - order number
    - email
    - phone / mobile
    - intent classification (basic rule-based)
    """

    EMAIL_REGEX = re.compile(
        r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b"
    )

    PHONE_REGEX = re.compile(
        r"(?:\+?\d[\d\-\s]{7,}\d)"
    )

    # Examples:
    # order number 12345
    # my order id is AZA12345
    # order no A123456
    ORDER_PATTERNS = [
        re.compile(
            r"(?:order\s*(?:number|no|id)?\s*(?:is)?\s*[:#-]?\s*)([A-Za-z0-9\-]{4,})",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b([A-Z]{2,}[0-9]{3,})\b",
            re.IGNORECASE,
        ),
    ]

    ORDER_INTENT_KEYWORDS = [
        "order status",
        "track my order",
        "where is my order",
        "order details",
        "my order",
        "order update",
        "placed an order",
    ]

    SHIPPING_INTENT_KEYWORDS = [
        "shipping status",
        "delivery status",
        "when will it arrive",
        "shipped",
        "delivered",
        "dispatch",
    ]

    RETURN_INTENT_KEYWORDS = [
        "return order",
        "return request",
        "refund",
        "exchange",
        "replace order",
    ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(self, transcript_text: str) -> OrderEntities:
        """
        Extract all supported entities from transcript text.
        """
        text = transcript_text or ""
        normalized = self._normalize_whitespace(text)

        email = self._extract_email(normalized)
        phone = self._extract_phone(normalized)
        order_number = self._extract_order_number(normalized)
        intent = self._extract_intent(normalized)

        # For now, use same value for phone/mobile if extracted from text.
        # Later we can distinguish based on transcript phrasing if needed.
        return OrderEntities(
            order_number=order_number,
            customer_email=email,
            customer_phone=phone,
            customer_mobile=phone,
            intent=intent,
        )

    # ------------------------------------------------------------------
    # Individual extractors
    # ------------------------------------------------------------------

    def _extract_email(self, text: str) -> Optional[str]:
        match = self.EMAIL_REGEX.search(text)
        if not match:
            return None
        return match.group(0).strip()

    def _extract_phone(self, text: str) -> Optional[str]:
        """
        Extract first phone-like sequence and normalize to digits only.
        """
        match = self.PHONE_REGEX.search(text)
        if not match:
            return None

        raw = match.group(0)
        digits = self._normalize_phone(raw)

        # Basic sanity check
        if len(digits) < 8:
            return None

        return digits

    def _extract_order_number(self, text: str) -> Optional[str]:
        for pattern in self.ORDER_PATTERNS:
            match = pattern.search(text)
            if match:
                return match.group(1).strip().upper()
        return None

    def _extract_intent(self, text: str) -> Optional[str]:
        lowered = text.lower()

        if any(keyword in lowered for keyword in self.RETURN_INTENT_KEYWORDS):
            return "return"

        if any(keyword in lowered for keyword in self.SHIPPING_INTENT_KEYWORDS):
            return "shipping"

        if any(keyword in lowered for keyword in self.ORDER_INTENT_KEYWORDS):
            return "order"

        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        return "".join(ch for ch in phone if ch.isdigit())

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        return " ".join(text.split())
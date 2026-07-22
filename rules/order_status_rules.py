"""
rules/order_status_rules.py

Semantic Order Status Rules

This module provides a rule-based semantic matcher for order statuses.
It is designed to recognize natural language responses from the voicebot
and normalize them into canonical business statuses.

Example:

    Bot:
        "Your order is currently being stitched."

    →

        PROCESSING

--------------------------------------------------------

Author:
Voicebot Validator

--------------------------------------------------------
"""

from __future__ import annotations

import re

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Pattern, Sequence, Tuple


# ============================================================
# Canonical Status Enum
# ============================================================

class OrderStatus(str, Enum):

    UNKNOWN = "UNKNOWN"

    PLACED = "PLACED"

    CONFIRMED = "CONFIRMED"

    PROCESSING = "PROCESSING"

    PAYMENT_PENDING = "PAYMENT_PENDING"

    PAYMENT_FAILED = "PAYMENT_FAILED"

    SHIPPED = "SHIPPED"

    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"

    DELIVERED = "DELIVERED"

    CANCELLED = "CANCELLED"

    RETURN_REQUESTED = "RETURN_REQUESTED"

    RETURN_APPROVED = "RETURN_APPROVED"

    RETURN_REJECTED = "RETURN_REJECTED"

    REFUNDED = "REFUNDED"

    EXCHANGED = "EXCHANGED"


# ============================================================
# Match Result
# ============================================================

@dataclass(slots=True)
class StatusMatch:

    status: OrderStatus

    confidence: float

    matched_phrase: Optional[str]

    matched_pattern: Optional[str]

    sentence: str


# ============================================================
# Status Rule
# ============================================================

@dataclass(frozen=True)
class StatusRule:

    canonical_status: OrderStatus

    phrases: Tuple[str, ...]

    negative_phrases: Tuple[str, ...]

    confidence: float = 0.95


# ============================================================
# Helper
# ============================================================

def _normalize(text: str) -> str:

    text = text.lower()

    text = text.replace("-", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# Phrase Compiler
# ============================================================

class PhraseCompiler:

    @staticmethod
    def compile_phrase(phrase: str) -> Pattern:

        escaped = re.escape(_normalize(phrase))

        return re.compile(rf"\b{escaped}\b", re.IGNORECASE)

    @classmethod
    def compile_many(
        cls,
        phrases: Sequence[str],
    ) -> List[Pattern]:

        return [
            cls.compile_phrase(p)
            for p in phrases
        ]


# ============================================================
# Matcher
# ============================================================

class OrderStatusMatcher:

    def __init__(
        self,
        rules: Sequence[StatusRule],
    ):

        self.rules = list(rules)

        self.compiled: Dict[
            OrderStatus,
            List[Pattern],
        ] = {}

        self.compiled_negative: Dict[
            OrderStatus,
            List[Pattern],
        ] = {}

        for rule in rules:

            self.compiled[
                rule.canonical_status
            ] = PhraseCompiler.compile_many(
                rule.phrases
            )

            self.compiled_negative[
                rule.canonical_status
            ] = PhraseCompiler.compile_many(
                rule.negative_phrases
            )

    # -------------------------------------------------------

    def normalize(
        self,
        text: str,
    ) -> str:

        return _normalize(text)

    # -------------------------------------------------------

    def match(
        self,
        text: str,
    ) -> StatusMatch:

        text = self.normalize(text)

        for rule in self.rules:

            # Skip if negative phrase exists

            negative_patterns = self.compiled_negative[
                rule.canonical_status
            ]

            if any(
                p.search(text)
                for p in negative_patterns
            ):
                continue

            for pattern in self.compiled[
                rule.canonical_status
            ]:

                m = pattern.search(text)

                if m:

                    return StatusMatch(

                        status=rule.canonical_status,

                        confidence=rule.confidence,

                        matched_phrase=m.group(0),

                        matched_pattern=pattern.pattern,

                        sentence=text,

                    )

        return StatusMatch(

            status=OrderStatus.UNKNOWN,

            confidence=0.0,

            matched_phrase=None,

            matched_pattern=None,

            sentence=text,

        )

    # -------------------------------------------------------

    def find_all(
        self,
        text: str,
    ) -> List[StatusMatch]:

        matches: List[StatusMatch] = []

        text = self.normalize(text)

        for rule in self.rules:

            for pattern in self.compiled[
                rule.canonical_status
            ]:

                m = pattern.search(text)

                if m:

                    matches.append(

                        StatusMatch(

                            status=rule.canonical_status,

                            confidence=rule.confidence,

                            matched_phrase=m.group(0),

                            matched_pattern=pattern.pattern,

                            sentence=text,

                        )

                    )

        return matches

    # -------------------------------------------------------
    # Sentence Matching
    # -------------------------------------------------------

    def match_sentence(
        self,
        sentence: str,
    ) -> StatusMatch:
        """
        Match a single sentence against all status rules.
        """
        return self.match(sentence)

    # -------------------------------------------------------
    # Document Matching
    # -------------------------------------------------------

    def match_document(
        self,
        text: str,
    ) -> List[StatusMatch]:
        """
        Split a document into sentences and match each one.
        """

        sentences = self._split_sentences(text)

        matches: List[StatusMatch] = []

        for sentence in sentences:

            result = self.match(sentence)

            if result.status != OrderStatus.UNKNOWN:
                matches.append(result)

        return matches

    # -------------------------------------------------------
    # Best Match
    # -------------------------------------------------------

    def match_best(
        self,
        text: str,
    ) -> StatusMatch:
        """
        Return the highest-confidence match in a document.
        """

        matches = self.match_document(text)

        if not matches:
            return StatusMatch(
                status=OrderStatus.UNKNOWN,
                confidence=0.0,
                matched_phrase=None,
                matched_pattern=None,
                sentence=text,
            )

        matches.sort(
            key=lambda m: m.confidence,
            reverse=True,
        )

        return matches[0]

    # -------------------------------------------------------
    # Extract Canonical Statuses
    # -------------------------------------------------------

    def extract_statuses(
        self,
        text: str,
    ) -> List[OrderStatus]:
        """
        Return unique canonical statuses detected in text.
        """

        statuses = []

        for match in self.match_document(text):

            if match.status not in statuses:
                statuses.append(match.status)

        return statuses

    # -------------------------------------------------------
    # Contains Status
    # -------------------------------------------------------

    def contains(
        self,
        text: str,
        status: OrderStatus,
    ) -> bool:

        for match in self.match_document(text):

            if match.status == status:
                return True

        return False

    # -------------------------------------------------------
    # Explain Match
    # -------------------------------------------------------

    def explain(
        self,
        text: str,
    ) -> Dict:

        best = self.match_best(text)

        return {

            "status": best.status.value,

            "confidence": best.confidence,

            "matched_phrase": best.matched_phrase,

            "matched_pattern": best.matched_pattern,

            "sentence": best.sentence,

        }

    # -------------------------------------------------------
    # Sentence Splitter
    # -------------------------------------------------------

    @staticmethod
    def _split_sentences(
        text: str,
    ) -> List[str]:

        if not text:
            return []

        text = text.replace("\n", ". ")

        parts = re.split(
            r"[.!?]+",
            text,
        )

        return [
            p.strip()
            for p in parts
            if p.strip()
        ]
    
    # -------------------------------------------------------
    # Fuzzy Match
    # -------------------------------------------------------

    def fuzzy_match(
        self,
        text: str,
        threshold: float = 0.82,
    ) -> StatusMatch:
        """
        Match using phrase similarity instead of exact regex.
        Useful when Whisper introduces spelling mistakes.
        """

        normalized = self.normalize(text)

        best: Optional[StatusMatch] = None

        best_score = 0.0

        for rule in self.rules:

            if self._contains_negative_phrase(
                normalized,
                rule,
            ):
                continue

            for phrase in rule.phrases:

                score = self._similarity(
                    normalized,
                    phrase,
                )

                if score > best_score:

                    best_score = score

                    best = StatusMatch(

                        status=rule.canonical_status,

                        confidence=round(score, 2),

                        matched_phrase=phrase,

                        matched_pattern=None,

                        sentence=text,

                    )

        if best and best_score >= threshold:
            return best

        return StatusMatch(
            status=OrderStatus.UNKNOWN,
            confidence=0.0,
            matched_phrase=None,
            matched_pattern=None,
            sentence=text,
        )

    # -------------------------------------------------------
    # Similarity
    # -------------------------------------------------------

    def _similarity(
        self,
        text: str,
        phrase: str,
    ) -> float:

        text = self.normalize(text)

        phrase = self.normalize(phrase)

        if phrase in text:
            return 1.0

        words = text.split()

        phrase_words = phrase.split()

        if len(words) < len(phrase_words):
            windows = [text]
        else:
            windows = [
                " ".join(words[i:i + len(phrase_words)])
                for i in range(
                    len(words) - len(phrase_words) + 1
                )
            ]

        best = 0.0

        for window in windows:

            score = self._levenshtein_ratio(
                window,
                phrase,
            )

            if score > best:
                best = score

        return best

    # -------------------------------------------------------
    # Levenshtein Ratio
    # -------------------------------------------------------

    @staticmethod
    def _levenshtein_ratio(
        s1: str,
        s2: str,
    ) -> float:

        if s1 == s2:
            return 1.0

        if not s1 or not s2:
            return 0.0

        len1 = len(s1)
        len2 = len(s2)

        matrix = [
            [0] * (len2 + 1)
            for _ in range(len1 + 1)
        ]

        for i in range(len1 + 1):
            matrix[i][0] = i

        for j in range(len2 + 1):
            matrix[0][j] = j

        for i in range(1, len1 + 1):

            for j in range(1, len2 + 1):

                cost = 0 if s1[i - 1] == s2[j - 1] else 1

                matrix[i][j] = min(

                    matrix[i - 1][j] + 1,

                    matrix[i][j - 1] + 1,

                    matrix[i - 1][j - 1] + cost,

                )

        distance = matrix[len1][len2]

        maximum = max(len1, len2)

        return 1 - (distance / maximum)

    # -------------------------------------------------------
    # Negative Phrase Detection
    # -------------------------------------------------------

    def _contains_negative_phrase(
        self,
        text: str,
        rule: StatusRule,
    ) -> bool:

        for phrase in rule.negative_phrases:

            if phrase.lower() in text:

                return True

        return False

    # -------------------------------------------------------
    # Rank Matches
    # -------------------------------------------------------

    def rank_matches(
        self,
        text: str,
    ) -> List[StatusMatch]:
        """
        Return all candidate matches sorted by confidence.
        """

        candidates: List[StatusMatch] = []

        exact = self.match_document(text)

        candidates.extend(exact)

        fuzzy = self.fuzzy_match(text)

        if fuzzy.status != OrderStatus.UNKNOWN:

            exists = any(
                m.status == fuzzy.status
                for m in candidates
            )

            if not exists:
                candidates.append(fuzzy)

        candidates.sort(
            key=lambda m: m.confidence,
            reverse=True,
        )

        return candidates

    # -------------------------------------------------------
    # Best Semantic Match
    # -------------------------------------------------------

    def semantic_match(
        self,
        text: str,
    ) -> StatusMatch:
        """
        Hybrid exact + fuzzy matcher.
        """

        ranked = self.rank_matches(text)

        if ranked:
            return ranked[0]

        return StatusMatch(
            status=OrderStatus.UNKNOWN,
            confidence=0.0,
            matched_phrase=None,
            matched_pattern=None,
            sentence=text,
        )
    
    # -------------------------------------------------------

    @staticmethod
    def is_terminal(
        status: OrderStatus,
    ) -> bool:

        return status in {

            OrderStatus.DELIVERED,

            OrderStatus.CANCELLED,

            OrderStatus.REFUNDED,

            OrderStatus.RETURN_REJECTED,

            OrderStatus.EXCHANGED,

        }

    @staticmethod
    def is_processing(
        status: OrderStatus,
    ) -> bool:

        return status in {

            OrderStatus.PLACED,

            OrderStatus.CONFIRMED,

            OrderStatus.PROCESSING,

            OrderStatus.SHIPPED,

            OrderStatus.OUT_FOR_DELIVERY,

        }


# ============================================================
# Rule Definitions
#
# Part 2 will continue from here with the complete set of
# StatusRule objects and instantiate the matcher.
# ============================================================

# ============================================================
# Order Status Rules
# ============================================================

ORDER_STATUS_RULES: List[StatusRule] = [

    # --------------------------------------------------------
    # ORDER PLACED
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.PLACED,
        phrases=(
            "order placed",
            "placed successfully",
            "your order has been placed",
            "order is placed",
            "successfully placed",
            "order booked",
            "booking completed",
            "order created",
            "created successfully",
            "we have received your order",
            "order received",
            "thank you for your order",
            "your purchase has been recorded",
            "order has been registered",
        ),
        negative_phrases=(
            "cancelled",
            "returned",
            "failed",
        ),
        confidence=0.98,
    ),

    # --------------------------------------------------------
    # ORDER CONFIRMED
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.CONFIRMED,
        phrases=(
            "order confirmed",
            "confirmed successfully",
            "your order is confirmed",
            "confirmation completed",
            "we have confirmed your order",
            "order verification completed",
            "verified",
            "verified successfully",
            "confirmation done",
            "confirmed by seller",
            "confirmed by designer",
        ),
        negative_phrases=(
            "cancelled",
            "failed",
        ),
        confidence=0.98,
    ),

    # --------------------------------------------------------
    # PROCESSING
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.PROCESSING,
        phrases=(

            "processing",

            "currently processing",

            "under processing",

            "being processed",

            "still processing",

            "in process",

            "order is in process",

            "being stitched",

            "currently being stitched",

            "under stitching",

            "stitching is in progress",

            "your lehenga is being stitched",

            "tailoring",

            "under tailoring",

            "currently under tailoring",

            "being tailored",

            "production",

            "under production",

            "currently in production",

            "manufacturing",

            "being manufactured",

            "quality check",

            "quality inspection",

            "quality assurance",

            "under qc",

            "packing",

            "being packed",

            "currently packing",

            "package preparation",

            "preparing shipment",

            "designer is preparing",

            "designer is working",

            "designer is making",

            "work in progress",

            "work is ongoing",

            "awaiting completion",

            "being prepared",

            "preparing your order",

            "your order is being prepared",

            "your order is under preparation",

            "almost ready",

            "finishing stage",

        ),
        negative_phrases=(

            "delivered",

            "cancelled",

            "returned",

            "refund",

            "shipped",

            "out for delivery",

        ),
        confidence=0.99,
    ),

    # --------------------------------------------------------
    # PAYMENT PENDING
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.PAYMENT_PENDING,
        phrases=(
            "payment pending",
            "awaiting payment",
            "payment not received",
            "waiting for payment",
            "pending payment",
            "payment is due",
            "payment required",
            "complete your payment",
            "payment incomplete",
        ),
        negative_phrases=(
            "payment successful",
            "payment received",
            "payment completed",
        ),
        confidence=0.98,
    ),

    # --------------------------------------------------------
    # PAYMENT FAILED
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.PAYMENT_FAILED,
        phrases=(
            "payment failed",
            "transaction failed",
            "payment unsuccessful",
            "payment declined",
            "bank declined",
            "payment rejected",
            "payment error",
            "payment could not be processed",
        ),
        negative_phrases=(
            "payment successful",
            "payment completed",
        ),
        confidence=0.99,
    ),

    # --------------------------------------------------------
    # SHIPPED
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.SHIPPED,
        phrases=(
            "shipped",
            "your order has been shipped",
            "dispatched",
            "dispatched successfully",
            "left warehouse",
            "left our warehouse",
            "handed over to courier",
            "courier has picked up",
            "shipment created",
            "shipment booked",
            "package dispatched",
            "package shipped",
            "in transit",
            "on the way",
        ),
        negative_phrases=(
            "delivered",
            "cancelled",
            "returned",
        ),
        confidence=0.99,
    ),

    # --------------------------------------------------------
    # OUT FOR DELIVERY
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.OUT_FOR_DELIVERY,
        phrases=(
            "out for delivery",
            "vehicle is out for delivery",
            "delivery agent is on the way",
            "delivery executive is on the way",
            "courier is reaching",
            "arriving today",
            "expected today",
            "will reach today",
        ),
        negative_phrases=(
            "delivered",
            "cancelled",
        ),
        confidence=0.99,
    ),

    # --------------------------------------------------------
    # DELIVERED
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.DELIVERED,
        phrases=(
            "delivered",
            "already delivered",
            "successfully delivered",
            "delivery completed",
            "received",
            "customer received",
            "handed over",
            "package delivered",
            "shipment delivered",
            "completed delivery",
            "reached you",
            "reached destination",
        ),
        negative_phrases=(
            "return initiated",
            "return requested",
        ),
        confidence=0.99,
    ),

    # --------------------------------------------------------
    # CANCELLED
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.CANCELLED,
        phrases=(
            "cancelled",
            "order cancelled",
            "has been cancelled",
            "canceled",
            "order canceled",
            "cancel request approved",
            "order was cancelled",
            "cancelled successfully",
            "booking cancelled",
        ),
        negative_phrases=(),
        confidence=1.00,
    ),

    # --------------------------------------------------------
    # RETURN REQUESTED
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.RETURN_REQUESTED,
        phrases=(
            "return requested",
            "return initiated",
            "return request created",
            "return request received",
            "pickup requested",
            "reverse pickup initiated",
        ),
        negative_phrases=(
            "refund completed",
        ),
        confidence=0.99,
    ),

    # --------------------------------------------------------
    # RETURN APPROVED
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.RETURN_APPROVED,
        phrases=(
            "return approved",
            "return accepted",
            "approved for return",
            "return request approved",
        ),
        negative_phrases=(
            "return rejected",
        ),
        confidence=0.99,
    ),

    # --------------------------------------------------------
    # RETURN REJECTED
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.RETURN_REJECTED,
        phrases=(
            "return rejected",
            "return declined",
            "cannot accept return",
            "return not approved",
        ),
        negative_phrases=(),
        confidence=0.99,
    ),

    # --------------------------------------------------------
    # REFUNDED
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.REFUNDED,
        phrases=(
            "refund completed",
            "refund processed",
            "money refunded",
            "refund successful",
            "amount refunded",
            "refund issued",
            "refund initiated",
            "refund has been processed",
        ),
        negative_phrases=(
            "refund failed",
        ),
        confidence=0.99,
    ),

    # --------------------------------------------------------
    # EXCHANGED
    # --------------------------------------------------------

    StatusRule(
        canonical_status=OrderStatus.EXCHANGED,
        phrases=(
            "exchange completed",
            "exchange processed",
            "replacement shipped",
            "replacement dispatched",
            "new product shipped",
            "exchange successful",
        ),
        negative_phrases=(),
        confidence=0.98,
    ),

]
MATCHER = OrderStatusMatcher(ORDER_STATUS_RULES)
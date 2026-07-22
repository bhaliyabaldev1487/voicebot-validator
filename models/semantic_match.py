"""
models/semantic_match.py

Common semantic matching models used by all rule engines.

These models are intentionally generic and reusable across:
    - Order Status
    - Payment Status
    - Shipment Status
    - Return Status
    - Refund Status

Author: Voicebot Validator
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ----------------------------------------------------------------------
# Match Type
# ----------------------------------------------------------------------


class MatchType(str, Enum):
    """
    Indicates how a semantic match was identified.
    """

    EXACT = "EXACT"

    REGEX = "REGEX"

    FUZZY = "FUZZY"

    SYNONYM = "SYNONYM"

    CONTEXT = "CONTEXT"

    AI = "AI"

    UNKNOWN = "UNKNOWN"


# ----------------------------------------------------------------------
# Semantic Evidence
# ----------------------------------------------------------------------


@dataclass(slots=True)
class SemanticEvidence:
    """
    Explains WHY a rule matched.

    Example:

        matched_phrase = "being stitched"

        sentence =
        "Your lehenga is currently being stitched."

        confidence = 0.98
    """

    matched_phrase: Optional[str] = None

    matched_pattern: Optional[str] = None

    sentence: Optional[str] = None

    start_index: Optional[int] = None

    end_index: Optional[int] = None

    confidence: float = 0.0

    match_type: MatchType = MatchType.UNKNOWN

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {
            "matched_phrase": self.matched_phrase,
            "matched_pattern": self.matched_pattern,
            "sentence": self.sentence,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "confidence": self.confidence,
            "match_type": self.match_type.value,
            "metadata": self.metadata,
        }


# ----------------------------------------------------------------------
# Status Rule
# ----------------------------------------------------------------------


@dataclass(slots=True)
class StatusRule:
    """
    One semantic rule.

    Example:

        PROCESSING

        phrases:
            "being stitched"
            "currently processing"
            "under tailoring"
    """

    canonical_status: Any

    phrases: List[str]

    negative_phrases: List[str] = field(default_factory=list)

    regex_patterns: List[str] = field(default_factory=list)

    confidence: float = 1.0

    priority: int = 100

    enabled: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:

        return {

            "status": str(self.canonical_status),

            "phrases": self.phrases,

            "negative_phrases": self.negative_phrases,

            "regex_patterns": self.regex_patterns,

            "confidence": self.confidence,

            "priority": self.priority,

            "enabled": self.enabled,

            "metadata": self.metadata,

        }


# ----------------------------------------------------------------------
# Status Match
# ----------------------------------------------------------------------


@dataclass(slots=True)
class StatusMatch:
    """
    Result returned by a semantic matcher.
    """

    status: Any

    confidence: float

    evidence: SemanticEvidence

    rule: Optional[StatusRule] = None

    score: float = 0.0

    is_negative_match: bool = False

    def passed(self, threshold: float = 0.80) -> bool:

        return self.confidence >= threshold

    def to_dict(self):

        return {

            "status": str(self.status),

            "confidence": round(self.confidence, 3),

            "score": round(self.score, 3),

            "negative_match": self.is_negative_match,

            "evidence": self.evidence.to_dict(),

            "rule": self.rule.to_dict() if self.rule else None,

        }


# ----------------------------------------------------------------------
# Semantic Result
# ----------------------------------------------------------------------


@dataclass(slots=True)
class SemanticResult:
    """
    Complete document-level matching result.
    """

    document: str

    matches: List[StatusMatch] = field(default_factory=list)

    processing_time_ms: float = 0.0

    def add(self, match: StatusMatch):

        self.matches.append(match)

    @property
    def best_match(self) -> Optional[StatusMatch]:

        if not self.matches:

            return None

        return max(
            self.matches,
            key=lambda x: x.confidence,
        )

    @property
    def matched(self) -> bool:

        return len(self.matches) > 0

    @property
    def statuses(self):

        seen = []

        for match in self.matches:

            if match.status not in seen:

                seen.append(match.status)

        return seen

    def sort(self):

        self.matches.sort(
            key=lambda x: (
                x.confidence,
                x.score,
            ),
            reverse=True,
        )

    def to_dict(self):

        return {

            "matched": self.matched,

            "processing_time_ms": round(
                self.processing_time_ms,
                2,
            ),

            "best_match": (
                self.best_match.to_dict()
                if self.best_match
                else None
            ),

            "statuses": [
                str(s)
                for s in self.statuses
            ],

            "matches": [
                m.to_dict()
                for m in self.matches
            ],

        }


# ----------------------------------------------------------------------
# Validation Comparison
# ----------------------------------------------------------------------


@dataclass(slots=True)
class SemanticComparison:
    """
    Compare expected DB value vs extracted bot value.
    """

    expected: Any

    actual: Any

    matched: bool

    confidence: float

    evidence: Optional[SemanticEvidence] = None

    reason: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):

        return {

            "expected": str(self.expected),

            "actual": str(self.actual),

            "matched": self.matched,

            "confidence": round(
                self.confidence,
                3,
            ),

            "reason": self.reason,

            "evidence": (
                self.evidence.to_dict()
                if self.evidence
                else None
            ),

            "metadata": self.metadata,

        }
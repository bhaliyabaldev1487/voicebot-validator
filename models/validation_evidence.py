from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ValidationEvidence:
    """
    Represents one validation result produced by a rule.
    """

    field_name: str
    expected: str
    actual: str
    passed: bool

    severity: str = "MEDIUM"

    confidence: float = 1.0

    details: str = ""

    db_column: str = ""

    bot_sentence: str = ""

    def to_dict(self):
        return asdict(self)
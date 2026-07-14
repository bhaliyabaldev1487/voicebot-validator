from dataclasses import dataclass


@dataclass
class ValidationEvidence:

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

        return {

            "field": self.field_name,

            "expected": self.expected,

            "actual": self.actual,

            "passed": self.passed,

            "severity": self.severity,

            "confidence": self.confidence,

            "details": self.details,

            "db_column": self.db_column,

            "bot_sentence": self.bot_sentence,

        }
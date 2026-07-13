from dataclasses import dataclass

@dataclass
class ValidationEvidence:

    field_name: str

    expected: str

    actual: str

    passed: bool

    confidence: float = 1.0

    bot_sentence: str = ""

    db_column: str = ""

    def to_dict(self):
        return vars(self)
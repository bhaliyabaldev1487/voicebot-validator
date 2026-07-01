from dataclasses import dataclass
from typing import Any


@dataclass
class Evidence:

    type: str

    value: Any

    speaker: str

    text: str

    confidence: float = 1.0

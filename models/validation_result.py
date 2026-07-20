from __future__ import annotations

from dataclasses import dataclass, field

from models.validation_evidence import ValidationEvidence


@dataclass
class ValidationResult:

    checks: list[ValidationEvidence] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    @property
    def success(self) -> bool:
        return self.failed == 0

    @property
    def score(self) -> float:

        if not self.checks:
            return 0.0

        return round((self.passed / len(self.checks)) * 100, 2)

    def to_dict(self):

        return {
            "success": self.success,
            "summary": f"{self.passed}/{len(self.checks)} checks passed",
            "score": self.score,
            "passed": self.passed,
            "failed": self.failed,
            "checks": [c.to_dict() for c in self.checks],
        }
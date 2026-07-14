from dataclasses import dataclass, field

from models.validation_evidence import ValidationEvidence


@dataclass
class ValidationResult:

    checks: list[ValidationEvidence] = field(default_factory=list)

    @property
    def passed(self):
        return sum(c.passed for c in self.checks)

    @property
    def failed(self):
        return len(self.checks) - self.passed

    @property
    def success(self):
        return self.failed == 0

    @property
    def score(self):

        if not self.checks:
            return 0

        return round(
            self.passed * 100 / len(self.checks),
            2,
        )

    def to_dict(self):

        return {
            "success": self.success,
            "score": self.score,
            "passed": self.passed,
            "failed": self.failed,
            "checks": [c.to_dict() for c in self.checks],
        }
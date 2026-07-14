from typing import List

from models.validation_context import ValidationContext
from models.validation_evidence import ValidationEvidence
from validators.rules.base_rule import ValidationRule
from models.validation_result import ValidationResult

class RuleEngine:

    def __init__(self, rules: List[ValidationRule]):
        self.rules = rules

    def execute(
        self,
        context: ValidationContext,
    ) -> List[ValidationEvidence]:

        evidence = []

        for rule in self.rules:

            try:

                result = rule.validate(context)

                if result:
                    evidence.append(result)

            except Exception as ex:

                evidence.append(
                    ValidationEvidence(
                        field_name=rule.__class__.__name__,
                        expected="",
                        actual="",
                        passed=False,
                        severity="CRITICAL",
                        details=str(ex),
                    )
                )

        return ValidationResult(
            checks=evidence,
        )
"""
Executes all validation rules.
"""

from __future__ import annotations

from typing import List

from models.validation_context import ValidationContext
from models.validation_evidence import ValidationEvidence
from models.validation_result import ValidationResult
from validators.rules.base_rule import ValidationRule


class RuleEngine:

    def __init__(
        self,
        rules: List[ValidationRule],
    ):
        self.rules = rules

    def execute(
        self,
        context: ValidationContext,
    ) -> ValidationResult:

        result = ValidationResult()

        for rule in self.rules:

            try:

                evidence = rule.validate(context)

                if evidence:
                    result.checks.append(evidence)

            except Exception as ex:

                result.checks.append(
                    ValidationEvidence(
                        field_name=rule.__class__.__name__,
                        expected="",
                        actual="",
                        passed=False,
                        severity="CRITICAL",
                        details=str(ex),
                    )
                )

        return result
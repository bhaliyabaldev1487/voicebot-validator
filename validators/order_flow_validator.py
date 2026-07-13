from dataclasses import dataclass, field, asdict
from typing import List, Optional

from models.validation_context import ValidationContext


@dataclass
class ValidationCheck:
    name: str
    passed: bool
    expected: Optional[str] = None
    actual: Optional[str] = None
    details: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class ValidationResult:
    success: bool
    checks: List[ValidationCheck] = field(default_factory=list)
    summary: str = ""

    @property
    def passed_checks(self):
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed_checks(self):
        return sum(1 for c in self.checks if not c.passed)

    def to_dict(self):
        return {
            "success": self.success,
            "summary": self.summary,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "checks": [c.to_dict() for c in self.checks],
        }


class OrderFlowValidator:
    """
    Validates the bot's response for Order flow against the
    actual customer and order data retrieved from the database.
    """

    def validate(self, context: ValidationContext) -> ValidationResult:

        checks = []

        lookup = context.lookup_result

        # -------------------------
        # Customer found
        # -------------------------
        checks.append(
            ValidationCheck(
                name="Customer Found",
                passed=lookup.customer is not None,
                expected="Customer exists",
                actual="Found" if lookup.customer else "Not Found",
            )
        )

        # -------------------------
        # Order found
        # -------------------------
        checks.append(
            ValidationCheck(
                name="Order Found",
                passed=lookup.order is not None,
                expected="Order exists",
                actual="Found" if lookup.order else "Not Found",
            )
        )

        transcript = context.transcript.customer_text.lower()

        # -------------------------
        # Order Number validation
        # -------------------------
        if lookup.order and context.entities.order_number:

            expected = lookup.order.customer_order_number
            actual = context.entities.order_number

            checks.append(
                ValidationCheck(
                    name="Order Number",
                    passed=expected == actual,
                    expected=expected,
                    actual=actual,
                )
            )

        # -------------------------
        # Shipping Status validation
        # -------------------------
        if lookup.order:

            db_status = lookup.order.order_status.upper()

            bot_status = None

            for status in [
                "PROCESSING",
                "SHIPPING",
                "DELIVERED",
                "CANCELLED",
            ]:
                if status.lower() in transcript:
                    bot_status = status
                    break

            if bot_status:

                checks.append(
                    ValidationCheck(
                        name="Order Status",
                        passed=(bot_status == db_status),
                        expected=db_status,
                        actual=bot_status,
                    )
                )

        passed = all(c.passed for c in checks)

        return ValidationResult(
            success=passed,
            checks=checks,
            summary=f"{sum(c.passed for c in checks)}/{len(checks)} checks passed",
        )
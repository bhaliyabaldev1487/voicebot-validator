from models.validation_evidence import ValidationEvidence
from validators.rules.base_rule import ValidationRule


class OrderStatusRule(ValidationRule):

    def validate(self, context):

        order = context.lookup_result.order

        if order is None:

            return ValidationEvidence(
                field_name="Order Status",
                expected="Order should exist",
                actual="No Order",
                passed=False,
                severity="CRITICAL",
            )

        expected = order.shipping_status.upper()

        actual = (
            context.bot_response.order_status or ""
        ).upper()

        passed = expected == actual

        return ValidationEvidence(
            field_name="Order Status",
            expected=expected,
            actual=actual,
            passed=passed,
            severity="CRITICAL",
            db_column="mx_order.orderStatus",
        )
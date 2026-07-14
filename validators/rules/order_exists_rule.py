from models.validation_evidence import ValidationEvidence
from validators.rules.base_rule import ValidationRule


class OrderExistsRule(ValidationRule):

    def validate(self, context):

        order = context.lookup_result.order

        return ValidationEvidence(

            field_name="Order Exists",

            expected="Order",

            actual="Found" if order else "Not Found",

            passed=order is not None,

            severity="CRITICAL",
        )
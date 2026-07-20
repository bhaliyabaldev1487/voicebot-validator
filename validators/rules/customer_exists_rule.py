"""
Customer existence validation rule.
"""

from models.validation_evidence import ValidationEvidence
from validators.rules.base_rule import ValidationRule


class CustomerExistsRule(ValidationRule):

    def validate(self, context):

        customer = context.lookup_result.customer

        return ValidationEvidence(
            field_name="Customer Exists",
            expected="Customer should exist",
            actual="Found" if customer else "Not Found",
            passed=customer is not None,
            severity="CRITICAL",
            db_column="mx_site_user.site_user_id",
            details="Customer lookup validation",
        )
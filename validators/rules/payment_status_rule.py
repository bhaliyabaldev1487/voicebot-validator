from models.validation_evidence import ValidationEvidence
from nlp.semantic_matcher import SemanticMatcher
from validators.rules.base_rule import ValidationRule


class PaymentStatusRule(ValidationRule):

    def __init__(self):

        self.matcher = SemanticMatcher()

    def validate(self, context):

        db = context.lookup_result.order

        bot_text = context.bot_text

        expected = ""

        if db:

            expected = db.order_status

        passed = self.matcher.status_matches(
            expected,
            bot_text,
        )

        return ValidationEvidence(

            field_name="Order Status",

            expected=expected,

            actual=bot_text,

            passed=passed,
        )
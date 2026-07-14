from models.validation_evidence import ValidationEvidence
from validators.rules.base_rule import ValidationRule


class OrderNumberRule(ValidationRule):

    def validate(self, context):

        db_order = context.lookup_result.order

        bot = context.bot_response

        expected = ""

        actual = ""

        if db_order:
            expected = db_order.customer_order_number

        if bot:
            actual = bot.order_number

        passed = (
            expected is not None
            and actual is not None
            and expected.upper() == actual.upper()
        )

        return ValidationEvidence(

            field_name="Order Number",

            expected=expected,

            actual=actual,

            passed=passed,
        )
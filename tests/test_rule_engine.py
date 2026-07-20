from validators.rule_engine import RuleEngine
from validators.rules.base_rule import ValidationRule
from models.validation_evidence import ValidationEvidence


class DummyRule(ValidationRule):

    def validate(self, context):

        return ValidationEvidence(
            field_name="Dummy",
            expected="1",
            actual="1",
            passed=True,
        )


engine = RuleEngine([DummyRule()])

print(engine)
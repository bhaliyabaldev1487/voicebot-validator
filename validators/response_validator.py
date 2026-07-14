from validators.rule_engine import RuleEngine
from validators.rules import DEFAULT_RULES


class ResponseValidator:

    def __init__(self):
        self.engine = RuleEngine(
            [rule() for rule in DEFAULT_RULES]
        )

    def validate(self, context):
        return self.engine.execute(context)
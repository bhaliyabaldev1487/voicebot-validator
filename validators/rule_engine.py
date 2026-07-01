class RuleEngine:

    def __init__(self):

        self.rules = []

    def register(self, rule):

        self.rules.append(rule)

    def execute(self, context):

        results = []

        for rule in self.rules:

            results.append(

                rule.validate(context)

            )

        return results

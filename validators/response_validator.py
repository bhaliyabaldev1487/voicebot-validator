"""
Main validator which executes all business rules.
"""

from validators.rule_engine import RuleEngine

from validators.rules.customer_exists_rule import CustomerExistsRule
from validators.rules.order_exists_rule import OrderExistsRule
from validators.rules.order_status_rule import OrderStatusRule

class ResponseValidator:

    def __init__(self):

        self.engine = RuleEngine(
        rules=[

            CustomerExistsRule(),

            OrderExistsRule(),

            OrderStatusRule(),
        ]
    )

    def validate(self, context):

        return self.engine.execute(context)
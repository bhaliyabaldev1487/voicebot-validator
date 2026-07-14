from validators.rules.customer_exists_rule import CustomerExistsRule
from validators.rules.order_exists_rule import OrderExistsRule
from validators.rules.order_number_rule import OrderNumberRule
from validators.rules.order_status_rule import OrderStatusRule
from validators.rules.payment_status_rule import PaymentStatusRule

DEFAULT_RULES = [
    CustomerExistsRule,
    OrderExistsRule,
    OrderNumberRule,
    OrderStatusRule,
    PaymentStatusRule,
]
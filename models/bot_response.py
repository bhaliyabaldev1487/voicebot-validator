from dataclasses import dataclass
from typing import Optional


@dataclass
class BotOrderResponse:

    order_number: Optional[str] = None

    order_status: Optional[str] = None

    payment_status: Optional[str] = None

    courier: Optional[str] = None

    tracking_number: Optional[str] = None

    delivery_date: Optional[str] = None

    total_amount: Optional[str] = None

    currency: Optional[str] = None

    shipping_city: Optional[str] = None

    shipping_state: Optional[str] = None

    shipping_pincode: Optional[str] = None

    def to_dict(self):
        return vars(self)
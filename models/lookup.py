from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from models.customer import Customer
from models.order import Order
from models.order_item import OrderItem


@dataclass
class OrderLookupRequest:
    caller_phone: Optional[str] = None
    order_number: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_mobile: Optional[str] = None
    customer_email: Optional[str] = None


@dataclass
class LookupResult:
    customer: Optional[Customer] = None
    order: Optional[Order] = None
    order_items: List[OrderItem] = field(default_factory=list)

    # Optional compatibility fields
    success: bool = False
    lookup_method: Optional[str] = None
    message: str = ""

    def to_dict(self):
        return {
            "success": self.success,
            "lookup_method": self.lookup_method,
            "message": self.message,
            "customer": self.customer.to_dict() if self.customer else None,
            "order": self.order.to_dict() if self.order else None,
            "order_items": [
                item.to_dict() for item in self.order_items
            ],
        }
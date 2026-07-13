from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.customer import Customer
from models.order import Order


@dataclass
class OrderLookupRequest:
    caller_phone: Optional[str] = None
    order_number: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_mobile: Optional[str] = None
    customer_email: Optional[str] = None


@dataclass
class LookupResult:
    success: bool
    customer: Optional[Customer]
    order: Optional[Order]
    lookup_method: Optional[str]
    message: str

    def to_dict(self):
        return {
            "success": self.success,
            "lookup_method": self.lookup_method,
            "message": self.message,
            "customer": self.customer.to_dict() if self.customer else None,
            "order": self.order.to_dict() if self.order else None,
        }
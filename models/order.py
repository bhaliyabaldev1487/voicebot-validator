from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Order:
    order_id: int
    customer_order_number: Optional[str]
    site_user_id: int
    order_status: str
    payment_status: Optional[str]
    total_price: Decimal
    date_added: Optional[str] = None

    @property
    def shipping_status(self) -> str:
        return (self.order_status or "").upper().strip()

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "customer_order_number": self.customer_order_number,
            "site_user_id": self.site_user_id,
            "order_status": self.order_status,
            "shipping_status": self.shipping_status,
            "payment_status": self.payment_status,
            "total_price": str(self.total_price),
            "date_added": self.date_added,
        }
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderItem:

    order_detail_id: int
    order_id: int

    product_title: str
    aza_code: Optional[str]

    quantity: int

    shipping_status: Optional[str]

    courier: Optional[str]

    tracking_id: Optional[str]

    expected_delivery_date: Optional[str]

    designer_name: Optional[str]

    color: Optional[str]

    size: Optional[str]

    def to_dict(self):

        return {
            "order_detail_id": self.order_detail_id,
            "order_id": self.order_id,
            "product_title": self.product_title,
            "aza_code": self.aza_code,
            "quantity": self.quantity,
            "shipping_status": self.shipping_status,
            "courier": self.courier,
            "tracking_id": self.tracking_id,
            "expected_delivery_date": self.expected_delivery_date,
            "designer_name": self.designer_name,
            "color": self.color,
            "size": self.size,
        }
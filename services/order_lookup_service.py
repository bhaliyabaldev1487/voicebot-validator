from __future__ import annotations

from typing import Optional

from database.provider import DatabaseProvider
from models.customer import Customer
from models.lookup import LookupResult, OrderLookupRequest
from models.order import Order


class OrderLookupService:
    def __init__(self, db: DatabaseProvider) -> None:
        self.db = db

    def lookup(self, request: OrderLookupRequest) -> LookupResult:
        """
        Lookup priority:
        1. Order number directly
        2. Customer phone from transcript
        3. Customer mobile from transcript
        4. Customer email from transcript
        5. Caller phone
        """
        if request.order_number:
            order = self.db.find_order_by_order_number(request.order_number)
            if order:
                return LookupResult(
                    success=True,
                    customer=None,
                    order=order,
                    lookup_method="order_number",
                    message="Order found by order number",
                )

        customer = self._find_customer(request)
        if not customer:
            return LookupResult(
                success=False,
                customer=None,
                order=None,
                lookup_method=None,
                message="Customer not found",
            )

        order = self.db.find_latest_order_for_customer(customer.site_user_id)
        if not order:
            return LookupResult(
                success=False,
                customer=customer,
                order=None,
                lookup_method="customer",
                message="Customer found but no order found",
            )

        return LookupResult(
            success=True,
            customer=customer,
            order=order,
            lookup_method="customer",
            message="Customer and order found",
        )

    def _find_customer(self, request: OrderLookupRequest) -> Optional[Customer]:
        if request.customer_phone:
            customer = self.db.find_customer_by_phone(request.customer_phone)
            if customer:
                return customer

        if request.customer_mobile:
            customer = self.db.find_customer_by_mobile(request.customer_mobile)
            if customer:
                return customer

        if request.customer_email:
            customer = self.db.find_customer_by_email(request.customer_email)
            if customer:
                return customer

        if request.caller_phone:
            customer = self.db.find_customer_by_phone(request.caller_phone)
            if customer:
                return customer

            customer = self.db.find_customer_by_mobile(request.caller_phone)
            if customer:
                return customer

        return None
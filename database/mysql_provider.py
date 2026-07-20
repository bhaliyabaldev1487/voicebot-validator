from __future__ import annotations

from typing import Optional

from database.provider import DatabaseProvider
from database.repository import OrderRepository
from database.session import create_session_factory
from models.lookup import LookupResult


class MySQLDatabaseProvider(DatabaseProvider):
    """
    Database provider backed by MySQL.
    """

    def __init__(
        self,
        connection_url: Optional[str] = None,
        echo: bool = False,
    ):

        SessionFactory = create_session_factory(
            connection_url=connection_url,
            echo=echo,
        )
        self.session = SessionFactory()

        self.repository = OrderRepository(self.session)

    def lookup(self, request) -> LookupResult:
        """
        Fetch customer, order and all sub-order items.
        """

        # -----------------------------------
        # Customer
        # -----------------------------------

        customer = self.repository.find_customer(
            caller_phone=request.caller_phone,
            customer_phone=request.customer_phone,
            customer_mobile=request.customer_mobile,
            customer_email=request.customer_email,
        )

        if not customer:
            return LookupResult()

        # -----------------------------------
        # Order
        # -----------------------------------

        order = self.repository.find_order(
            site_user_id=customer.site_user_id,
            order_number=request.order_number,
        )

        if not order:
            return LookupResult(
                customer=customer,
                order=None,
                order_items=[],
            )
        # -----------------------------------
        # Order Items
        # -----------------------------------

        order_items = self.repository.get_order_items(
            order.order_id,
        )

        return LookupResult(
            customer=customer,
            order=order,
            order_items=order_items,
        )

    def close(self):

        self.session.close()
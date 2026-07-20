from __future__ import annotations

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.mapper import to_customer, to_order
from database.models import Order as OrderORM
from database.models import SiteUser
from models.customer import Customer
from models.order import Order
from database.models import OrderDetail
from models.order_item import OrderItem
from database.mapper import map_order_item

class OrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_customer(
        self,
        caller_phone: str | None = None,
        customer_phone: str | None = None,
        customer_mobile: str | None = None,
        customer_email: str | None = None,
    ):
        """
        Resolve customer using available identifiers.
        Priority:
        caller_phone -> customer_phone -> mobile -> email
        """

        if caller_phone:
            customer = self.find_customer_by_phone(caller_phone)
            if customer:
                return customer

        if customer_phone:
            customer = self.find_customer_by_phone(customer_phone)
            if customer:
                return customer

        if customer_mobile:
            customer = self.find_customer_by_mobile(customer_mobile)
            if customer:
                return customer

        if customer_email:
            customer = self.find_customer_by_email(customer_email)
            if customer:
                return customer

        return None

    def find_order(
        self,
        site_user_id: int,
        order_number: str | None = None,
    ):
        """
        Find an order either by order number or latest order.
        """
        if order_number:
            order = self.find_order_by_order_number(order_number)
            if order:
                return order
        return self.find_latest_order_for_customer(site_user_id)


    def find_customer_by_phone(self, phone: str) -> Optional[Customer]:
        row = (
            self.session.query(SiteUser)
            .filter(SiteUser.phoneNo == phone)
            .order_by(SiteUser.siteUserID.desc())
            .first()
        )
        return to_customer(row) if row else None

    def find_customer_by_mobile(self, mobile: str) -> Optional[Customer]:
        row = (
            self.session.query(SiteUser)
            .filter(SiteUser.mobile == mobile)
            .order_by(SiteUser.siteUserID.desc())
            .first()
        )
        return to_customer(row) if row else None

    def find_customer_by_email(self, email: str) -> Optional[Customer]:
        row = (
            self.session.query(SiteUser)
            .filter(
                or_(
                    SiteUser.userEmail == email,
                    SiteUser.communicationEmail == email,
                )
            )
            .order_by(SiteUser.siteUserID.desc())
            .first()
        )
        return to_customer(row) if row else None

    def find_order_by_order_number(self, order_number: str) -> Optional[Order]:
        row = (
            self.session.query(OrderORM)
            .filter(OrderORM.customerOrderNumber == order_number)
            .order_by(OrderORM.orderID.desc())
            .first()
        )
        print("Row data from table for order number:", row)
        return to_order(row) if row else None

    def find_latest_order_for_customer(self, site_user_id: int) -> Optional[Order]:
        row = (
            self.session.query(OrderORM)
            .filter(OrderORM.siteUserID == site_user_id)
            .order_by(OrderORM.orderID.desc())
            .first()
        )
        return to_order(row) if row else None
    
    def get_order_items(
        self,
        order_id: int,
        ) -> list[OrderItem]:

        rows = (
            self.session.query(OrderDetail)
            .filter(
                OrderDetail.order_id == order_id
            )
            .all()
        )

        return [
            map_order_item(r)
            for r in rows
        ]
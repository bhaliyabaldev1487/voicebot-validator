from __future__ import annotations

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from database.mapper import to_customer, to_order
from database.models import Order as OrderORM
from database.models import SiteUser
from models.customer import Customer
from models.order import Order


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

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
        return to_order(row) if row else None

    def find_latest_order_for_customer(self, site_user_id: int) -> Optional[Order]:
        row = (
            self.session.query(OrderORM)
            .filter(OrderORM.siteUserID == site_user_id)
            .order_by(OrderORM.orderID.desc())
            .first()
        )
        return to_order(row) if row else None
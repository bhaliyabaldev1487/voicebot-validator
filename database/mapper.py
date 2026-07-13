from __future__ import annotations

from decimal import Decimal, InvalidOperation

from database.models import Order as OrderORM
from database.models import SiteUser
from models.customer import Customer
from models.order import Order


def _to_decimal(value: object) -> Decimal:
    if value is None:
        return Decimal("0")
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return Decimal("0")


def to_customer(row: SiteUser) -> Customer:
    return Customer(
        site_user_id=row.siteUserID,
        first_name=row.userFName or "",
        last_name=row.userLName or "",
        email=row.userEmail or row.communicationEmail,
        phone_no=row.phoneNo,
        mobile=row.mobile,
    )


def to_order(row: OrderORM) -> Order:
    return Order(
        order_id=row.orderID,
        customer_order_number=row.customerOrderNumber,
        site_user_id=row.siteUserID,
        order_status=row.orderStatus,
        payment_status=row.paymentStatus,
        total_price=_to_decimal(row.totalPrice),
        date_added=str(row.dateAdded) if row.dateAdded else None,
    )
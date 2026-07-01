"""
database/models.py

SQLAlchemy ORM Models for VoiceBot Validator

Only fields required by the validator are mapped.
Additional fields can be added later when implementing
Shipping / Return / Refund validation.

Author: VoiceBot Validator
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


# -------------------------------------------------------------------------
# Base
# -------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


# -------------------------------------------------------------------------
# Customer
# -------------------------------------------------------------------------


class SiteUser(Base):
    """
    mx_site_user
    """

    __tablename__ = "mx_site_user"

    siteUserID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    userFName: Mapped[str] = mapped_column(String(256))

    userLName: Mapped[str] = mapped_column(String(256))

    userEmail: Mapped[str] = mapped_column(
        String(256),
        unique=True,
        index=True,
    )

    phoneNo: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    mobile: Mapped[str] = mapped_column(
        String(15),
        index=True,
    )

    mobile_code: Mapped[str] = mapped_column(
        String(4),
        default=""
    )

    email_verified: Mapped[int]

    mobile_verified: Mapped[int]

    status: Mapped[int]

    countryName: Mapped[str]

    city: Mapped[str]

    loyalty_points: Mapped[int]

    dateAdded: Mapped[datetime] = mapped_column(DateTime)

    dateModified: Mapped[datetime] = mapped_column(DateTime)

    orders = relationship(
        "Order",
        back_populates="customer",
        lazy="selectin",
    )

    @property
    def full_name(self):

        return f"{self.userFName} {self.userLName}".strip()

    def __repr__(self):

        return (
            f"<SiteUser("
            f"id={self.siteUserID}, "
            f"name='{self.full_name}')>"
        )


# -------------------------------------------------------------------------
# Order
# -------------------------------------------------------------------------


class Order(Base):
    """
    mx_order
    """

    __tablename__ = "mx_order"

    orderID: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    customerOrderNumber: Mapped[str | None] = mapped_column(
        String(50),
        index=True,
    )

    siteUserID: Mapped[int] = mapped_column(
        ForeignKey("mx_site_user.siteUserID"),
        index=True,
    )

    PaymentMethod: Mapped[str] = mapped_column(
        String(100)
    )

    PaymentID: Mapped[str]

    TransactionID: Mapped[str]

    MerchantRefNo: Mapped[str]

    orderStatus: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    paymentStatus: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )

    totalPrice: Mapped[str]

    currency: Mapped[str]

    shippingPhone: Mapped[str]

    shippingEmail: Mapped[str]

    shippingCity: Mapped[str]

    shippingState: Mapped[str]

    shippingCountry: Mapped[str]

    billingPhone: Mapped[str]

    billingEmail: Mapped[str]

    dateAdded: Mapped[datetime] = mapped_column(
        DateTime,
        index=True,
    )

    dateModified: Mapped[datetime]

    status: Mapped[int]

    customer = relationship(
        "SiteUser",
        back_populates="orders",
        lazy="joined",
    )

    @property
    def is_paid(self):

        return self.paymentStatus.lower() in (
            "paid",
            "captured",
            "success",
        )

    @property
    def is_delivered(self):

        return self.orderStatus.lower() == "delivered"

    def __repr__(self):

        return (
            f"<Order("
            f"id={self.orderID}, "
            f"customerOrderNumber='{self.customerOrderNumber}', "
            f"status='{self.orderStatus}')>"
        )

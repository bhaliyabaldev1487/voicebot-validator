from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SiteUser(Base):
    __tablename__ = "mx_site_user"

    siteUserID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userFName: Mapped[str] = mapped_column(String(256), nullable=False)
    userLName: Mapped[str] = mapped_column(String(256), nullable=False)
    userEmail: Mapped[str] = mapped_column(String(256), nullable=False)
    phoneNo: Mapped[str] = mapped_column(String(100), nullable=False)
    mobile: Mapped[str] = mapped_column(String(15), nullable=False)
    mobile_code: Mapped[str] = mapped_column(String(4), nullable=False, default="")
    communicationEmail: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return (
            "SiteUser("
            f"siteUserID={self.siteUserID}, "
            f"userEmail={self.userEmail!r}, "
            f"phoneNo={self.phoneNo!r}, "
            f"mobile={self.mobile!r})"
        )


class Order(Base):
    __tablename__ = "mx_order"

    orderID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customerOrderNumber: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    siteUserID: Mapped[int] = mapped_column(Integer, nullable=False)
    siteUserName: Mapped[str] = mapped_column(String(255), nullable=False)
    siteUserEmail: Mapped[str] = mapped_column(String(255), nullable=False)

    shippingPhone: Mapped[str] = mapped_column(String(100), nullable=False)
    shippingEmail: Mapped[str] = mapped_column(String(100), nullable=False)

    orderStatus: Mapped[str] = mapped_column(String(100), nullable=False)
    paymentStatus: Mapped[str] = mapped_column(String(50), nullable=False)

    totalPrice: Mapped[str] = mapped_column(String(50), nullable=False)
    dateAdded: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    communication_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return (
            "Order("
            f"orderID={self.orderID}, "
            f"customerOrderNumber={self.customerOrderNumber!r}, "
            f"siteUserID={self.siteUserID}, "
            f"orderStatus={self.orderStatus!r})"
        )
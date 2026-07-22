"""
models/canonical_status.py

Canonical business status definitions used throughout the Voicebot
Validator.

This module intentionally contains only enum definitions and lightweight
helper methods. Matching logic, normalization and semantic rules belong
to the rule engine.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Optional, Type, TypeVar

T = TypeVar("T", bound="CanonicalEnum")


class CanonicalEnum(str, Enum):
    """
    Base enum for all canonical statuses.
    """

    @classmethod
    def normalize(cls: Type[T], value: Optional[str]) -> T:
        """
        Convert arbitrary string into canonical enum.

        Unknown values always map to UNKNOWN.
        """

        if value is None:
            return cls.UNKNOWN

        normalized = (
            str(value)
            .strip()
            .replace("-", "_")
            .replace(" ", "_")
            .upper()
        )

        for member in cls:
            if member.name == normalized:
                return member

            if member.value == normalized:
                return member

        return cls.UNKNOWN

    @classmethod
    def values(cls) -> list[str]:
        return [item.value for item in cls]

    @classmethod
    def names(cls) -> list[str]:
        return [item.name for item in cls]

    @classmethod
    def contains(cls, value: Optional[str]) -> bool:
        return cls.normalize(value) != cls.UNKNOWN

    @property
    def label(self) -> str:
        return self.value.replace("_", " ").title()

    def __str__(self) -> str:
        return self.value


# ----------------------------------------------------------------------
# Order
# ----------------------------------------------------------------------


class OrderStatus(CanonicalEnum):

    UNKNOWN = "UNKNOWN"

    PLACED = "PLACED"

    CONFIRMED = "CONFIRMED"

    PROCESSING = "PROCESSING"

    READY_TO_SHIP = "READY_TO_SHIP"

    SHIPPED = "SHIPPED"

    IN_TRANSIT = "IN_TRANSIT"

    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"

    DELIVERED = "DELIVERED"

    CANCELLED = "CANCELLED"

    RETURN_REQUESTED = "RETURN_REQUESTED"

    RETURN_APPROVED = "RETURN_APPROVED"

    RETURN_REJECTED = "RETURN_REJECTED"

    RETURNED = "RETURNED"

    EXCHANGE_REQUESTED = "EXCHANGE_REQUESTED"

    EXCHANGED = "EXCHANGED"

    REFUND_INITIATED = "REFUND_INITIATED"

    REFUNDED = "REFUNDED"

    FAILED = "FAILED"


# ----------------------------------------------------------------------
# Payment
# ----------------------------------------------------------------------


class PaymentStatus(CanonicalEnum):

    UNKNOWN = "UNKNOWN"

    PENDING = "PENDING"

    SUCCESS = "SUCCESS"

    FAILED = "FAILED"

    AUTHORIZED = "AUTHORIZED"

    CAPTURED = "CAPTURED"

    REFUNDED = "REFUNDED"

    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"

    CANCELLED = "CANCELLED"

    COD = "COD"


# ----------------------------------------------------------------------
# Shipment
# ----------------------------------------------------------------------


class ShipmentStatus(CanonicalEnum):

    UNKNOWN = "UNKNOWN"

    NOT_SHIPPED = "NOT_SHIPPED"

    READY_TO_SHIP = "READY_TO_SHIP"

    SHIPPED = "SHIPPED"

    IN_TRANSIT = "IN_TRANSIT"

    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"

    DELIVERED = "DELIVERED"

    DELAYED = "DELAYED"

    LOST = "LOST"

    RETURN_TO_ORIGIN = "RETURN_TO_ORIGIN"

    CANCELLED = "CANCELLED"


# ----------------------------------------------------------------------
# Return
# ----------------------------------------------------------------------


class ReturnStatus(CanonicalEnum):

    UNKNOWN = "UNKNOWN"

    REQUESTED = "REQUESTED"

    APPROVED = "APPROVED"

    REJECTED = "REJECTED"

    PICKUP_SCHEDULED = "PICKUP_SCHEDULED"

    PICKED_UP = "PICKED_UP"

    RECEIVED = "RECEIVED"

    COMPLETED = "COMPLETED"

    CANCELLED = "CANCELLED"


# ----------------------------------------------------------------------
# Exchange
# ----------------------------------------------------------------------


class ExchangeStatus(CanonicalEnum):

    UNKNOWN = "UNKNOWN"

    REQUESTED = "REQUESTED"

    APPROVED = "APPROVED"

    REJECTED = "REJECTED"

    SHIPPED = "SHIPPED"

    DELIVERED = "DELIVERED"

    COMPLETED = "COMPLETED"

    CANCELLED = "CANCELLED"


# ----------------------------------------------------------------------
# Refund
# ----------------------------------------------------------------------


class RefundStatus(CanonicalEnum):

    UNKNOWN = "UNKNOWN"

    INITIATED = "INITIATED"

    PROCESSING = "PROCESSING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    CANCELLED = "CANCELLED"


# ----------------------------------------------------------------------
# Registry
# ----------------------------------------------------------------------


STATUS_REGISTRY: Dict[str, Type[CanonicalEnum]] = {

    "order": OrderStatus,

    "payment": PaymentStatus,

    "shipment": ShipmentStatus,

    "return": ReturnStatus,

    "exchange": ExchangeStatus,

    "refund": RefundStatus,

}


def normalize_status(
    category: str,
    value: Optional[str],
) -> CanonicalEnum:
    """
    Generic normalization helper.

    Example:
        normalize_status("order", "processing")
        -> OrderStatus.PROCESSING
    """

    enum_cls = STATUS_REGISTRY.get(category.lower())

    if enum_cls is None:
        raise ValueError(
            f"Unsupported status category: {category}"
        )

    return enum_cls.normalize(value)


def is_known_status(
    category: str,
    value: Optional[str],
) -> bool:

    return normalize_status(
        category,
        value,
    ).value != "UNKNOWN"
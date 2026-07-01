"""
Database Provider Interface

This module defines the contract that every backend provider must implement.

Supported providers:
- MySQL
- PostgreSQL
- REST API
- Mock Provider (Unit Tests)

The validator layer MUST never communicate directly with SQLAlchemy
or raw SQL. All database interactions should go through this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DatabaseProvider(ABC):
    """Abstract interface for customer/order lookups."""

    # ------------------------------------------------------------------
    # Customer Lookups
    # ------------------------------------------------------------------

    @abstractmethod
    def get_customer_by_phone(self, phone: str) -> dict[str, Any] | None:
        """Lookup customer using registered phone number."""

    @abstractmethod
    def get_customer_by_email(self, email: str) -> dict[str, Any] | None:
        """Lookup customer using email."""

    @abstractmethod
    def get_customer(self, customer_id: int) -> dict[str, Any] | None:
        """Lookup customer by primary key."""

    # ------------------------------------------------------------------
    # Order Lookups
    # ------------------------------------------------------------------

    @abstractmethod
    def get_order(self, order_number: str) -> dict[str, Any] | None:
        """Lookup order using order number."""

    @abstractmethod
    def get_orders_by_customer(
        self,
        customer_id: int,
    ) -> list[dict[str, Any]]:
        """Return every order belonging to customer."""

    @abstractmethod
    def get_latest_order(
        self,
        customer_id: int,
    ) -> dict[str, Any] | None:
        """Return latest order."""

    # ------------------------------------------------------------------
    # Shipment Lookups
    # ------------------------------------------------------------------

    @abstractmethod
    def get_tracking(
        self,
        order_number: str,
    ) -> dict[str, Any] | None:
        """Return shipment details."""

    # ------------------------------------------------------------------
    # Generic
    # ------------------------------------------------------------------

    @abstractmethod
    def health_check(self) -> bool:
        """Returns True if provider is healthy."""

    @abstractmethod
    def close(self) -> None:
        """Close underlying connections."""

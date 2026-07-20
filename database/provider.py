from __future__ import annotations

from abc import ABC, abstractmethod

from models.lookup import LookupResult, OrderLookupRequest


class DatabaseProvider(ABC):
    """
    High-level database provider.

    Implementations are responsible for performing the complete lookup:
    - Customer
    - Order
    - Order Items
    """

    @abstractmethod
    def lookup(
        self,
        request: OrderLookupRequest,
    ) -> LookupResult:
        """
        Execute complete lookup from the database.
        """
        raise NotImplementedError
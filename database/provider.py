from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from models.customer import Customer
from models.order import Order


class DatabaseProvider(ABC):
    @abstractmethod
    def find_customer_by_phone(self, phone: str) -> Optional[Customer]:
        raise NotImplementedError

    @abstractmethod
    def find_customer_by_mobile(self, mobile: str) -> Optional[Customer]:
        raise NotImplementedError

    @abstractmethod
    def find_customer_by_email(self, email: str) -> Optional[Customer]:
        raise NotImplementedError

    @abstractmethod
    def find_order_by_order_number(self, order_number: str) -> Optional[Order]:
        raise NotImplementedError

    @abstractmethod
    def find_latest_order_for_customer(self, site_user_id: int) -> Optional[Order]:
        raise NotImplementedError
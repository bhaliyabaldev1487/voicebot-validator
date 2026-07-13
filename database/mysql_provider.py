from __future__ import annotations

from typing import Optional

from database.provider import DatabaseProvider
from database.repository import OrderRepository
from database.session import create_session_factory
from models.customer import Customer
from models.order import Order


class MySQLDatabaseProvider(DatabaseProvider):
    def __init__(self, connection_url: str, echo: bool = False) -> None:
        self.connection_url = connection_url
        self.echo = echo
        self.session_factory = create_session_factory(connection_url, echo=echo)

    def _repo(self) -> OrderRepository:
        session = self.session_factory()
        return OrderRepository(session)

    def find_customer_by_phone(self, phone: str) -> Optional[Customer]:
        session = self.session_factory()
        try:
            repo = OrderRepository(session)
            return repo.find_customer_by_phone(phone)
        finally:
            session.close()

    def find_customer_by_mobile(self, mobile: str) -> Optional[Customer]:
        session = self.session_factory()
        try:
            repo = OrderRepository(session)
            return repo.find_customer_by_mobile(mobile)
        finally:
            session.close()

    def find_customer_by_email(self, email: str) -> Optional[Customer]:
        session = self.session_factory()
        try:
            repo = OrderRepository(session)
            return repo.find_customer_by_email(email)
        finally:
            session.close()

    def find_order_by_order_number(self, order_number: str) -> Optional[Order]:
        session = self.session_factory()
        try:
            repo = OrderRepository(session)
            return repo.find_order_by_order_number(order_number)
        finally:
            session.close()

    def find_latest_order_for_customer(self, site_user_id: int) -> Optional[Order]:
        session = self.session_factory()
        try:
            repo = OrderRepository(session)
            return repo.find_latest_order_for_customer(site_user_id)
        finally:
            session.close()
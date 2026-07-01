from abc import ABC, abstractmethod


class DatabaseAdapter(ABC):

    @abstractmethod
    def get_customer_by_phone(self, phone):
        ...

    @abstractmethod
    def get_orders_by_customer(self, customer_id):
        ...

    @abstractmethod
    def get_order_by_number(self, order_number):
        ...

class MySQLProvider(OrderProvider):

    def __init__(self, session):

        self.session = session

    def customer_by_phone(self, phone):

        ...

    def customer_by_email(self, email):

        ...

    def order_by_number(self, order):

        ...

    def latest_order(self, customer):

        ...

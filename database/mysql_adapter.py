from sqlalchemy import create_engine
from sqlalchemy import text

from config.settings import settings


class MySQLAdapter:

    def __init__(self):

        db = settings.database

        self.engine = create_engine(
            f"mysql+pymysql://"
            f"{db['user']}:{db['password']}"
            f"@{db['host']}:{db['port']}"
            f"/{db['database']}"
        )

    def get_customer_by_phone(self, phone):

        sql = text("""
        SELECT *
        FROM customers
        WHERE phone=:phone
        """)

        with self.engine.connect() as conn:

            return conn.execute(
                sql,
                {"phone": phone}
            ).mappings().first()

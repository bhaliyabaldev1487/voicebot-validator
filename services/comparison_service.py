from models.validation_evidence import ValidationEvidence


class ComparisonService:

    def compare(self, db_order, bot):

        evidence = []

        self._compare(
            evidence,
            "Order Number",
            db_order.customer_order_number,
            bot.order_number,
        )

        self._compare(
            evidence,
            "Order Status",
            db_order.order_status,
            bot.order_status,
        )

        self._compare(
            evidence,
            "Payment Status",
            db_order.payment_status,
            bot.payment_status,
        )

        self._compare(
            evidence,
            "Shipping City",
            db_order.shipping_city,
            bot.shipping_city,
        )

        self._compare(
            evidence,
            "Currency",
            db_order.currency,
            bot.currency,
        )

        self._compare(
            evidence,
            "Total Amount",
            str(db_order.total_price),
            bot.total_amount,
        )

        return evidence

    def _compare(
        self,
        evidence,
        field,
        expected,
        actual,
    ):

        expected = "" if expected is None else str(expected)
        actual = "" if actual is None else str(actual)

        evidence.append(
            ValidationEvidence(
                field_name=field,
                expected=expected,
                actual=actual,
                passed=expected.lower() == actual.lower(),
            )
        )
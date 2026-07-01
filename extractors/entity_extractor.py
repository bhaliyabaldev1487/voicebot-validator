import re


class EntityExtractor:

    ORDER_REGEX = r"\b\d{6,15}\b"

    PHONE_REGEX = r"\b[6-9]\d{9}\b"

    EMAIL_REGEX = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    def order_number(self, text):

        match = re.search(
            self.ORDER_REGEX,
            text
        )

        if match:

            return match.group()

        return None

    def phone(self, text):

        match = re.search(
            self.PHONE_REGEX,
            text
        )

        if match:

            return match.group()

        return None

    def email(self, text):

        match = re.search(
            self.EMAIL_REGEX,
            text
        )

        if match:

            return match.group()

        return None

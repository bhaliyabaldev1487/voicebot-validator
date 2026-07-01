ORDER_KEYWORDS = [

    "order",

    "ordered",

    "purchase",

    "bought",

    "status",

    "my order"

]


class IntentExtractor:

    def detect(self, text):

        text = text.lower()

        for word in ORDER_KEYWORDS:

            if word in text:

                return "ORDER"

        return "UNKNOWN"

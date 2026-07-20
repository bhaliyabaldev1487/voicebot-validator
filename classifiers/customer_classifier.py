import re

CUSTOMER_PATTERNS = {

    r"my order number":30,

    r"my order":15,

    r"where is my order":25,

    r"i placed":15,

    r"i received":10,

    r"i didn't receive":25,

    r"my email":15,

    r"my phone":15,

    r"my mobile":15,

    r"can you check":15,

    r"can you tell":15,

    r"i want":10,

    r"i need":10,

    r"when will":10,

}


class CustomerClassifier:

    def score(self, profile):

        score = 0

        text = profile.full_text

        for pattern, weight in CUSTOMER_PATTERNS.items():

            if re.search(pattern, text):

                score += weight

        return score
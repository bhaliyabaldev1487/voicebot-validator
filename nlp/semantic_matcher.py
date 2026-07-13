from nlp.status_dictionary import STATUS_SYNONYMS
from nlp.payment_dictionary import PAYMENT_SYNONYMS


class SemanticMatcher:

    def status_matches(
        self,
        expected,
        bot_text,
    ):

        if expected is None:
            return False

        expected = expected.upper()

        if expected not in STATUS_SYNONYMS:
            return False

        bot = bot_text.lower()

        for phrase in STATUS_SYNONYMS[expected]:

            if phrase.lower() in bot:

                return True

        return False

    def payment_matches(
        self,
        expected,
        bot_text,
    ):

        if expected is None:
            return False

        expected = expected.upper()

        if expected not in PAYMENT_SYNONYMS:
            return False

        bot = bot_text.lower()

        for phrase in PAYMENT_SYNONYMS[expected]:

            if phrase.lower() in bot:

                return True

        return False
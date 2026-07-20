from nlp.status_dictionary import STATUS_SYNONYMS


class SemanticMatcher:

    def status_matches(
        self,
        expected_status: str,
        bot_text: str,
    ) -> bool:

        if not expected_status:
            return False

        expected_status = expected_status.upper().strip()
        bot_text = bot_text.lower()

        synonyms = STATUS_SYNONYMS.get(expected_status, [])

        for phrase in synonyms:

            if phrase.lower() in bot_text:
                return True

        return False
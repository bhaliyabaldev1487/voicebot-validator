import re


class SpokenTextNormalizer:

    FILLER_WORDS = {
        "uh",
        "umm",
        "hmm",
        "okay",
        "ok",
        "please",
        "actually",
    }

    def normalize(self, text: str) -> str:

        if not text:
            return ""

        text = text.upper()

        text = text.replace("-", " ")

        text = re.sub(r"[.,!?():;]", " ", text)

        text = re.sub(r"\s+", " ", text)

        words = []

        for word in text.split():

            if word.lower() not in self.FILLER_WORDS:

                words.append(word)

        return " ".join(words)
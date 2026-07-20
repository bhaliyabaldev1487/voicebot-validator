import re

BOT_PATTERNS = {

    r"hello":10,

    r"welcome":10,

    r"how can i help":25,

    r"how may i help":25,

    r"english or arabic":40,

    r"please share":20,

    r"please provide":20,

    r"please confirm":20,

    r"would you like":15,

    r"let me check":20,

    r"one moment":15,

    r"thank you for calling":25,

    r"thank you for letting me know":20,

    r"anything else":15,

    r"please stay connected":15,

    r"here is the whatsapp number":30,

}


class BotClassifier:

    def score(self, profile):

        score = 0

        text = profile.full_text

        for pattern, weight in BOT_PATTERNS.items():

            if re.search(pattern, text):

                score += weight

        return score
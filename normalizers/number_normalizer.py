class NumberNormalizer:

    NUMBERS = {

        "ZERO":"0",
        "OH":"0",

        "ONE":"1",
        "TWO":"2",
        "THREE":"3",
        "FOUR":"4",
        "FIVE":"5",
        "SIX":"6",
        "SEVEN":"7",
        "EIGHT":"8",
        "NINE":"9",
    }

    def normalize(self, text: str):

        tokens = text.upper().split()

        result = []

        i = 0

        while i < len(tokens):

            token = tokens[i]

            if token == "DOUBLE":

                if i + 1 < len(tokens):

                    digit = self.NUMBERS.get(tokens[i + 1])

                    if digit:

                        result.append(digit)

                        result.append(digit)

                        i += 2

                        continue

            if token == "TRIPLE":

                if i + 1 < len(tokens):

                    digit = self.NUMBERS.get(tokens[i + 1])

                    if digit:

                        result.extend([digit] * 3)

                        i += 2

                        continue

            result.append(self.NUMBERS.get(token, token))

            i += 1

        return " ".join(result)
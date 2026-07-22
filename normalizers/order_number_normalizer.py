import re

from normalizers.number_normalizer import NumberNormalizer


class OrderNumberNormalizer:

    def __init__(self):

        self.number_normalizer = NumberNormalizer()

    def normalize(self, text: str):

        text = self.number_normalizer.normalize(text)

        text = text.upper()

        text = re.sub(r"[^A-Z0-9 ]", " ", text)

        tokens = text.split()

        output = []

        for token in tokens:

            if len(token) == 1:

                output.append(token)

            elif token.isdigit():

                output.append(token)

            else:

                output.append(token)

        return "".join(output)
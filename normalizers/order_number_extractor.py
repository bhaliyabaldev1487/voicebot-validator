import re

from normalizers.order_number_normalizer import OrderNumberNormalizer
from normalizers.spoken_text_normalizer import SpokenTextNormalizer


class OrderNumberExtractor:

    PATTERN = re.compile(r"[A-Z0-9]{6,20}")

    def __init__(self):

        self.text_normalizer = SpokenTextNormalizer()

        self.order_normalizer = OrderNumberNormalizer()

    def extract(self, text):

        if not text:

            return None

        normalized = self.text_normalizer.normalize(text)

        normalized = self.order_normalizer.normalize(normalized)

        matches = self.PATTERN.findall(normalized)

        if not matches:

            return None

        best = max(matches, key=len)

        return best
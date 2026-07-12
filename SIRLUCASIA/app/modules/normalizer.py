import re
import unicodedata


class Normalizer:

    def normalize(self, text):

        text = text.strip()

        text = re.sub(r"\s+", " ", text)

        text = text.lower()

        text = "".join(
            c
            for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )

        return text
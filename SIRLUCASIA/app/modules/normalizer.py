import re


class Normalizer:

    def normalize(self, text):

        # Eliminar espacios al inicio y final
        text = text.strip()

        # Unificar espacios
        text = re.sub(r"\s+", " ", text)

        # Minúsculas
        text = text.lower()

        # Eliminar signos de apertura y cierre
        text = text.replace("¿", "")
        text = text.replace("?", "")
        text = text.replace("¡", "")
        text = text.replace("!", "")

        # Quitar acentos SOLO de vocales
        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ü": "u"
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text
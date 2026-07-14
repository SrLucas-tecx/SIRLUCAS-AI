import re
import unicodedata


class Normalizer:

    def normalize(self, text):

        # Verificar que sea una cadena
        if not isinstance(text, str):
            return ""

        # Eliminar espacios al inicio y final
        text = text.strip()

        # Convertir a minúsculas
        text = text.lower()

        # Eliminar acentos
        text = "".join(
            c
            for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )

        # Eliminar signos de puntuación más comunes
        text = re.sub(r"[¿?¡!.,;:()\"']", "", text)

        # Reemplazar múltiples espacios por uno solo
        text = re.sub(r"\s+", " ", text)
        
        print(f"[Normalizer] -> {text}")

        return text
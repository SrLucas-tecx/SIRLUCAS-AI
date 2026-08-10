import re
import unicodedata


class Normalizer:

    def __init__(self):

        # ==================================================
        # Palabras de ruido
        # ==================================================

        self.noise_words = [
            "por favor",
            "quisiera",
            "me gustaria",
            "si puedes",
            "podrias"
        ]

        # ==================================================
        # Verbos
        # ==================================================

        self.verb_map = {
            "abre": "abrir",
            "abriras": "abrir",
            "cierra": "cerrar",
            "cerraras": "cerrar",
            "ejecuta": "ejecutar",
        }

        # ==================================================
        # Aplicaciones conocidas
        # ==================================================

        self.app_map = {
            "google chrome": "chrome",
            "navegador": "chrome",
            "ms word": "word",
            "excel": "excel",
            "hojas de calculo": "excel",
        }

    # ==================================================
    # NORMALIZE
    # ==================================================

    def normalize(self, text: str) -> str:

        if not isinstance(text, str):
            return ""

        # Limpiar espacios
        text = text.strip()

        # Minúsculas
        text = text.lower()

        # Eliminar acentos
        text = "".join(
            c
            for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )

        # Eliminar signos de puntuación
        #
        # IMPORTANTE:
        # NO eliminamos "." porque los documentos pueden
        # contener extensiones como demo.txt
        #
        text = re.sub(
            r"[¿?¡!;,:\(\)\"']",
            "",
            text
        )

        # Normalizar espacios
        text = re.sub(r"\s+", " ", text)

        # Eliminar palabras de ruido
        text = self.remove_noise(text)

        # Normalizar verbos
        text = self.normalize_verbs(text)

        # Normalizar aplicaciones únicamente
        # cuando corresponde
        text = self.normalize_apps(text)

        text = text.strip()

        print(f"[Normalizer] -> {text}")

        return text

    # ==================================================
    # REMOVE NOISE
    # ==================================================

    def remove_noise(self, text: str) -> str:

        for word in self.noise_words:
            text = text.replace(word, "")

        # Volver a limpiar espacios
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ==================================================
    # NORMALIZE VERBS
    # ==================================================

    def normalize_verbs(self, text: str) -> str:

        for original, normalized in self.verb_map.items():

            # \b evita reemplazos dentro de otras palabras
            text = re.sub(
                rf"\b{re.escape(original)}\b",
                normalized,
                text
            )

        return text

    # ==================================================
    # NORMALIZE APPS
    # ==================================================

    def normalize_apps(self, text: str) -> str:

        words = text.split()

        if not words:
            return text

        first_word = words[0]

        # Solo normalizamos aplicaciones cuando
        # realmente estamos hablando de abrir/iniciar/ejecutar
        if first_word in {
            "abrir",
            "iniciar",
            "inicia",
            "ejecutar",
        }:

            for original, normalized in self.app_map.items():

                text = re.sub(
                    rf"\b{re.escape(original)}\b",
                    normalized,
                    text
                )

        return text
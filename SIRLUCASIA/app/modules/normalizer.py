import re
import unicodedata

class Normalizer:

    def __init__(self):
        # Palabras de ruido
        self.noise_words = [
            "por favor",
            "quisiera",
            "me gustaria",
            "si puedes",
            "podrias"
        ]

        # Verbos a normalizar
        self.verb_map = {
            "abre": "abrir",
            "abriras": "abrir",
            "cierra": "cerrar",
            "cerraras": "cerrar",
            "ejecuta": "ejecutar",
        }

        # Aplicaciones conocidas
        self.app_map = {
            "google chrome": "chrome",
            "navegador": "chrome",
            "ms word": "word",
            "excel": "excel",
            "hojas de calculo": "excel",
        }

    def normalize(self, text: str) -> str:
        if not isinstance(text, str):
            return ""

        # Limpieza básica
        text = text.strip().lower()
        text = "".join(
            c for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )
        text = re.sub(r"[¿?¡!;,:\(\)\"']", "", text)
        text = re.sub(r"\s+", " ", text)

        # Aplicar normalizaciones
        text = self.remove_noise(text)
        text = self.normalize_verbs(text)
        text = self.normalize_apps(text)

        print(f"[Normalizer] -> {text}")
        return text

    def remove_noise(self, text: str) -> str:
        for word in self.noise_words:
            text = text.replace(word, "")
        return text.strip()

    def normalize_verbs(self, text: str) -> str:
        for k, v in self.verb_map.items():
            text = text.replace(k, v)
        return text

    def normalize_apps(self, text: str) -> str:
        """
        Contextualiza la normalización de aplicaciones:
        - Si la frase empieza con 'abrir', 'iniciar', 'ejecutar' → aplica app_map.
        - Si la frase empieza con 'lista', 'muestra', 'lee', 'crea' → NO aplica app_map.
        """
        # Detectar intención por el primer verbo
        first_word = text.split(" ")[0]

        if first_word in ["abrir", "inicia", "ejecutar"]:
            for k, v in self.app_map.items():
                text = text.replace(k, v)

        return text

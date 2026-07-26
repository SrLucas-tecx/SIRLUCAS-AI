import re
import unicodedata

class Normalizer:

    def __init__(self):
        # Diccionarios de normalización
        self.noise_words = ["por favor", "quisiera", "me gustaria", "si puedes", "podrias"]
        self.verb_map = {
            "abre": "abrir",
            "abriras": "abrir",
            "cierra": "cerrar",
            "cerraras": "cerrar",
            "ejecuta": "ejecutar",
        }
        self.app_map = {
            "google chrome": "chrome",
            "navegador": "chrome",
            "ms word": "word",
            "documentos": "word",
            "excel": "excel",
            "hojas de calculo": "excel",
        }

    def normalize(self, text: str) -> str:
        # Verificar que sea una cadena
        if not isinstance(text, str):
            return ""

        # Eliminar espacios al inicio y final
        text = text.strip()

        # Convertir a minúsculas
        text = text.lower()

        # Eliminar acentos
        text = "".join(
            c for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )

        # Eliminar signos de puntuación más comunes
        text = re.sub(r"[¿?¡!.,;:()\"']", "", text)

        # Reemplazar múltiples espacios por uno solo
        text = re.sub(r"\s+", " ", text)

        # Aplicar normalizaciones adicionales
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
        for k, v in self.app_map.items():
            text = text.replace(k, v)
        return text

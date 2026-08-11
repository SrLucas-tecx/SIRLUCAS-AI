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
            "podrias",
        ]

        # ==================================================
        # Verbos
        # ==================================================
        self.verb_map = {
            "abre": "abrir",
            "abriras": "abrir",
            "abrirlo": "abrir",
            "cierra": "cerrar",
            "cierralo": "cerrar",
            "ciérralo": "cerrar",
            "cerraras": "cerrar",
            "reinicia": "reiniciar",
            "reinicialo": "reiniciar",
            "reinícialo": "reiniciar",
            "ejecuta": "ejecutar",
        }

        # ==================================================
        # Aplicaciones conocidas
        # ==================================================
        self.app_map = {
            "google chrome": "chrome",
            "navegador": "chrome",
            "ms word": "word",
            "word": "word",
            "excel": "excel",
            "hojas de calculo": "excel",
            "powerpoint": "powerpoint",
            "calculadora": "calculadora",
            "opera gx": "opera gx",
            "firefox": "firefox",
            "edge": "edge",
        }
        
        self.verb_map.update({
        "reinicialo": "reiniciar",
        "reinícialo": "reiniciar",
        "esta abierto": "esta abierto"
        })


        # ==================================================
        # Formas de invocar a SIRLUCAS
        # ==================================================
        self.invocation_patterns = [
            r"^hola oye lucas\b",
            r"^oye lucas\b",
            r"^hola lucas\b",
            r"^hey lucas\b",
            r"^lucas\b",
        ]

    # ==================================================
    # NORMALIZE
    # ==================================================
    def normalize(self, text: str) -> str:

        if not isinstance(text, str):
            return ""

        # Limpieza básica
        text = text.strip().lower()

        # Eliminar acentos
        text = "".join(
            c for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )

        # Eliminar signos de puntuación (excepto ".")
        text = re.sub(r"[¿?¡!;,:\(\)\"']", "", text)

        # Normalizar espacios
        text = re.sub(r"\s+", " ", text).strip()

        # Eliminar invocación a Lucas
        text = self.remove_invocation(text)

        # Si era únicamente un saludo/invocación, conservarlo
        if self.is_invocation_only(text):
            print(f"[Normalizer] -> {text}")
            return text

        # Eliminar palabras de ruido
        text = self.remove_noise(text)

        # Normalizar verbos
        text = self.normalize_verbs(text)

        # Normalizar aplicaciones
        text = self.normalize_apps(text)

        # Limpieza final
        text = re.sub(r"\s+", " ", text).strip()

        print(f"[Normalizer] -> {text}")
        return text

    # ==================================================
    # REMOVE INVOCATION
    # ==================================================
    def remove_invocation(self, text: str) -> str:
        if not text:
            return text

        for pattern in self.invocation_patterns:
            match = re.match(pattern, text)
            if not match:
                continue

            remaining = text[match.end():].strip()
            if not remaining:
                return text
            return remaining

        return text

    # ==================================================
    # IS INVOCATION ONLY
    # ==================================================
    def is_invocation_only(self, text: str) -> bool:
        if not text:
            return False

        for pattern in self.invocation_patterns:
            if re.fullmatch(pattern, text):
                return True
        return False

    # ==================================================
    # REMOVE NOISE
    # ==================================================
    def remove_noise(self, text: str) -> str:
        for word in self.noise_words:
            text = re.sub(rf"\b{re.escape(word)}\b", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ==================================================
    # NORMALIZE VERBS
    # ==================================================
    def normalize_verbs(self, text: str) -> str:
        for original, normalized in self.verb_map.items():
            text = re.sub(rf"\b{re.escape(original)}\b", normalized, text)
        return text

    # ==================================================
    # NORMALIZE APPS
    # ==================================================
    def normalize_apps(self, text: str) -> str:
        words = text.split()
        if not words:
            return text

        first_word = words[0]
        if first_word in {"abrir", "iniciar", "inicia", "ejecutar", "cerrar", "reiniciar"}:
            for original, normalized in self.app_map.items():
                text = re.sub(rf"\b{re.escape(original)}\b", normalized, text)
        return text


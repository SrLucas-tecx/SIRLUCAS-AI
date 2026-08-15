# app/IA/response_wrapper.py

from app.core.response_formatter import ResponseFormatter
from app.IA.response_generator import ResponseGenerator

class ResponseWrapper:
    """
    Unifica las respuestas deterministas y generativas.
    Aplica personalidad y estilo de SIRLUCAS AI.
    """

    def __init__(self):
        self.formatter = ResponseFormatter()
        self.generator = ResponseGenerator()

    def wrap(self, response, source="deterministic"):
        """
        Recibe la respuesta y la formatea según su origen.
        """
        if source == "ollama":
            text = self.generator.format(response)
        else:
            text = self.formatter.format(response)

        # Personalidad: añadir un toque característico
        return self._apply_personality(text)

    def _apply_personality(self, text):
        """
        Aplica estilo y personalidad de SIRLUCAS AI.
        """
        if not text:
            return "No tengo nada que decir por ahora 🙂"

        # Ejemplo: añadir un prefijo amigable
        return f"🤖 SIRLUCAS: {text}"

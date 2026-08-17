from app.core.response_formatter import ResponseFormatter
from app.IA.response_generator import ResponseGenerator


class ResponseWrapper:

    def __init__(self):

        self.formatter = ResponseFormatter()
        self.generator = ResponseGenerator()

    def wrap(
        self,
        response,
        source="deterministic"
    ):

        if source == "ollama":

            text = self.generator.format(
                response
            )

        else:

            text = self.formatter.format(
                response
            )

        return self._apply_personality(
            text
        )

    def _apply_personality(self, text):

        if not text:

            return (
                "No tengo una respuesta "
                "disponible en este momento."
            )

        return str(text).strip()
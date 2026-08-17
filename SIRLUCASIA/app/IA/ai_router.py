from app.IA.ollama_client import OllamaClient
from app.IA.prompt_manager import PromptManager
from app.IA.response_generator import ResponseGenerator


class AIRouter:
    """
    Controla cuándo y cómo SIRLUCAS AI utiliza Ollama.

    Ollama NO ejecuta acciones del sistema.
    Solo genera respuestas de lenguaje natural.
    """

    def __init__(self, ollama_client=None, enabled=True):

        self.ollama = ollama_client or OllamaClient()
        self.enabled = enabled

        self.prompt_manager = PromptManager()
        self.response_generator = ResponseGenerator()

    # ==================================================
    # DISPONIBILIDAD
    # ==================================================

    def is_available(self):
        return self.ollama.is_available()

    # ==================================================
    # RESPUESTA PRINCIPAL
    # ==================================================

    def generate_response(self, message, context=None):

        if not self.enabled:
            return self._disabled_response()

        if not self.is_available():
            return self._unavailable_response()

        try:
            # Construir contexto
            context_text = self._format_context(context or {})

            # Construir prompt
            prompt = self.prompt_manager.build(message, context_text)

            # Consultar Ollama
            response = self.ollama.generate(prompt)

            # Formatear respuesta
            formatted = self.response_generator.format(response)

            return {
                "success": True,
                "source": "ollama",
                "response": formatted,
            }

        except Exception as e:
            return {
                "success": False,
                "source": "ollama",
                "response": "Ocurrió un error al consultar la IA.",
                "error": str(e),
            }

    # ==================================================
    # FORMATEAR CONTEXTO
    # ==================================================

    def _format_context(self, context):

        if not context:
            return "No hay contexto disponible."

        lines = []

        for key, value in context.items():
            if value is None:
                continue

            # Historial
            if key == "history":
                if not value:
                    continue

                lines.append("Historial reciente:")

                for turn in value[-10:]:
                    usuario = turn.get("usuario", "")
                    respuesta = turn.get("respuesta", "")

                    if usuario:
                        lines.append(f"Usuario: {usuario}")
                    if respuesta:
                        lines.append(f"SIRLUCAS: {respuesta}")

                continue

            lines.append(f"{key}: {value}")

        if not lines:
            return "No hay contexto relevante."

        return "\n".join(lines)

    # ==================================================
    # OLLAMA DESACTIVADO
    # ==================================================

    def _disabled_response(self):
        return {
            "success": False,
            "source": "disabled",
            "response": "La inteligencia artificial generativa está desactivada.",
        }

    # ==================================================
    # OLLAMA NO DISPONIBLE
    # ==================================================

    def _unavailable_response(self):
        return {
            "success": False,
            "source": "ollama",
            "response": "Ollama no está disponible en este momento.",
        }

    # ==================================================
    # MÉTODO PRINCIPAL
    # ==================================================

    def handle(self, message, context=None):
        """
        Punto de entrada para Assistant.
        Decide si usar Ollama y devuelve la respuesta.
        """
        if not self.enabled:
            return self._disabled_response()

        return self.generate_response(message=message, context=context)

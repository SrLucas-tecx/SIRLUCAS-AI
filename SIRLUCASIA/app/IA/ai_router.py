from app.IA.ollama_client import OllamaClient
from app.IA.prompt_manager import PromptManager
from app.IA.response_generator import ResponseGenerator

class AIRouter:
    def __init__(self, ollama_client=None, enabled=True):
        self.ollama = ollama_client or OllamaClient()
        self.enabled = enabled
        self.prompt_manager = PromptManager()       # ✅ nuevo
        self.response_generator = ResponseGenerator()  # ✅ nuevo

    def generate_response(self, message, context=None):
        if not self.enabled:
            return self._disabled_response()
        if not self.is_available():
            return self._unavailable_response()

        try:
            # Construir prompt con PromptManager
            context_text = self._format_context(context or {})
            prompt = self.prompt_manager.build(message, context_text)

            # Enviar a Ollama
            response = self.ollama.generate(prompt)

            # Formatear salida con ResponseGenerator
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

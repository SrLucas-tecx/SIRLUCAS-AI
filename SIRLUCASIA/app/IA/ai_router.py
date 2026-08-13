# app/IA/ai_router.py

import logging

from app.IA.ollama_client import OllamaClient


class AIRouter:
    """
    Decide cuándo SIRLUCAS AI debe utilizar Ollama.

    IMPORTANTE:
    AIRouter NO ejecuta acciones del sistema.
    NO abre programas.
    NO modifica documentos.
    NO gestiona memoria permanente.

    Su función es determinar cuándo utilizar IA generativa
    y devolver una respuesta estructurada.
    """

    def __init__(
        self,
        ollama_client=None,
        enabled=True,
    ):
        self.logger = logging.getLogger(__name__)

        self.ollama = ollama_client or OllamaClient()

        self.enabled = enabled

    # ==================================================
    # DISPONIBILIDAD
    # ==================================================

    def is_available(self):
        """
        Comprueba si el uso de Ollama está disponible.
        """

        if not self.enabled:
            return False

        return self.ollama.is_available()

    # ==================================================
    # DECISIÓN
    # ==================================================

    def should_use_ai(self, parser_result):
        """
        Decide si el resultado del Parser necesita Ollama.

        Ollama se utiliza principalmente cuando:
        - no existe una regla determinista;
        - la regla pertenece a conversación;
        - la intención necesita interpretación lingüística.

        NO se envían a Ollama las acciones deterministas
        del sistema.
        """

        if not self.enabled:
            return False

        if parser_result is None:
            return True

        command = parser_result.get("command")
        module = parser_result.get("module")
        rule = parser_result.get("rule")

        # ----------------------------------------------
        # Regla desconocida
        # ----------------------------------------------

        if rule == "unknown":
            return True

        if command == "unknown":
            return True

        # ----------------------------------------------
        # Conversación
        # ----------------------------------------------

        if module == "conversation":
            return True

        # ----------------------------------------------
        # Todo lo demás permanece determinista
        # ----------------------------------------------

        return False

    # ==================================================
    # GENERAR RESPUESTA
    # ==================================================

    def generate_response(
        self,
        message,
        context=None,
    ):
        """
        Envía una consulta conversacional a Ollama.
        """

        if not self.enabled:
            return self._disabled_response()

        if not self.is_available():
            return self._unavailable_response()

        try:

            prompt = self.build_prompt(
                message=message,
                context=context,
            )

            response = self.ollama.generate(prompt)

            if not response:
                return {
                    "success": False,
                    "source": "ollama",
                    "response": "No recibí una respuesta de Ollama.",
                }

            return {
                "success": True,
                "source": "ollama",
                "response": response,
            }

        except Exception as e:

            self.logger.exception(
                "Error generando respuesta con Ollama"
            )

            return {
                "success": False,
                "source": "ollama",
                "response": "Ocurrió un error al consultar la IA.",
                "error": str(e),
            }

    # ==================================================
    # PROMPT
    # ==================================================

    def build_prompt(
        self,
        message,
        context=None,
    ):
        """
        Construye el prompt que recibe Ollama.

        El contexto es opcional.
        """

        context = context or {}

        system_instruction = """
Eres SIRLUCAS AI, un asistente personal inteligente.

Responde en español.

Sé claro, útil y natural.

No inventes acciones que el sistema no haya ejecutado.

No afirmes haber abierto, cerrado, creado, eliminado
o modificado algo si el sistema no lo confirmó.

Si no conoces una información, dilo claramente.

El sistema determinista de SIRLUCAS AI es responsable
de ejecutar acciones sobre el sistema operativo,
archivos, documentos y memoria.
"""

        context_text = self._format_context(context)

        prompt = f"""
{system_instruction}

CONTEXTO ACTUAL:
{context_text}

MENSAJE DEL USUARIO:
{message}

RESPUESTA:
"""

        return prompt.strip()

    # ==================================================
    # CONTEXTO
    # ==================================================

    def _format_context(self, context):
        """
        Convierte el contexto recibido en texto legible
        para Ollama.
        """

        if not context:
            return "No hay contexto adicional."

        lines = []

        fields = {
            "topic": "Tema",
            "program": "Programa activo",
            "document": "Documento activo",
            "search": "Búsqueda activa",
            "person": "Persona activa",
            "file": "Archivo activo",
            "folder": "Carpeta activa",
            "url": "URL activa",
            "task": "Tarea actual",
            "conversation_mode": "Modo de conversación",
        }

        for key, label in fields.items():

            value = context.get(key)

            if value is not None:
                lines.append(
                    f"- {label}: {value}"
                )

        history = context.get("history")

        if history:
            lines.append("")
            lines.append("Historial reciente:")

            for item in history[-5:]:

                user = item.get("usuario")
                assistant = item.get("respuesta")

                if user:
                    lines.append(
                        f"  Usuario: {user}"
                    )

                if assistant:
                    lines.append(
                        f"  SIRLUCAS: {assistant}"
                    )

        if not lines:
            return "No hay contexto adicional."

        return "\n".join(lines)

    # ==================================================
    # RESPUESTAS DE ESTADO
    # ==================================================

    def _disabled_response(self):
        return {
            "success": False,
            "source": "ai_router",
            "response": None,
            "error": "IA desactivada.",
        }

    def _unavailable_response(self):
        return {
            "success": False,
            "source": "ai_router",
            "response": None,
            "error": "Ollama no está disponible.",
        }
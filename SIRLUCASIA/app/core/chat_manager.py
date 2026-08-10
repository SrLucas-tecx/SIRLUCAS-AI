"""
ChatManager
===========

Manager del módulo "conversation": punto de entrada de la charla libre.

Hoy no hay un motor generativo conectado, así que responde siempre con un
placeholder. Cuando se integre un motor (p. ej. Ollama), solo hay que
reemplazar el cuerpo de `chat()`: el Router, el Parser y el IntentResolver
ya enrutan `module="conversation"` hasta acá.
"""

import logging

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus

logger = logging.getLogger(__name__)

PLACEHOLDER_MESSAGE = "Aún no tengo respuesta generativa configurada."


class ChatManager:
    """Responde a los mensajes de charla libre enrutados como `conversation`."""

    def execute(self, data: dict) -> ActionResult:
        topic = data.get("topic") if isinstance(data, dict) else None

        logger.info("[ChatManager] Mensaje de conversación recibido: %s", topic)

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="conversation",
            command="chat",
            message=PLACEHOLDER_MESSAGE,
            data={"topic": topic},
        )

import logging

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
from app.core.context_manager import ContextManager

logger = logging.getLogger(__name__)

# Instancia global de ContextManager
context = ContextManager()

GENERIC_PRONOUNS = ("lo", "la", "los", "las", "eso", "esto", "esa", "ese", "esos", "esas")


class Router:

    def __init__(self):
        self.modules = {}

    def register(self, name, module):
        self.modules[name.lower()] = module
        logger.info("[Router] Módulo registrado -> %s", name.lower())

    def route(self, data):

        if not isinstance(data, dict):
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="router",
                command=None,
                message="Datos inválidos: se esperaba un diccionario.",
            )

        module_name = (data.get("module") or "").lower()
        command = data.get("command")

        if not module_name:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="router",
                command=command,
                message="No se especificó el módulo.",
            )

        manager = self.modules.get(module_name)

        if manager is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="router",
                command=command,
                message=f"No existe el módulo '{module_name}'.",
            )

        # --- Integración con ContextManager ---
        try:
            context.update(data)
        except Exception as e:
            logger.exception("[Router] Error actualizando contexto")
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="context",
                command="update",
                message="Error actualizando contexto.",
                error=str(e),
            )

        # --- Resolver referencias si el topic es pronombre ---
        topic = data.get("topic")
        if topic and topic.lower() in GENERIC_PRONOUNS:
            ref = context.resolve_reference(topic)
            if ref and ref.get("value"):
                data["topic"] = ref["value"]
                data["entity"] = ref

        # --- Resolver referencias específicas de documentos ---
        if command in ("read", "rename", "delete") and topic and topic.lower() in GENERIC_PRONOUNS:
            ref = context.resolve_reference(topic)
            if ref and ref.get("type") == "document":
                data["topic"] = ref["value"]
                data["entity"] = ref

        # --- Resolver referencias específicas de programas ---
        if command in ("close", "restart", "open") and topic and topic.lower() in GENERIC_PRONOUNS:
            ref = context.resolve_reference(topic)
            if ref and ref.get("type") == "program":
                data["topic"] = ref["value"]
                data["entity"] = ref

        # --- Manejo de comandos desconocidos ---
        if command == "unknown":
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module=module_name,
                command=command,
                message="Comando desconocido."
            )

        # --- Ejecución del manager ---
        try:
            response = manager.execute(data)

        except Exception as e:
            logger.exception(
                "[Router] Error ejecutando %s.%s", module_name, command
            )

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module=module_name,
                command=command,
                message=f"Error ejecutando la acción '{command}'.",
                error=str(e),
            )

        return response

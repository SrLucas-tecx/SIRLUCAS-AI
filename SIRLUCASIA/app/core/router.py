import logging

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus

logger = logging.getLogger(__name__)


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

        # La persistencia en memoria ocurre únicamente cuando el intent
        # es de memoria y el Router despacha al MemoryManager, nunca como
        # efecto secundario de cualquier otra ruta.
        return response
import logging

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus

logger = logging.getLogger(__name__)


class TaskExecutor:

    def __init__(self, router, event_bus):
        self.router = router
        self.event_bus = event_bus

    def execute(self, actions):
        results = []

        if not actions:
            return results

        for action in actions:

            logger.debug("[TaskExecutor] Acción: %s", action.to_dict())

            try:
                # Ejecutar la acción mediante el Router
                result = self.router.route(action.to_dict())

                # Marcar estado de la acción
                if result.success:
                    action.complete()
                else:
                    action.fail()

            except Exception as e:
                logger.exception("[TaskExecutor] Error ejecutando acción.")

                action.fail()

                # Si el router falla completamente no hay ActionResult:
                # se construye uno de error para no propagar None a los
                # listeners.
                result = self._error_result(action, e)

            if result is None:
                result = self._error_result(action)

            # Publicar evento
            try:
                self.event_bus.publish(
                    "action.executed",
                    result
                )
            except Exception:
                logger.exception("[TaskExecutor] Error al publicar evento.")

            results.append(result)

        return results

    def _error_result(self, action, error=None):
        data = action.to_dict() if hasattr(action, "to_dict") else {}

        return ActionResult(
            success=False,
            status=ActionStatus.ERROR,
            module=data.get("module"),
            command=data.get("command"),
            message="No se pudo ejecutar la acción.",
            error=str(error) if error is not None else None,
        )

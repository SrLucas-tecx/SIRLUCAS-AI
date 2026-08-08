# ==================================================
# TaskPipeline
# Encadena las fases de resolución, planificación,
# optimización y ejecución de tareas
# ==================================================

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus


class TaskPipeline:

    def __init__(
        self,
        entity_resolver,
        reference_resolver,
        context_resolver,
        context_manager,
        intent_resolver,
        planner,
        optimizer,
        executor
    ):
        self.entity = entity_resolver
        self.reference = reference_resolver
        self.context_resolver = context_resolver
        self.context = context_manager
        self.intent = intent_resolver
        self.planner = planner
        self.optimizer = optimizer
        self.executor = executor

    def execute(self, message):

        if not isinstance(message, dict):
            return self._error("Entrada inválida.")

        raw_message = message.get("raw_message") or message.get("normalized")

        # Resolver entidad
        message = self.entity.resolve(message)
        if not isinstance(message, dict):
            return self._error("El resolvedor de entidades devolvió un valor inválido.")

        # Resolver referencias
        message = self.reference.resolve(message)
        if not isinstance(message, dict):
            return self._error("El resolvedor de referencias devolvió un valor inválido.")

        # Resolver contexto
        message = self.context_resolver.resolve(message, self.context)
        if not isinstance(message, dict):
            return self._error("El resolvedor de contexto devolvió un valor inválido.")

        # Resolver intención
        message = self.intent.resolve(message)
        if not isinstance(message, dict):
            return self._error("El resolvedor de intención devolvió un valor inválido.")

        # ==============================
        # Si no entendió la intención
        # ==============================
        if message.get("intent") == "UNKNOWN":

            return [
                ActionResult(
                    success=False,
                    status=ActionStatus.WARNING,
                    module="assistant",
                    command=None,
                    message="No entendí lo que quisiste decir."
                )
            ]

        # Actualizar contexto
        message.setdefault("user_message", raw_message)
        self.context.update(message)

        # Planificar acciones
        actions = self.planner.plan(message)

        # Optimizar acciones
        actions = self.optimizer.optimize(actions, self.context)

        # Ejecutar acciones
        results = self.executor.execute(actions)

        # Registrar la respuesta del asistente en el contexto
        answer = next(
            (r.message for r in results if isinstance(r, ActionResult) and r.message),
            None
        )
        self.context.set_answer(answer)

        return results

    def _error(self, text):
        return [
            ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="assistant",
                command=None,
                message=text
            )
        ]
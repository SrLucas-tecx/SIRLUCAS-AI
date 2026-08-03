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
            return [
                ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="assistant",
                    command=None,
                    message="Entrada inválida."
                )
            ]

        # Resolver entidad
        message = self.entity.resolve(message)

        # Resolver referencias
        message = self.reference.resolve(message)

        # Resolver contexto
        message = self.context_resolver.resolve(message, self.context)

        # Resolver intención
        message = self.intent.resolve(message)

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
        self.context.update(message)

        # Planificar acciones
        actions = self.planner.plan(message)

        # Optimizar acciones
        actions = self.optimizer.optimize(actions, self.context)

        # Ejecutar acciones
        return self.executor.execute(actions)
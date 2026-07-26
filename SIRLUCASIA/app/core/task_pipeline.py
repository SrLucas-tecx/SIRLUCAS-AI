# ==================================================
# TaskPipeline
# Encadena las fases de resolución, planificación,
# optimización y ejecución de tareas
# ==================================================

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
        # Validar que realmente venga un diccionario
        if not isinstance(message, dict):
            return []

        # Resolver entidad
        message = self.entity.resolve(message)

        # Resolver referencias
        message = self.reference.resolve(message)

        # Resolver contexto
        message = self.context_resolver.resolve(message, self.context)

        # Resolver intención
        message = self.intent.resolve(message)

        # Actualizar contexto
        self.context.update(message)

        # Planificar acciones
        actions = self.planner.plan(message)

        # Optimizar acciones con contexto
        actions = self.optimizer.optimize(actions, self.context)

        # Ejecutar acciones
        return self.executor.execute(actions)

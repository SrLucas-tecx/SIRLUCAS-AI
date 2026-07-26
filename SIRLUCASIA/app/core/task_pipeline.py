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

        message = self.entity.resolve(message)

        message = self.reference.resolve(message)

        message = self.context_resolver.resolve(

        message,

        self.context

    )

        message = self.intent.resolve(message)

        self.context.update(message)

        actions = self.planner.plan(message)

        actions = self.optimizer.optimize(actions)

        return self.executor.execute(actions)
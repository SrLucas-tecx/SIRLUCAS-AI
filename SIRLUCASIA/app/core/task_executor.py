class TaskExecutor:
    def __init__(self, router, event_bus):
        self.router = router
        self.event_bus = event_bus

    def execute(self, actions):
        results = []
        for action in actions:
            result = self.router.route(action.to_dict())

            # Publicar evento para todos los listeners
            try:
                self.event_bus.publish("action.executed", result)
            except Exception as e:
                print(f"[TaskExecutor] Error al publicar evento: {e}")

            results.append(result)

        return results

class TaskExecutor:

    def __init__(self, router, event_bus):
        self.router = router
        self.event_bus = event_bus

    def execute(self, actions):
        results = []

        if not actions:
            return results

        for action in actions:

            print("\n=== ACTION ===")
            print(action.to_dict())

            try:
                # Ejecutar la acción mediante el Router
                result = self.router.route(action.to_dict())

                # Marcar estado de la acción
                if result.success:
                    action.complete()
                else:
                    action.fail()

            except Exception as e:
                print(f"[TaskExecutor] Error ejecutando acción: {e}")

                action.fail()

                # Si el router falla completamente,
                # no tenemos un ActionResult válido.
                result = None

            # Publicar evento
            try:
                self.event_bus.publish(
                    "action.executed",
                    result
                )
            except Exception as e:
                print(
                    f"[TaskExecutor] Error al publicar evento: {e}"
                )

            results.append(result)

        return results
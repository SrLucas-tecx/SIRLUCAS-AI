from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
from app.database.web_database import WebDatabase

class WebManager:

    def __init__(self):
        self.database = WebDatabase()
        print("=" * 50)
        print("[WebManager]")
        print("Inicializado correctamente.")
        print("=" * 50)

    def execute(self, data):
        command = data.get("command")
        method = getattr(self, command, None)
        if method is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="web",
                command=command,
                message=f"No existe la acción '{command}'.",
                error=f"Acción '{command}' no implementada en WebManager."
            )
        return method(data)

    def search(self, data):
        topic = data.get("topic")
        if not topic:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="web",
                command="search",
                message="No especificaste qué buscar.",
                error="Campo 'topic' vacío."
            )

        result = self.database.find(topic)
        if result is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="web",
                command="search",
                message=f"No encontré '{topic}'.",
                error=f"No se encontró búsqueda registrada para '{topic}'."
            )

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="web",
            command="search",
            message=f"Búsqueda web simulada: {result}",
            data={"topic": topic, "result": result}
        )

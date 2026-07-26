from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
from app.database.conversation_database import ConversationDatabase

class ConversationManager:

    def __init__(self):
        self.database = ConversationDatabase()
        print("=" * 50)
        print("[ConversationManager]")
        print("Inicializado correctamente.")
        print("=" * 50)

    def execute(self, data):
        command = data.get("command")
        method = getattr(self, command, None)
        if method is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="conversation",
                command=command,
                message=f"No existe la acción '{command}'."
            )
        return method(data)

    def talk(self, data):
        topic = data.get("topic")
        if topic is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="conversation",
                command="talk",
                message="No especificaste un tema."
            )

        response = self.database.find(topic)
        if response is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="conversation",
                command="talk",
                message="No tengo una respuesta para eso."
            )

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="conversation",
            command="talk",
            message=response
        )

    def history(self, data):
        history = self.database.last(10)
        if not history:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="conversation",
                command="history",
                message="No hay historial."
            )

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="conversation",
            command="history",
            data=history,
            message="\n".join(history)
        )

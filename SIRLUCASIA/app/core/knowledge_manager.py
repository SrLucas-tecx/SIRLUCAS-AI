from app.database.knowledge_database import KnowledgeDatabase
from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus


class KnowledgeManager:

    def __init__(self):

        self.database = KnowledgeDatabase()

        print("=" * 50)
        print("[KnowledgeManager]")
        print(f"{len(self.database.list())} conocimientos cargados.")
        print("=" * 50)

    # ==========================================
    # Router
    # ==========================================

    def execute(self, data):

        command = data.get("command")

        method = getattr(self, command, None)

        if method is None:

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="knowledge",
                command=command,
                message=f"No existe la acción '{command}'."
            )

        return method(data)

    # ==========================================
    # Buscar conocimiento
    # ==========================================

    def search(self, data):

        topic = (
            data.get("topic")
            or data.get("value")
        )

        if topic is None:

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="knowledge",
                command="search",
                message="No especificaste qué buscar."
            )

        answer = self.database.find(topic)

        if answer is None:

            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="knowledge",
                command="search",
                message="No conozco ese tema todavía."
            )

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="knowledge",
            command="search",
            message=answer,
            data={
                "topic": topic,
                "answer": answer
            }
        )
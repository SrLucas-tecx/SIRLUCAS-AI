from app.memory.memory_database import MemoryDatabase
from app.memory.memory_resolver import MemoryResolver
from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus

# ==================================================
# MemoryManager
# ==================================================

class MemoryManager:

    def __init__(self):
        self.database = MemoryDatabase()
        self.resolver = MemoryResolver(self.database)

        print("=" * 50)
        print("[MemoryManager]")
        print("Inicializado correctamente.")
        print("=" * 50)

    # ==================================================
    # Router
    # ==================================================
    def execute(self, data):
        command = data.get("command")
        method = getattr(self, command, None)

        if method is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command=command,
                message=f"No existe la acción '{command}'."
            )

        return method(data)

    # ==================================================
    # Guardar contexto
    # ==================================================
    def remember(self, data):
        self.resolver.remember(data)
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="remember",
            message="Información almacenada."
        )

    # ==================================================
    # Resolver contexto
    # ==================================================
    def resolve(self, data):
        result = self.resolver.resolve(data)
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="resolve",
            message="Memoria recuperada.",
            data=result
        )

    # ==================================================
    # Último tema
    # ==================================================
    def last_topic(self):
        return self.resolver.last_topic()

    # ==================================================
    # Último comando
    # ==================================================
    def last_command(self):
        return self.resolver.last_command()

    # ==================================================
    # Último módulo
    # ==================================================
    def last_module(self):
        return self.resolver.last_module()

    # ==================================================
    # Último contexto
    # ==================================================
    def last(self):
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="last",
            data=self.resolver.last()
        )

    # ==================================================
    # Toda la memoria
    # ==================================================
    def context(self):
        return self.database.all()

    # ==================================================
    # Limpiar memoria
    # ==================================================
    def clear(self):
        self.database.clear()
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="clear",
            message="Memoria limpiada."
        )

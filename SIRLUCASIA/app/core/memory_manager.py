from app.utils.json_manager import JSONManager
from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus

# ==================================================
# MemoryManager
# Encargado de administrar la memoria del asistente
# ==================================================

class MemoryManager:

    def __init__(self):
        self.memory = JSONManager.load("data/memory.json")
        if self.memory is None:
            self.memory = {}

    # ==================================================
    # Dispatcher
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
                message=f"No existe el comando '{command}'."
            )

        return method(data)

    # ==================================================
    # Guardar información
    # ==================================================
    def remember(self, data):
        print("\n=== MEMORY RECIBE ===")
        key = data.get("key")
        value = data.get("value")

        if not key:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="remember",
                message="No especificaste la clave."
            )

        if value is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="remember",
                message="No especificaste el valor."
            )

        self.memory[key] = value
        JSONManager.save("data/memory.json", self.memory)

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="remember",
            message=f"Recordaré que tu {key} es {value}.",
            data={"key": key, "value": value}
        )

    # ==================================================
    # Recuperar información
    # ==================================================
    def recall(self, data):
        key = data.get("key")

        if not key:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="recall",
                message="No especificaste qué recordar."
            )

        value = self.memory.get(key)

        if value is None:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="memory",
                command="recall",
                message=f"No recuerdo tu {key}."
            )

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="recall",
            message=value,
            data={"key": key, "value": value}
        )

    # ==================================================
    # Eliminar información
    # ==================================================
    def forget(self, data):
        key = data.get("key")

        if not key:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="forget",
                message="No especificaste qué olvidar."
            )

        if key not in self.memory:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="forget",
                message=f"No existe '{key}' en memoria."
            )

        del self.memory[key]
        JSONManager.save("data/memory.json", self.memory)

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="forget",
            message=f"He olvidado tu {key}.",
            data={"key": key}
        )

    # ==================================================
    # Listar memoria
    # ==================================================
    def list_memories(self, data=None):
        if not self.memory:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="memory",
                command="list_memories",
                message="La memoria está vacía."
            )

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="list_memories",
            message="Memorias obtenidas.",
            data=self.memory
        )

    # ==================================================
    # Limpiar memoria
    # ==================================================
    def clear(self, data=None):
        self.memory.clear()
        JSONManager.save("data/memory.json", self.memory)

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="clear",
            message="Memoria limpiada correctamente."
        )

    # ==================================================
    # Comprobar existencia
    # ==================================================
    def exists(self, data):
        key = data.get("key")
        if not key:
            return False
        return key in self.memory

    # ==================================================
    # Obtener todas las claves
    # ==================================================
    def keys(self, data=None):
        return list(self.memory.keys())

    # ==================================================
    # Obtener todos los valores
    # ==================================================
    def values(self, data=None):
        return list(self.memory.values())

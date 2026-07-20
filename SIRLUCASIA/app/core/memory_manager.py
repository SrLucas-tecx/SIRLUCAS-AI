from app.utils.json_manager import JSONManager


# ==================================================
# MemoryManager
# Encargado de administrar la memoria del asistente
# ==================================================

class MemoryManager:

    def __init__(self):

        self.memory = JSONManager.load(
            "data/memory.json"
        )

        if self.memory is None:
            self.memory = {}

    # ==================================================
    # Dispatcher
    # ==================================================

    def execute(self, data):

        command = data.get("command")

        method = getattr(self, command, None)

        if method is None:
            return f"No existe el comando '{command}'."

        return method(data)

    # ==================================================
    # Guardar información
    # ==================================================

    def remember(self, data):

        key = data.get("key")
        value = data.get("value")

        if not key:
            return "No especificaste la clave."

        if value is None:
            return "No especificaste el valor."

        self.memory[key] = value

        JSONManager.save(
            "data/memory.json",
            self.memory
        )

        return f"Recordaré que tu {key} es {value}."

    # ==================================================
    # Recuperar información
    # ==================================================

    def recall(self, data):

        key = data.get("key")

        if not key:
            return "No especificaste qué recordar."

        value = self.memory.get(key)

        if value is None:
            return f"No recuerdo tu {key}."

        return value

    # ==================================================
    # Eliminar información
    # ==================================================

    def forget(self, data):

        key = data.get("key")

        if not key:
            return "No especificaste qué olvidar."

        if key not in self.memory:
            return f"No existe '{key}' en memoria."

        del self.memory[key]

        JSONManager.save(
            "data/memory.json",
            self.memory
        )

        return f"He olvidado tu {key}."

    # ==================================================
    # Listar memoria
    # ==================================================

    def list_memories(self, data=None):

        if not self.memory:
            return "La memoria está vacía."

        return self.memory

    # ==================================================
    # Limpiar memoria
    # ==================================================

    def clear(self, data=None):

        self.memory.clear()

        JSONManager.save(
            "data/memory.json",
            self.memory
        )

        return "Memoria limpiada correctamente."

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
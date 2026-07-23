from app.memory.memory_database import MemoryDatabase
from app.memory.memory_resolver import MemoryResolver


# ==================================================
# MemoryManager
# ==================================================

class MemoryManager:

    def __init__(self):

        self.database = MemoryDatabase()

        self.resolver = MemoryResolver(
            self.database
        )

        print("=" * 50)
        print("[MemoryManager]")
        print("Inicializado correctamente.")
        print("=" * 50)

    # ==================================================
    # Guardar contexto
    # ==================================================

    def remember(self, data):

        self.resolver.remember(data)

    # ==================================================
    # Resolver contexto
    # ==================================================

    def resolve(self, data):

        return self.resolver.resolve(data)

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

        return self.resolver.last()

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
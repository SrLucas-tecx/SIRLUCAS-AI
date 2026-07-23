# ==================================================
# MemoryDatabase
# Guarda el contexto del asistente
# ==================================================

class MemoryDatabase:

    def __init__(self):

        self.data = {}

    # ==================================================
    # Guardar dato
    # ==================================================

    def save(self, key, value):

        self.data[key] = value

    # ==================================================
    # Obtener dato
    # ==================================================

    def get(self, key):

        return self.data.get(key)

    # ==================================================
    # Obtener toda la memoria
    # ==================================================

    def all(self):

        return self.data.copy()

    # ==================================================
    # Limpiar memoria
    # ==================================================

    def clear(self):

        self.data.clear()
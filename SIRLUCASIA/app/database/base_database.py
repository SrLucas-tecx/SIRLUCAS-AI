# ==================================================
# BaseDatabase
# Clase base para todas las bases de datos
# ==================================================

class BaseDatabase:

    def __init__(self):

        self.data = {}

    # ===============================
    # Buscar elemento
    # ===============================

    def find(self, key):

        if key is None:
            return None

        return self.data.get(key.lower())

    # ===============================
    # Agregar elemento
    # ===============================

    def add(self, key, value):

        self.data[key.lower()] = value

    # ===============================
    # Eliminar elemento
    # ===============================

    def delete(self, key):

        self.data.pop(key.lower(), None)

    # ===============================
    # Actualizar elemento
    # ===============================

    def update(self, key, value):

        self.data[key.lower()] = value

    # ===============================
    # Listar elementos
    # ===============================

    def list(self):

        return list(self.data.keys())
    
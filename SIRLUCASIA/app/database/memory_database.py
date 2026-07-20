from app.database.base_database import BaseDatabase
from app.utils.json_manager import JSONManager


# ==================================================
# MemoryDatabase
# Base de datos de la memoria del asistente
# ==================================================

class MemoryDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        memory = JSONManager.load(
            "data/memory.json"
        )

        if memory is None:
            memory = {}

        self.data = memory

    # ======================================
    # Guardar cambios en disco
    # ======================================

    def save(self):

        JSONManager.save(
            "data/memory.json",
            self.data
        )
from app.database.base_database import BaseDatabase


# ==================================================
# HistoryDatabase
# Historial de comandos ejecutados
# ==================================================

class HistoryDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        self.data = []
        
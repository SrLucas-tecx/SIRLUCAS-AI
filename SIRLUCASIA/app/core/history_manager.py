from datetime import datetime

from app.database.history_database import HistoryDatabase


class HistoryManager:

    def __init__(self):

        self.database = HistoryDatabase()

    # ===============================
    # Dispatcher
    # ===============================

    def execute(self, data):

        command = data.get("command")

        method = getattr(self, command, None)

        if method is None:
            return None

        return method(data)

    # ===============================
    # Registrar comando
    # ===============================

    def add(self, module, command, topic=None):

        self.database.data.append({

            "time": datetime.now(),

            "module": module,

            "command": command,

            "topic": topic

        })

    # ===============================
    # Obtener historial
    # ===============================

    def history(self):

        return self.database.data

    # ===============================
    # Último comando
    # ===============================

    def last(self):

        if not self.database.data:
            return None

        return self.database.data[-1]

    # ===============================
    # Limpiar historial
    # ===============================

    def clear(self):

        self.database.data.clear()
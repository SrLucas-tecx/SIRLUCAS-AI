import os

from app.database.program_database import ProgramDatabase


# ==================================================
# SystemManager
# Encargado de abrir, cerrar y controlar programas
# ==================================================

class SystemManager:

    def __init__(self):

        self.database = ProgramDatabase()

        print("=" * 50)
        print("[SystemManager]")
        print(f"{len(self.database.list())} aplicaciones registradas.")
        print("=" * 50)

    # ==================================================
    # Router
    # ==================================================

    def execute(self, data):

        command = data.get("command")

        method = getattr(self, command, None)

        if method is None:
            return f"No existe la acción '{command}'."

        return method(data)

    # ==================================================
    # Verificar existencia
    # ==================================================

    def exists(self, name):

        if not name:
            return False

        return self.database.find(name.lower()) is not None

    # ==================================================
    # Abrir aplicación
    # ==================================================

    def open(self, data):

        app = data.get("topic")

        if not app:
            return "No especificaste qué aplicación abrir."

        app = app.lower()

        program = self.database.find(app)

        if program is None:
            return f"No conozco la aplicación '{app}'."

        try:

            os.system(f'start "" "{program}"')

            return f"Abriendo {app}..."

        except Exception as e:

            return f"No pude abrir {app}: {e}"

    # ==================================================
    # Cerrar aplicación
    # ==================================================

    def close(self, data):

        app = data.get("topic")

        if not app:
            return "No especificaste qué aplicación cerrar."

        app = app.lower()

        program = self.database.find(app)

        if program is None:
            return f"No conozco la aplicación '{app}'."

        try:

            os.system(f'taskkill /IM "{program}" /F')

            return f"Cerrando {app}..."

        except Exception as e:

            return f"No pude cerrar {app}: {e}"
        
import subprocess
from app.database.program_database import ProgramDatabase

# ==================================================
# SystemManager
# Encargado de abrir, cerrar y controlar programas
# ==================================================

class SystemManager:

    def __init__(self):
        self.database = ProgramDatabase()
        self.last_program = None  # Guardar último programa abierto

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
        return self.database.find(name) is not None  # Normalización la hace ProgramDatabase

    # ==================================================
    # Abrir aplicación
    # ==================================================
    def open(self, data):
        app = data.get("topic")

        if not app:
            return "No especificaste qué aplicación abrir."

        program = self.database.find(app)

        if program is None:
            return f"No conozco la aplicación '{app}'."

        try:
            subprocess.Popen(program)  # abre sin bloquear
            self.last_program = app   # guardar último programa
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

        program = self.database.find(app)

        if program is None:
            return f"No conozco la aplicación '{app}'."

        try:
            result = subprocess.run(
                ["taskkill", "/IM", program, "/F"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return f"{app} cerrado correctamente."

            # Mostrar error real de Windows si existe
            return result.stderr.strip() or f"No pude cerrar {app}."
        except Exception as e:
            return f"No pude cerrar {app}: {e}"

    # ==================================================
    # Reiniciar aplicación
    # ==================================================
    def restart(self, data):
        app = data.get("topic")

        if not app:
            return "No especificaste qué aplicación reiniciar."

        self.close(data)
        self.open(data)

        return f"Reiniciando {app}..."

    # ==================================================
    # Verificar si está abierto
    # ==================================================
    def is_open(self, app):
        program = self.database.find(app)

        if program is None:
            return False

        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {program}"],
                capture_output=True,
                text=True
            )
            return program.lower() in result.stdout.lower()
        except Exception:
            return False

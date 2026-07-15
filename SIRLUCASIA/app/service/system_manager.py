import os


# ==================================================
# SystemManager
# Encargado de abrir, cerrar y controlar programas
# ==================================================

class SystemManager:

    def __init__(self):

        # Base de datos temporal de aplicaciones.
        # En el siguiente sprint esto se moverá a ProgramDatabase.
        self.apps = {

            "bloc de notas": "notepad.exe",
            "notepad": "notepad.exe",

            "calculadora": "calc.exe",
            "calc": "calc.exe",

            "explorador": "explorer.exe",

            "paint": "mspaint.exe",

            "vs code": "Code.exe",

            "cmd": "cmd.exe",

            "powershell": "powershell.exe"

        }

        print("=" * 50)
        print("[SystemManager]")
        print(f"{len(self.apps)} aplicaciones registradas.")
        print("=" * 50)

    # ==================================================
    # Punto de entrada del Router
    # ==================================================
    # Utiliza despacho dinámico para llamar al método
    # correspondiente al comando recibido.
    # ==================================================
    def execute(self, data):

        command = data.get("command")

        method = getattr(self, command, None)

        if method is None:
            return f"No existe la acción '{command}'."

        return method(data)

    # ==================================================
    # Abrir aplicación
    # ==================================================
    def open(self, data):

        app = data.get("topic")

        if not app:
            return "No especificaste qué aplicación abrir."

        app = app.lower()

        if app not in self.apps:
            return f"No conozco la aplicación '{app}'."

        try:

            os.system(f'start "" "{self.apps[app]}"')

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

        if app not in self.apps:
            return f"No conozco la aplicación '{app}'."

        try:

            os.system(f'taskkill /IM "{self.apps[app]}" /F')

            return f"Cerrando {app}..."

        except Exception as e:

            return f"No pude cerrar {app}: {e}"
        
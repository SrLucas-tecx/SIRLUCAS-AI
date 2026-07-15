from app.database.base_database import BaseDatabase


# ==================================================
# ProgramDatabase
# Base de datos de programas del sistema
# ==================================================

class ProgramDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        self.data = {

            # ==========================
            # Bloc de notas
            # ==========================
            "bloc de notas": "notepad.exe",
            "notepad": "notepad.exe",
            "editor": "notepad.exe",

            # ==========================
            # Calculadora
            # ==========================
            "calculadora": "calc.exe",
            "calc": "calc.exe",

            # ==========================
            # Paint
            # ==========================
            "paint": "mspaint.exe",

            # ==========================
            # Explorador
            # ==========================
            "explorador": "explorer.exe",
            "explorador de archivos": "explorer.exe",

            # ==========================
            # VS Code
            # ==========================
            "vs code": "Code.exe",
            "visual studio code": "Code.exe",
            "vscode": "Code.exe",
            "code": "Code.exe",

            # ==========================
            # Consolas
            # ==========================
            "cmd": "cmd.exe",
            "simbolo del sistema": "cmd.exe",

            "powershell": "powershell.exe",
            "power shell": "powershell.exe"

        }

    def find(self, name):

        if not name:
            return None

        return self.data.get(name.lower())
import os
import shutil
import subprocess
import webbrowser

from app.database.base_database import BaseDatabase


class ProgramDatabase(BaseDatabase):

    def __init__(self):
        super().__init__()

        # Alias conocidos
        self.data = {
            "bloc de notas": "notepad.exe",
            "notepad": "notepad.exe",
            "editor": "notepad.exe",

            "calculadora": "calc.exe",
            "calc": "calc.exe",

            "paint": "mspaint.exe",

            "explorador": "explorer.exe",
            "explorador de archivos": "explorer.exe",

            "vs code": "Code.exe",
            "visual studio code": "Code.exe",
            "vscode": "Code.exe",
            "code": "Code.exe",

            "cmd": "cmd.exe",
            "simbolo del sistema": "cmd.exe",

            "powershell": "powershell.exe",
            "power shell": "powershell.exe",
        }

        # Alias de navegadores
        self.browser_aliases = {
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",

            "edge": "msedge.exe",
            "microsoft edge": "msedge.exe",

            "firefox": "firefox.exe",
            "mozilla firefox": "firefox.exe",

            "opera": "opera.exe",
            "opera gx": "opera.exe",
        }

    def find(self, name):
        if not name:
            return None

        name = name.strip().lower()

        # ==========================================
        # 1. Buscar en base de datos
        # ==========================================

        if name in self.data:
            return self.data[name]

        # ==========================================
        # 2. Buscar navegador
        # ==========================================

        if name in self.browser_aliases:

            executable = self.browser_aliases[name]

            if shutil.which(executable):
                return executable

        # ==========================================
        # 3. Buscar directamente en PATH
        # ==========================================

        executable = shutil.which(name)

        if executable:
            return executable

        # ==========================================
        # 4. Si escribió .exe
        # ==========================================

        if not name.endswith(".exe"):
            executable = shutil.which(name + ".exe")

            if executable:
                return executable

        # ==========================================
        # No encontrado
        # ==========================================

        return None

    def is_default_browser(self, name):
        """
        Determina si el usuario está pidiendo
        específicamente el navegador predeterminado.
        """

        if not name:
            return False

        name = name.lower().strip()

        return name in {
            "navegador",
            "navegador predeterminado",
            "navegador por defecto",
            "browser",
            "browser predeterminado",
        }

    def open_default_browser(self, url=None):
        """
        Abre el navegador predeterminado de Windows.
        """

        if url:
            return webbrowser.open(url)

        return webbrowser.open("about:blank")
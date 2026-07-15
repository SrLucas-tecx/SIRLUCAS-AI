from app.database.base_database import BaseDatabase

from app.database.program_database import ProgramDatabase

db = ProgramDatabase()

print(db.list())
class ProgramDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        self.data = {

            "bloc de notas": {
                "exe": "notepad.exe",
                "aliases": ["notepad", "editor"]
            },

            "calculadora": {
                "exe": "calc.exe",
                "aliases": ["calc"]
            },

            "paint": {
                "exe": "mspaint.exe",
                "aliases": []
            },

            "explorador": {
                "exe": "explorer.exe",
                "aliases": ["explorer"]
            },

            "vs code": {
                "exe": "Code.exe",
                "aliases": [
                    "code",
                    "vscode",
                    "visual studio code"
                ]
            },

            "cmd": {
                "exe": "cmd.exe",
                "aliases": [
                    "terminal"
                ]
            },

            "powershell": {
                "exe": "powershell.exe",
                "aliases": [
                    "power shell"
                ]
            }

        }

    def find(self, name):

        program = super().find(name)

        if program:
            return program

        if name is None:
            return None

        name = name.lower()

        for program in self.data.values():

            if name in program["aliases"]:

                return program

        return None
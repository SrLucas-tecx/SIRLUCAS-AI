from app.database.base_database import BaseDatabase


# ==================================================
# CalculatorDatabase
# Base de datos de operadores matemáticos
# ==================================================

class CalculatorDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        self.data = {

            "+": "add",

            "-": "subtract",

            "*": "multiply",

            "/": "divide",

            "%": "mod",

            "**": "power",

            "^": "power"

        }
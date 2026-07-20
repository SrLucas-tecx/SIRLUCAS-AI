from app.database.calculator_database import CalculatorDatabase


class CalculatorManager:

    def __init__(self):

        self.database = CalculatorDatabase()

        print("=" * 50)
        print("[CalculatorManager]")
        print("Inicializado correctamente.")
        print("=" * 50)

    # =====================================
    # Dispatcher
    # =====================================

    def execute(self, data):

        command = data.get("command")

        method = getattr(self, command, None)

        if method is None:
            return f"No existe el comando '{command}'."

        return method(data)

    # =====================================
    # Calcular
    # =====================================

    def calculate(self, data):

        expression = data.get("topic")

        if not expression:
            return "No especificaste una operación."

        try:

            result = eval(expression)

            return f"Resultado: {result}"

        except Exception:

            return "No pude calcular esa operación."
        
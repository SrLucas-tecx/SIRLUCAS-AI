from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
from app.database.calculator_database import CalculatorDatabase

class CalculatorManager:

    def __init__(self):
        self.database = CalculatorDatabase()
        print("=" * 50)
        print("[CalculatorManager]")
        print("Inicializado correctamente.")
        print("=" * 50)

    def execute(self, data):
        command = data.get("command")
        method = getattr(self, command, None)
        if method is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="calculator",
                command=command,
                message=f"No existe la acción '{command}'."
            )
        return method(data)

    def calculate(self, data):
        expression = data.get("topic")
        if not expression:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="calculator",
                command="calculate",
                message="No especificaste una operación."
            )
        try:
            result = eval(expression)
            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="calculator",
                command="calculate",
                message=f"Resultado: {result}",
                data=result
            )
        except Exception as e:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="calculator",
                command="calculate",
                message="No pude calcular esa operación.",
                error=str(e)
            )

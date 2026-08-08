"""
CalculatorManager
=================

Manager de dominio "calculadora" de SIRLUCAS AI.

Evalúa expresiones aritméticas recibidas desde el pipeline de forma
SEGURA, sin usar `eval()`. Los operadores permitidos se leen
exclusivamente de `CalculatorDatabase`, que es la única fuente de
verdad sobre qué símbolos soporta la calculadora: si en el futuro se
agrega o quita un operador ahí, este evaluador se actualiza solo, sin
tocar este archivo.

Nota de producto: el operador "^" se interpreta como POTENCIA, no como
XOR bit a bit (que es el significado por defecto de `ast.BitXor` en
Python). Es una decisión explícita del proyecto, documentada aquí para
que no se "corrija" por error en el futuro.
"""

import ast
import operator
import logging
from typing import Callable

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
from app.database.calculator_database import CalculatorDatabase

# Definimos un tipo más preciso para números
Number = float | int
# Configuración de logger en lugar de print
logger = logging.getLogger(__name__)

# Símbolo -> (nodo AST que Python genera para ese símbolo, función a ejecutar)
_BINARY_OPERATORS: dict[str, tuple[type, Callable[[Number, Number], Number]]] = {
    "+": (ast.Add, operator.add),
    "-": (ast.Sub, operator.sub),
    "*": (ast.Mult, operator.mul),
    "/": (ast.Div, operator.truediv),
    "%": (ast.Mod, operator.mod),
    "**": (ast.Pow, operator.pow),
    # "^" eliminado: ahora se reemplaza antes del AST
}

_UNARY_OPERATORS: dict[str, tuple[type, Callable[[Number], Number]]] = {
    "-": (ast.USub, operator.neg),
    "+": (ast.UAdd, operator.pos),
}


class CalculatorManager:
    """Ejecuta operaciones aritméticas para el comando `calculate`."""

    def __init__(self) -> None:
        self.database = CalculatorDatabase()

        # Whitelist real de nodos AST permitidos, derivada de los
        # símbolos que CalculatorDatabase declara soportados.
        self._allowed_binary_nodes: dict[type, Callable[[Number, Number], Number]] = {
            node_type: func
            for symbol, (node_type, func) in _BINARY_OPERATORS.items()
            if symbol in self.database.data
        }
        self._allowed_unary_nodes: dict[type, Callable[[Number], Number]] = {
            node_type: func
            for symbol, (node_type, func) in _UNARY_OPERATORS.items()
            if symbol in self.database.data
        }

        logger.info("[CalculatorManager] Inicializado correctamente.")

    # ==========================================
    # Dispatcher
    # ==========================================
    def execute(self, data: dict[str, object]) -> ActionResult:
        command = data.get("command")
        method = getattr(self, command, None)
        if method is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="calculator",
                command=command,
                message=f"No existe la acción '{command}'.",
            )
        return method(data)

    # ==========================================
    # Calcular
    # ==========================================
    def calculate(self, data: dict) -> ActionResult:
        expression = data.get("topic")
        if not expression:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="calculator",
                command="calculate",
                message="No especificaste una operación.",
            )

        try:
            result = self._safe_eval(expression)
            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="calculator",
                command="calculate",
                message=f"Resultado: {result}",
                data=result,
            )

        except SyntaxError:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="calculator",
                command="calculate",
                message="No entendí esa operación.",
                error="Expresión con sintaxis inválida.",
            )

        except ZeroDivisionError:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="calculator",
                command="calculate",
                message="No puedo dividir entre cero.",
                error="División entre cero.",
            )

        except ValueError as e:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="calculator",
                command="calculate",
                message="No pude calcular esa operación.",
                error=str(e),
            )

        except Exception as e:
            logger.exception("[CalculatorManager] Error inesperado en calculate()")
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="calculator",
                command="calculate",
                message="No pude calcular esa operación.",
                error=str(e),
            )

    # ==========================================
    # Evaluador seguro (reemplaza a eval())
    # ==========================================
    def _safe_eval(self, expression: str) -> Number:
        """
        Evalúa una expresión aritmética simple sin ejecutar código
        Python arbitrario.

        Solo permite números y los operadores registrados en
        `CalculatorDatabase`. Cualquier otro nodo del árbol sintáctico
        se rechaza con `ValueError`.

        Nunca usar eval() aquí.
        Cualquier ampliación debe hacerse agregando nodos AST permitidos.
        """

        # Protección contra entradas desproporcionadas
        if len(expression) > 500:
            raise ValueError("La expresión es demasiado larga.")

        # Reemplazar ^ por ** antes de parsear
        if "^" in self.database.data:
            expression = expression.replace("^", "**")

        tree = ast.parse(expression, mode="eval")

        if sum(1 for _ in ast.walk(tree)) > 100:
            raise ValueError("Expresión demasiado compleja.")

        return self._eval_node(tree.body)

    def _eval_node(self, node: ast.AST) -> Number:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise ValueError(f"Valor no permitido: {node.value!r}")
            # Límite opcional para literales numéricos
            if abs(node.value) > 1e100:
                raise ValueError("Número demasiado grande.")
            return node.value

        if isinstance(node, ast.BinOp):
            func = self._allowed_binary_nodes.get(type(node.op))
            if func is None:
                raise ValueError("Operador no permitido.")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return func(left, right)

        if isinstance(node, ast.UnaryOp):
            func = self._allowed_unary_nodes.get(type(node.op))
            if func is None:
                raise ValueError("Operador no permitido.")
            return func(self._eval_node(node.operand))

        raise ValueError("Expresión no permitida.")


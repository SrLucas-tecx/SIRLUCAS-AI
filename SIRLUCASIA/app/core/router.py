from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus


class Router:

    def __init__(self):
        self.modules = {}

    def register(self, name, module):
        self.modules[name.lower()] = module
        print(f"[Router] Módulo registrado -> {name.lower()}")

    def route(self, data):

        if not isinstance(data, dict):
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="router",
                command=None,
                message="Datos inválidos: se esperaba un diccionario.",
            )

        module_name = (data.get("module") or "").lower()
        command = data.get("command")

        if not module_name:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="router",
                command=command,
                message="No se especificó el módulo.",
            )

        manager = self.modules.get(module_name)

        if manager is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="router",
                command=command,
                message=f"No existe el módulo '{module_name}'.",
            )

        try:
            response = manager.execute(data)

        except Exception as e:
            print(
                f"[Router] Error ejecutando "
                f"{module_name}.{command}: {e}"
            )

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module=module_name,
                command=command,
                message=f"Error ejecutando la acción '{command}'.",
                error=str(e),
            )

        # ==============================
        # MEMORIA
        # ==============================

        memory = self.modules.get("memory")

        if memory:
            try:
                memory.remember(data)
            except Exception as e:
                print(
                    f"[Router] Error en memory.remember: {e}"
                )

        return response
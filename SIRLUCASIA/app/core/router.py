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
                message="Datos inválidos: se esperaba un diccionario."
            )

        command = data.get("command")
        topic = data.get("topic")

        # ---------- OPEN ----------
        if command == "open":
            response = self._resolve_open(topic)
            if response is not None:
                return response

        # ---------- CLOSE ----------
        if command == "close":
            response = self._resolve_close(topic)
            if response is not None:
                return response

        module = (data.get("module") or "").lower()

        if not module:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="router",
                command=command,
                message="No se especificó el módulo."
            )

        manager = self.modules.get(module)

        if manager is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="router",
                command=command,
                message=f"No existe el módulo '{module}'."
            )

        response = manager.execute(data)

        memory = self.modules.get("memory")
        if memory:
            try:
                memory.remember(data)
            except Exception as e:
                print(f"[Router] Error en memory.remember: {e}")

        return response

    # ==================================================
    # Resolver OPEN
    # ==================================================
    def _resolve_open(self, topic):
        system = self.modules.get("system")
        document = self.modules.get("document")

        if system:
            program = system.database.find(topic)
            if program:
                return system.open({"topic": topic})

        if document:
            if document.exists(topic):
                return document.open({"topic": topic})

        return None

    # ==================================================
    # Resolver CLOSE
    # ==================================================
    def _resolve_close(self, topic):
        system = self.modules.get("system")
        document = self.modules.get("document")

        if system:
            program = system.database.find(topic)
            if program:
                return system.close({"topic": topic})

        if document:
            if document.exists(topic):
                return document.close({"topic": topic})

        return None

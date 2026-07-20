class Router:

    def __init__(self):

        self.modules = {}

    # ==================================================
    # Registrar módulos
    # ==================================================

    def register(self, name, module):

        self.modules[name.lower()] = module

        print(f"[Router] Módulo registrado -> {name.lower()}")

    # ==================================================
    # Router principal
    # ==================================================

    def route(self, data):

        if not isinstance(data, dict):
            return None

        module = data.get("module", "").lower()
        command = data.get("command")
        topic = data.get("topic")

        # Resolver OPEN automáticamente

        if command == "open":

            response = self._resolve_open(topic)

            if response is not None:
                return response

        # Resolver CLOSE automáticamente

        if command == "close":

            response = self._resolve_close(topic)

            if response is not None:
                return response

        manager = self.modules.get(module)

        if manager is None:
            return f"No existe el módulo '{module}'."

        return manager.execute(data)

    # ==================================================
    # Resolver OPEN
    # ==================================================

    def _resolve_open(self, topic):

        system = self.modules.get("system")
        document = self.modules.get("document")

        if system and system.exists(topic):

            return system.open({
                "topic": topic
            })

        if document and document.exists(topic):

            return document.open({
                "topic": topic
            })

        return None

    # ==================================================
    # Resolver CLOSE
    # ==================================================

    def _resolve_close(self, topic):

        system = self.modules.get("system")
        document = self.modules.get("document")

        if system and system.exists(topic):

            return system.close({
                "topic": topic
            })

        if document and document.exists(topic):

            return document.close({
                "topic": topic
            })

        return None
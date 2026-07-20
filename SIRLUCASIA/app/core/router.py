class Router:

    def __init__(self):

        self.modules = {}

    # ============================================
    # Registrar módulos
    # ============================================

    def register(self, name, module):

        self.modules[name.lower()] = module

        print(f"[Router] Módulo registrado -> {name.lower()}")

    # ============================================
    # Router principal
    # ============================================

    def route(self, data):

        if not isinstance(data, dict):
            return None

        module = data.get("module", "").lower()
        command = data.get("command")
        topic = data.get("topic")

        # Resolver automáticamente OPEN

        if command == "open":

            response = self._resolve_open(topic)

            if response is not None:
                return response

        # Resolver automáticamente CLOSE

        if command == "close":

            response = self._resolve_close(topic)

            if response is not None:
                return response

        # Router normal

        manager = self.modules.get(module)

        if manager is None:
            return f"No existe el módulo '{module}'."

        return manager.execute(data)

    # ============================================
    # Resolver apertura
    # ============================================

    def _resolve_open(self, topic):

        if not topic:
            return None

        system = self.modules.get("system")
        document = self.modules.get("document")

        # Primero revisar programas

        if system:

            if system.database.find(topic):

                return system.open({
                    "topic": topic
                })

        # Después revisar documentos

        if document:

            if document.exists(topic):

                return document.open({
                    "topic": topic
                })

        return None

    # ============================================
    # Resolver cierre
    # ============================================

    def _resolve_close(self, topic):

        if not topic:
            return None

        system = self.modules.get("system")
        document = self.modules.get("document")

        # Programas

        if system:

            if system.database.find(topic):

                return system.close({
                    "topic": topic
                })

        # Documentos

        if document:

            if document.exists(topic):

                return document.close({
                    "topic": topic
                })

        return None
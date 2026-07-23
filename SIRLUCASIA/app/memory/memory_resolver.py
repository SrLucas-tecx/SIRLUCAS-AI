# ==================================================
# MemoryResolver
# Decide qué recordar y qué recuperar
# ==================================================

class MemoryResolver:

    def __init__(self, database):

        self.database = database

    # ==================================================
    # Registrar acción
    # ==================================================

    def remember(self, data):

        command = data.get("command")
        module = data.get("module")
        topic = data.get("topic")

        if topic:
            self.database.save("last_topic", topic)

        if command:
            self.database.save("last_command", command)

        if module:
            self.database.save("last_module", module)

    # ==================================================
    # Resolver datos faltantes
    # ==================================================

    def resolve(self, data):

        if not data.get("topic"):

            topic = self.last_topic()

            if topic:
                data["topic"] = topic

        if not data.get("module"):

            module = self.last_module()

            if module:
                data["module"] = module

        return data

    # ==================================================
    # Último tema
    # ==================================================

    def last_topic(self):

        return self.database.get("last_topic")

    # ==================================================
    # Último comando
    # ==================================================

    def last_command(self):

        return self.database.get("last_command")

    # ==================================================
    # Último módulo
    # ==================================================

    def last_module(self):

        return self.database.get("last_module")

    # ==================================================
    # Último contexto
    # ==================================================

    def last(self):

        return {

            "topic": self.last_topic(),
            "module": self.last_module(),
            "command": self.last_command()

        }
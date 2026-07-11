class CommandManager:

    def __init__(self, memory_manager):

        self.memory = memory_manager

    def execute(self, message):

        print(f"Ejecutando comando: {message}")

        parts = message.split()

        if len(parts) == 0:
            return None

        command = parts[0].lower()

        if command == "remember":
            return self.remember(parts)

        if command == "recall":
            return self.recall(parts)

        return None

    def remember(self, parts):

        if len(parts) < 3:
            return "Uso: remember <clave> <valor>"

        key = parts[1]
        value = " ".join(parts[2:])

        print(f"Guardando: {key} = {value}")

        self.memory.remember(key, value)

        return f"Lo recordaré. ({key} = {value})"

    def recall(self, parts):

        if len(parts) < 2:
            return "Uso: recall <clave>"

        key = parts[1]

        value = self.memory.recall(key)

        if value is None:
            return f"No recuerdo '{key}'."

        return f"{key} = {value}"
    
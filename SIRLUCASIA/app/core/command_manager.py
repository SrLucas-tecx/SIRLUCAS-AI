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

        if len(parts) < 2:
            return "Uso: remember <clave> <valor>"

        key = parts[1]

        value = self .memory.recall(key)
        #------------------------------------------------------------#
        #nesesito checar esto
        #------------------------------------------------------------#

        if value is None:
            return f"No lo recuerdo '{key}'."
        
        return f"{key} = [value]"
    
        print(f"Guardando: {key} = {value}")

        self.memory.remember(key, value)

        return f"Lo recordaré. ({key} = {value})"
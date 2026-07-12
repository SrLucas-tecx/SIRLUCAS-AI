class CommandManager:

    def __init__(self, memory_manager):

        self.memory = memory_manager

        # Comandos ejecutables
        self.commands = {
            "remember": self.remember,
            "recall": self.recall,
            "forget": self.forget,
            "list": self.list_memories,
            "help": self.help
        }

        # Información de ayuda
        self.command_info = {
            "remember": {
                "description": "Guarda información en memoria.",
                "usage": "remember <clave> <valor>"
            },
            "recall": {
                "description": "Recupera una memoria.",
                "usage": "recall <clave>"
            },
            "forget": {
                "description": "Olvida una memoria.",
                "usage": "forget <clave>"
            },
            "list": {
                "description": "Muestra todas las memorias.",
                "usage": "list"
            },
            "help": {
                "description": "Muestra la ayuda.",
                "usage": "help"
            }
        }

    def execute(self, data):

        print(f"Ejecutando comando: {data}")

         # ==========================
         # NUEVO SISTEMA (dict)
         # ==========================

        if isinstance(data, dict):

            command = data.get("command")

            handler = self.commands.get(command)

            if handler:
                return handler(data)
            return None

        # ==========================
        # SISTEMA ANTIGUO (string)
        # ==========================
        
        if isinstance(data, str):

           parts = data.split()

           if len(parts) == 0:
            return None

        command = parts[0].lower()

        handler = self.commands.get(command)

        if handler:
            return handler(parts)

        return None
    
    def remember(self, data):
        #Nuevo sistema 
        if isinstance(data,dict):

            key = data["key"]
            value = data["value"]
        else:

        #    if lend(data)< 3:
                return "Uso:remmeber <clave> <valor>"
        #print(f"Guardando: {key}={value}")

        #self.memory.remember(key,value)

        #return f"lo recordare.({key}={value})"
    

    def recall(self, parts):

        if len(parts) < 2:
            return "Uso: recall <clave>"

        key = parts[1]

        value = self.memory.recall(key)

        if value is None:
            return f"No recuerdo '{key}'."

        return f"{key} = {value}"
    

    def forget(self, parts):

        if len(parts) < 2:
            return "Uso: forget <clave>"

        key = parts[1]

        if self.memory.forget(key):
            return f"He olvidado '{key}'."

        return f"No encontré '{key}' en mi memoria."

    def list_memories(self, parts):

        memories = self.memory.list_memories()

        if not memories:
            return "No tengo memorias guardadas."

        response = "Memorias guardadas:\n"

        for key, value in memories.items():
            response += f"\n- {key}: {value}"

        return response

    def help(self, parts):

        response = (
            "\n"
            "==============================\n"
            "       SIRLUCAS AI\n"
            "     Lista de comandos\n"
            "==============================\n\n"
            "remember <clave> <valor>\n"
            "    Guarda un dato en memoria.\n\n"
            "recall <clave>\n"
            "    Recupera un dato guardado.\n\n"
            "forget <clave>\n"
            "    Elimina un dato de memoria.\n\n"
            "list\n"
            "    Muestra todas las memorias.\n\n"
            "help\n"
            "    Muestra esta ayuda."
        )

        return response
import logging
from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus

class CommandManager:

    def __init__(self, memory_manager):

        self.memory = memory_manager

        # Comandos disponibles
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

    def register_command(self, name, handler, description=None, usage=None):
        """Extensión ligera para registrar comandos nuevos sin refactorizar."""
        if not callable(handler):
            raise TypeError("El handler de un comando debe ser invocable.")

        key = (name or "").lower()
        self.commands[key] = handler

        if description is not None or usage is not None:
            self.command_info[key] = {
                "description": description or "Comando personalizado.",
                "usage": usage or key
            }

        return handler

    def register(self, name, handler, description=None, usage=None):
        """Alias compatible para registrar nuevos comandos externos."""
        return self.register_command(name, handler, description, usage)

    def register_extension(self, name, handler, description=None, usage=None):
        """Compatibilidad para extensiones futuras del proyecto."""
        return self.register_command(name, handler, description, usage)

    def execute(self, data):
        command = data.get("command") if isinstance(data, dict) else None
        handler = self.commands.get(command)

        if handler:
            return handler(data)

        return ActionResult(
            success=False,
            status=ActionStatus.ERROR,
            module="command",
            command=command,
            message=f"No existe el comando '{command}'.",
            error="Comando desconocido en CommandManager."
        )

    def remember(self, data):
        if isinstance(data, dict):
            key = data.get("key")
            value = data.get("value")
        else:
            if len(data) < 3:
                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="command",
                    command="remember",
                    message="Uso: remember <clave> <valor>",
                    error="Argumentos insuficientes."
                )
            key = data[1]
            value = " ".join(data[2:])

        self.memory.remember({"key": key, "value": value})

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="command",
            command="remember",
            message=f"Lo recordaré. ({key} = {value})",
            data={"key": key, "value": value}
        )

    def recall(self, data):
        if isinstance(data, dict):
            key = data.get("key")
        else:
            if len(data) < 2:
                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="command",
                    command="recall",
                    message="Uso: recall <clave>",
                    error="Argumentos insuficientes."
                )
            key = data[1]

        value = self.memory.recall({"key": key})

        if not value.success:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="command",
                command="recall",
                message=f"No recuerdo '{key}'."
            )

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="command",
            command="recall",
            message=f"{key} = {value.message}",
            data={"key": key, "value": value.message}
        )

    def forget(self, data):
        if isinstance(data, dict):
            key = data.get("key")
        else:
            if len(data) < 2:
                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="command",
                    command="forget",
                    message="Uso: forget <clave>",
                    error="Argumentos insuficientes."
                )
            key = data[1]

        result = self.memory.forget({"key": key})

        if not result.success:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="command",
                command="forget",
                message=f"No encontré '{key}' en mi memoria."
            )

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="command",
            command="forget",
            message=f"He olvidado '{key}'.",
            data={"key": key}
        )

    def list_memories(self, data=None):
        memories = self.memory.list_memories()

        if not memories.success or not memories.data:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="command",
                command="list",
                message="No tengo memorias guardadas."
            )

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="command",
            command="list",
            message="Memorias guardadas.",
            data=memories.data
        )

    def help(self, data=None):
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="command",
            command="help",
            message="Lista de comandos disponible.",
            data=self.command_info
        )

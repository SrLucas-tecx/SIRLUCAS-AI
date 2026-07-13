import random

print("ASSISTANT NUEVO CARGADO")

from app.core.intent_manager import IntentManager
from app.core.memory_manager import MemoryManager
from app.core.command_manager import CommandManager
from app.modules.parser import Parser
from app.core.router import Router
from app.core.context_manager import ContextManager


class Assistant:

    def __init__(self):

        self.name = "SIRLUCAS AI"
        self.version = "0.1"

        # Módulos principales
        self.intent_manager = IntentManager()
        self.memory_manager = MemoryManager()
        self.command_manager = CommandManager(self.memory_manager)

        # Contexto de conversación
        self.context = ContextManager()

        # Router
        self.router = Router()

        self.router.register(
            "memory",
            self.command_manager
        )

        # Parser
        self.parser = Parser()

    def start(self):

        self.show_banner()
        self.chat()

    def show_banner(self):

        print("=" * 50)
        print(f"{self.name} - Versión {self.version}")
        print("=" * 50)
        print("¡Qué onda!")
        print("Mi nombre es SIRLUCAS AI :)")

        if self.intent_manager.intents:
            print("Intenciones cargadas correctamente")
        else:
            print("Error al cargar las intenciones")

        print("=" * 50)

    def chat(self):

        while True:

            raw_message = input("\nTú > ")

            # Salir
            if raw_message.lower() in [
                "salir",
                "exit",
                "quit"
            ]:
                self.stop()
                break

            # Parser
            message = self.parser.parse(raw_message)

            # ==========================
            # Actualizar Contexto
            # ==========================
            if isinstance(message, dict):

                self.context.update(message)

                print("\n>>> CONTEXTO")
                print(self.context.get())
                print()

            print(">>> Llamando al Router")

            # Router
            if isinstance(message, dict):

                response = self.router.route(message)

            else:

                response = self.command_manager.execute(message)

            print(">>> Respuesta:", response)

            # IntentManager
            if response is None:
                response = self.intent_manager.process(raw_message)

            print(f"\n{self.name} > {response}")

    def stop(self):

        despedida = self.intent_manager.get_by_tag("despedida")

        if despedida:
            print(
                f"\n{self.name} > "
                f"{random.choice(despedida['responses'])}"
            )
        else:
            print(f"\n{self.name} > Hasta luego.")


if __name__ == "__main__":

    assistant = Assistant()
    assistant.start()
    
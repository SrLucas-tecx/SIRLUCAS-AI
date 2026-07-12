import random

print("ASSISTANT NUEVO CARGADO")

from app.core.intent_manager import IntentManager
from app.core.memory_manager import MemoryManager
from app.core.command_manager import CommandManager
from app.modules.parser import Parser
from app.core.router import Router





class Assistant:

    def __init__(self):

        self.name = "SIRLUCAS AI"
        self.version = "0.1"
        

        # Inicializar los módulos principales
        self.intent_manager = IntentManager()
        self.memory_manager = MemoryManager()
        self.command_manager = CommandManager(self.memory_manager)

        # Inicializar Router
        self.router = Router()

        # Registrar módulos
        self.router.register(
            "memory",
            self.command_manager
        )

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

            message = input("\nTú > ")
            message = self.parser.parse(message)

            if message.lower() in [
                "salir",
                "exit",
                "quit"
            ]:
                self.stop()
                break

            # Primero intenta ejecutar un comando
            print(">>> Llamando a CommandManager")
            response = self.command_manager.execute(message)
            print(">>> Respuesta:", response)
            
            # Si no era un comando, busca una intención
            if response is None:
                response = self.intent_manager.process(message)

            print(f"\n{self.name} > {response}")

    def stop(self):

        despedida = self.intent_manager.get_by_tag("despedida")

        if despedida:
            print(f"\n{self.name} > {random.choice(despedida['responses'])}")
        else:
            print(f"\n{self.name} > Hasta luego.")

if __name__ == "__main__":

    assistant = Assistant()
    assistant.start()
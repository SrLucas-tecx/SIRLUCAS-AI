import random

print("ASSISTANT NUEVO CARGADO")

from app.core.intent_manager import IntentManager
from app.core.memory_manager import MemoryManager
from app.core.command_manager import CommandManager
from app.modules.parser import Parser
from app.core.router import Router
from app.core.context_manager import ContextManager
from app.core.knowledge_manager import KnowledgeManager
from app.core.web_manager import WebManager
from app.service.system_manager import SystemManager
from app.service.document_manager import DocumentManager




class Assistant:

    def __init__(self):

        self.name = "SIRLUCAS AI"
        self.version = "0.1"

        # Modo depuración
        self.debug = True

        # ==========================
        # Módulos principales
        # ==========================

        self.intent_manager = IntentManager()
        self.memory_manager = MemoryManager()
        self.command_manager = CommandManager(self.memory_manager)
        self.context = ContextManager()

        self.knowledge = KnowledgeManager()
        self.web = WebManager()

        self.system = SystemManager()

        self.document = DocumentManager()
        # ==========================
        # Router
        # ==========================

        self.router = Router()

        self.router.register(
            "memory",
            self.command_manager
        )
        self.router.register(
            "knowledge",
            self.knowledge)
        
        self.router.register(
            "web",
            self.web)
        
        self.router.register(
            "system",
            self.system)
        
        self.router.register(
            "document",
            self.document)
        # ==========================
        # Parser
        # ==========================

        self.parser = Parser()




    def start(self):

        self.show_banner()
        self.chat()

    def show_banner(self):

        print("=" * 60)
        print(f"{self.name} | Versión {self.version}")
        print("=" * 60)
        print("¡Qué onda!")
        print("Mi nombre es SIRLUCAS AI :)")

        if self.intent_manager.intents:
            print("Intenciones cargadas correctamente")
        else:
            print("Error al cargar las intenciones")

        print("=" * 60)

    def chat(self):

        while True:

            raw_message = input("\nTú > ")

            # ==========================
            # Salir
            # ==========================

            if raw_message.lower() in [
                "salir",
                "exit",
                "quit"
            ]:
                self.stop()
                break

            # ==========================
            # Parser
            # ==========================

            message = self.parser.parse(raw_message)

            # ==========================
            # Actualizar contexto
            # ==========================

            if isinstance(message, dict):

                self.context.update(message)

                if self.debug:

                    print("\n========== CONTEXTO ==========")
                    print("Turno   :", self.context.turn())
                    print("Tema    :", self.context.topic())
                    print("Módulo  :", self.context.module())
                    print("Comando :", self.context.command())
                    print("==============================\n")

            # ==========================
            # Router / CommandManager
            # ==========================

            if self.debug:
                print(">>> Llamando al Router")

            if isinstance(message, dict):

                response = self.router.route(message)

            else:

                response = self.command_manager.execute(message)

            if self.debug:
                print(">>> Respuesta:", response)

            # ==========================
            # IntentManager
            # ==========================

            if response is None:

                response = self.intent_manager.process(raw_message)

            # ==========================
            # Respuesta por defecto
            # ==========================

            if response is None:

                response = "Lo siento, todavía estoy aprendiendo."

            print(f"\n{self.name} > {response}")

    def stop(self):

        despedida = self.intent_manager.get_by_tag(
            "despedida"
        )

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
import random

from app.core.intent_manager import IntentManager
from app.core.memory_manager import MemoryManager
from app.core.command_manager import CommandManager
from app.modules.parser import Parser
from app.core.router import Router
from app.core.context_manager import ContextManager
from app.core.conversation_manager import ConversationManager
from app.core.history_manager import HistoryManager
from app.core.knowledge_manager import KnowledgeManager
from app.core.web_manager import WebManager
from app.core.calculator_manager import CalculatorManager
from app.service.system_manager import SystemManager
from app.service.document_manager import DocumentManager
from app.core.context_resolver import ContextResolver
from app.resolvers import ReferenceResolver
from app.core.entity_resolver import EntityResolver
from app.core.action_planner import ActionPlanner
from app.core.intent_resolver import IntentResolver
from app.core.task_executor import TaskExecutor   # 👈 agregado


class Assistant:

    def __init__(self):
        self.name = "SIRLUCAS AI"
        self.version = "0.1"
        self.debug = True

        # ====================================
        # Managers principales
        # ====================================
        self.intent_manager = IntentManager()
        self.memory = MemoryManager()
        self.command_manager = CommandManager(self.memory)
        self.context = ContextManager()
        self.reference_resolver = ReferenceResolver(self.context)
        self.context_resolver = ContextResolver()
        self.entity_resolver = EntityResolver()
        self.action_planner = ActionPlanner()
        self.intent_resolver = IntentResolver()
        self.conversation = ConversationManager()
        self.history = HistoryManager()
        self.knowledge = KnowledgeManager()
        self.web = WebManager()
        self.system = SystemManager()
        self.document = DocumentManager()
        self.calculator = CalculatorManager()

        # ====================================
        # Router
        # ====================================
        self.router = Router()
        self.router.register("memory", self.memory)
        self.router.register("knowledge", self.knowledge)
        self.router.register("web", self.web)
        self.router.register("system", self.system)
        self.router.register("document", self.document)
        self.router.register("calculator", self.calculator)
        self.router.register("conversation", self.conversation)
        self.router.register("history", self.history)

        # Executor 👇 nuevo
        self.executor = TaskExecutor(self.router, self.history)

        # Parser
        self.parser = Parser()

    # ====================================
    # Inicio
    # ====================================
    def start(self):
        self.show_banner()
        self.chat()

    # ====================================
    # Banner
    # ====================================
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

    # ====================================
    # Chat principal
    # ====================================
    def chat(self):
        while True:
            raw_message = input("\nTú > ")

            if raw_message.lower() in ["salir", "exit", "quit"]:
                self.stop()
                break

            # ----------------------------
            # Parser
            # ----------------------------
            message = self.parser.parse(raw_message, self.context)

            if isinstance(message, dict):
                message = self.entity_resolver.resolve(message)
                message = self.reference_resolver.resolve(message)
                message = self.context_resolver.resolve(message, self.context)
                message = self.intent_resolver.resolve(message)
                self.context.update(message)

                if self.debug:
                    print("\n========== CONTEXTO ==========")
                    print("Turno   :", self.context.turn())
                    print("Tema    :", self.context.topic())
                    print("Módulo  :", self.context.module())
                    print("Comando :", self.context.command())
                    print("Entidad :", message.get("entity"))
                    print("==============================\n")

            # ----------------------------
            # ActionPlanner + Executor
            # ----------------------------
            if self.debug:
                print(">>> Planificando acciones")

            response = None
            if isinstance(message, dict):
                actions = self.action_planner.plan(message)
                responses = self.executor.execute(actions)   # 👈 nuevo flujo
                response = responses[-1] if responses else None
            else:
                response = self.command_manager.execute(message)

            if self.debug:
                print(">>> Respuesta:", response)
                print(">>> Último comando")
                print(self.history.last())

            # ----------------------------
            # IntentManager
            # ----------------------------
            if response is None:
                response = self.intent_manager.process(raw_message)

            if response is None:
                response = "Lo siento, todavía estoy aprendiendo."

            # 👇 Ahora imprime el mensaje del ActionResult
            if hasattr(response, "message"):
                print(f"\n{self.name} > {response.message}")
            else:
                print(f"\n{self.name} > {response}")

    # ====================================
    # Salida
    # ====================================
    def stop(self):
        despedida = self.intent_manager.get_by_tag("despedida")

        if despedida:
            print(f"\n{self.name} > {random.choice(despedida['responses'])}")
        else:
            print(f"\n{self.name} > Hasta luego.")


if __name__ == "__main__":
    assistant = Assistant()
    assistant.start()

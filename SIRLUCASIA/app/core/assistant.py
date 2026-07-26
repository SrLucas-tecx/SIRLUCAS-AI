import random

from app.core.intent_manager import IntentManager
from app.core.memory_manager import MemoryManager
from app.core.command_manager import CommandManager
from app.modules.parser import Parser
from app.core.context_manager import ContextManager
from app.core.history_manager import HistoryManager
from app.core.knowledge_manager import KnowledgeManager
from app.core.web_manager import WebManager
from app.core.calculator_manager import CalculatorManager
from app.service.system_manager import SystemManager
from app.service.document_manager import DocumentManager
from app.core.router import Router
from app.core.task_pipeline import TaskPipeline
from app.core.response_formatter import ResponseFormatter   # 👈 nuevo


class Assistant:

    def __init__(self):
        self.name = "SIRLUCAS AI"
        self.version = "0.1"
        self.debug = True

        # Managers principales
        self.intent_manager = IntentManager()
        self.memory = MemoryManager()
        self.command_manager = CommandManager(self.memory)
        self.context = ContextManager()
        self.history = HistoryManager()
        self.knowledge = KnowledgeManager()
        self.web = WebManager()
        self.system = SystemManager()
        self.document = DocumentManager()
        self.calculator = CalculatorManager()

        # Router
        self.router = Router()
        self.router.register("memory", self.memory)
        self.router.register("knowledge", self.knowledge)
        self.router.register("web", self.web)
        self.router.register("system", self.system)
        self.router.register("document", self.document)
        self.router.register("calculator", self.calculator)
        self.router.register("history", self.history)

        # Pipeline y Formatter
        self.pipeline = TaskPipeline(
            entity_resolver=None,
            reference_resolver=None,
            context_resolver=None,
            context_manager=self.context,
            intent_resolver=None,
            planner=None,
            optimizer=None,
            executor=self.router   # 👈 el Router actúa como executor
        )
        self.response_formatter = ResponseFormatter()

        # Parser
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
        print("=" * 60)

    def chat(self):
        while True:
            raw_message = input("\nTú > ")

            if raw_message.lower() in ["salir", "exit", "quit"]:
                self.stop()
                break

            # Parser → Pipeline → Formatter
            message = self.parser.parse(raw_message, self.context)
            result = self.pipeline.execute(message)
            response = self.response_formatter.format(result)

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
